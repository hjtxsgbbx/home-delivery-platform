"""
幂等性处理模块

通过 Redis + 数据库唯一索引保证回调处理的幂等性
"""
import redis
from typing import Optional, Dict, Any
from datetime import datetime
from config.settings import get_redis_config


class IdempotencyManager:
    """
    幂等性管理器
    
    核心思想：
    1. Redis 作为快速检查层，存储已处理的回调 key
    2. 数据库作为持久化层，使用唯一索引防止重复插入
    3. 先检查 Redis（快速失败），再写入数据库（最终保护）
    
    幂等性 key 生成规则：
    - 微信支付：WECHAT_{out_trade_no}_{transaction_id}
    - 支付宝：ALI_{trade_no}_{notify_type}
    """
    
    # 缓存过期时间（秒）
    REDIS_TTL = 3600  # 1 小时
    
    def __init__(self, prefix='payment:idempotency'):
        self._redis = None
        self.prefix = prefix
    
    def _get_redis_client(self):
        """获取 Redis 客户端"""
        if self._redis is None:
            config = get_redis_config()
            self._redis = redis.Redis(
                host=config['host'],
                port=config['port'],
                db=config['db'],
                password=config.get('password', ''),
                decode_responses=True,
                socket_connect_timeout=10
            )
        return self._redis
    
    def generate_key(self, payment_type: str, **kwargs) -> str:
        """
        生成幂等性 key
        
        Args:
            payment_type: 'wechat' or 'alipay'
            **kwargs: 额外参数，用于生成 key
            
        Returns:
            幂等性 key
        """
        if payment_type == 'wechat':
            # WECHAT_{out_trade_no}_{transaction_id}
            out_trade_no = kwargs.get('out_trade_no', '')[:32] or str(time.time())[:10]
            transaction_id = kwargs.get('transaction_id', '')[:64] or ''
            return f"{self.prefix}:wechat:{out_trade_no}:{transaction_id}"
            
        elif payment_type == 'alipay':
            # ALI_{trade_no}_{notify_type}
            trade_no = kwargs.get('trade_no', '')[:32] or str(time.time())[:10]
            notify_type = kwargs.get('notify_type', 'unknown')
            return f"{self.prefix}:alipay:{trade_no}:{notify_type}"
            
        else:
            raise ValueError(f"Unknown payment type: {payment_type}")
    
    def is_processed(self, key: str) -> bool:
        """
        检查回调是否已经处理过
        
        Args:
            key: 幂等性 key
            
        Returns:
            True 如果已处理，False 否则
        """
        try:
            exists = self._redis_client.exists(key)
            return bool(exists)
        except Exception as e:
            # Redis 故障时返回 False，允许尝试写入数据库进行最终保护
            print(f"Redis check failed: {e}")
            return False
    
    def mark_as_processed(self, key: str, data: Dict[str, Any]) -> bool:
        """
        标记为已处理
        
        Args:
            key: 幂等性 key
            data: 回调数据
            
        Returns:
            True 如果成功，False 否则（包括 Redis 故障）
        """
        try:
            # 先设置到 Redis
            self._redis_client.setex(
                key,
                self.REDIS_TTL,
                str({
                    'status': data.get('status', 'pending'),
                    'processed_at': datetime.utcnow().isoformat(),
                    'data_hash': hash(str(data))
                })
            )
            
            # 注意：这里不直接写入数据库，数据库的唯一索引检查在应用层进行
            return True
            
        except Exception as e:
            print(f"Failed to mark as processed: {e}")
            # Redis 故障时记录到日志，由应用层做最终保护
            self._log_failure(key, str(e))
            return False
    
    def _redis_client(self):
        """获取 Redis 客户端"""
        if not hasattr(self, '_client'):
            config = get_redis_config()
            self._client = redis.Redis(
                host=config['host'],
                port=config['port'],
                db=config['db'],
                password=config.get('password', ''),
                decode_responses=True,
                socket_timeout=5
            )
        return self._client
    
    def _log_failure(self, key: str, error: str):
        """记录失败日志（实际应用中应使用日志系统）"""
        # TODO: 集成到应用日志系统
        print(f"[Idempotency Error] Key: {key}, Error: {error}")


def check_and_lock(idempotency_key: str, lock_timeout: int = 30) -> Optional[Dict]:
    """
    检查并加锁
    
    Args:
        idempotency_key: 幂等性 key
        lock_timeout: 锁超时时间（秒）
        
    Returns:
        如果成功获取锁，返回缓存数据；否则返回 None
    """
    import time as time_module
    
    try:
        redis_client = IdempotencyManager()._redis_client()
        
        # 尝试获取分布式锁
        lock_key = f"{idempotency_key}:lock"
        acquired = RedisDistributedLock().acquire(lock_key)
        
        if not acquired:
            return None
        
        try:
            # 检查是否已处理
            exists = redis_client.exists(idempotency_key)
            
            if exists:
                cached_data = redis_client.get(idempotency_key)
                import json
                data = json.loads(cached_data)
                
                # 验证状态，只允许从 pending -> processing/processing_failed/success
                current_status = data['status']
                if current_status in ['processing', 'success']:
                    return None  # 正在处理或已完成
                
                return {
                    'cached': True,
                    **data,
                    'lock_until': time_module.time() + lock_timeout
                }
            
            else:
                # 创建新记录
                return {
                    'cached': False,
                    'status': 'processing',
                    'processed_at': None,
                    'lock_until': time_module.time() + lock_timeout
                }
                
        finally:
            RedisDistributedLock().release(lock_key)
            
    except Exception as e:
        print(f"Error in check_and_lock: {e}")
        return None


def release_lock(idempotency_key: str):
    """释放锁"""
    lock_key = f"{idempotency_key}:lock"
    RedisDistributedLock().release(lock_key)
