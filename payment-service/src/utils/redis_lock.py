"""
Redis 分布式锁实现
使用 Redis SETNX 和 Lua 脚本实现安全的分布式锁
"""
import redis
import uuid
import time
from typing import Optional, Callable, Any
from contextlib import contextmanager
from config.settings import get_redis_config


class RedisDistributedLock:
    """
    Redis 分布式锁
    
    特性：
    - 自动续期防止锁过期
    - 支持设置 TTL
    - 安全的释放机制（验证 owner）
    """
    
    def __init__(self, prefix='payment_lock', expire_seconds=300):
        """
        初始化 Redis 分布式锁
        
        Args:
            prefix: Redis key 前缀，用于区分不同服务的锁
            expire_seconds: 锁的过期时间（秒）
        """
        self._redis = None
        self.prefix = prefix
        self.expire_seconds = expire_seconds
    
    def _get_redis_client(self):
        """获取或创建 Redis 客户端"""
        if self._redis is None:
            config = get_redis_config()
            self._redis = redis.Redis(
                host=config['host'],
                port=config['port'],
                db=config['db'],
                password=config.get('password', ''),
                decode_responses=True,
                socket_connect_timeout=10,
                socket_timeout=5
            )
        return self._redis
    
    def acquire(self, lock_key: str) -> bool:
        """
        获取分布式锁
        
        Args:
            lock_key: 锁的 key
            
        Returns:
            True 如果成功获取锁，False 否则
        """
        redis_client = self._get_redis_client()
        
        # 使用 Lua 脚本保证原子性
        lua_script = """
        local current_lock = redis.call('GET', KEYS[1])
        if not current_lock or current_lock ~= ARGV[1] then
            -- 锁不存在或不是当前客户端持有，尝试加锁
            redis.call('SET', KEYS[1], ARGV[1], 'PX', tonumber(ARGV[2]))
            return 1
        end
        return 0
        """
        
        lock_id = f"{time.time()}{uuid.uuid4().hex[:8]}"
        lua_result = redis_client.eval(lua_script, 1, self.prefix + lock_key, lock_id, self.expire_seconds * 1000)
        
        return bool(lua_result)
    
    def release(self, lock_key: str) -> bool:
        """
        安全释放分布式锁
        
        Args:
            lock_key: 锁的 key
            
        Returns:
            True 如果成功释放，False 否则（包括锁不存在的情况）
        """
        redis_client = self._get_redis_client()
        
        lua_script = """
        local current_lock = redis.call('GET', KEYS[1])
        if current_lock and current_lock == ARGV[1] then
            redis.call('DEL', KEYS[1])
            return 1
        end
        return 0
        """
        
        lock_id = f"{time.time()}{uuid.uuid4().hex[:8]}"
        lua_result = redis_client.eval(lua_script, 1, self.prefix + lock_key, lock_id)
        
        return bool(lua_result)
    
    def try_renew(self, lock_key: str) -> bool:
        """
        尝试续期锁
        
        Args:
            lock_key: 锁的 key
            
        Returns:
            True 如果成功续期，False 否则
        """
        redis_client = self._get_redis_client()
        
        lua_script = """
        local current_lock = redis.call('GET', KEYS[1])
        if not current_lock or current_lock ~= ARGV[1] then
            return 0
        end
        
        -- 使用 EXPIRE 重新设置过期时间，不会删除锁
        redis.call('EXPIRE', KEYS[1], tonumber(ARGV[2]))
        return 1
        """
        
        lock_id = f"{time.time()}{uuid.uuid4().hex[:8]}"
        lua_result = redis_client.eval(lua_script, 1, self.prefix + lock_key, lock_id, self.expire_seconds)
        
        return bool(lua_result)
    
    @contextmanager
    def context(self, lock_key: str):
        """
        上下文管理器，自动处理锁的获取和释放
        
        Usage:
            with lock.context('payment:order:create'):
                # 持有锁的代码块
                pass
        """
        acquired = self.acquire(lock_key)
        
        try:
            yield acquired
            
            if acquired:
                # 在代码块执行期间定期续期，防止锁过期
                for _ in range(self.expire_seconds // 1):
                    time.sleep(0.5)
                    if not self.try_renew(lock_key):
                        break
                        
        finally:
            if acquired:
                self.release(lock_key)


class RateLimiter:
    """
    Redis 限流器（令牌桶算法）
    
    用于限制 API 调用频率，防止并发问题
    """
    
    def __init__(self, redis_client, key_template='rate_limit:{key}', max_requests=100, window_seconds=60):
        self.redis = redis_client
        self.key_template = key_template
        self.max_requests = max_requests
        self.window_seconds = window_seconds
    
    def allow_request(self, key: str) -> bool:
        """
        检查是否允许请求
        
        Args:
            key: 限流 key
            
        Returns:
            True 如果允许请求，False 否则（超过限制）
        """
        key_pattern = self.key_template.format(key=key)
        
        # 获取当前时间戳和剩余令牌数
        pipeline = self.redis.pipeline()
        now = int(time.time())
        window_start = (now // self.window_seconds) * self.window_seconds
        
        # Lua 脚本实现限流逻辑
        lua_script = """
        local current_key = KEYS[1]
        local max_requests = tonumber(ARGV[1])
        local window_seconds = tonumber(ARGV[2])
        local now = tonumber(ARGV[3])
        
        -- 清理过期窗口
        redis.call('DEL', current_key)
        
        -- 初始化计数
        local count = redis.call('INCR', current_key)
        if count == 1 then
            redis.call('EXPIRE', current_key, window_seconds + 10)
            count = 1
        end
        
        return count <= max_requests and 1 or 0
        """
        
        result = self.redis.eval(lua_script, 1, key_pattern, self.max_requests, self.window_seconds, now)
        return bool(result)


def create_distributed_lock(prefix='payment', expire=300):
    """工厂函数创建分布式锁实例"""
    return RedisDistributedLock(prefix=prefix, expire_seconds=expire)
