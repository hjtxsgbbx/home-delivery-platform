"""
支付服务配置管理
"""
import os
from functools import lru_cache


@lru_cache()
def get_settings():
    """获取配置项，使用 LRU 缓存避免重复读取环境变量"""
    
    # Redis 配置
    REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
    REDIS_DB = int(os.getenv('REDIS_DB', 0))
    REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', '')
    REDIS_PREFIX = os.getenv('REDIS_PREFIX', 'payment:')
    
    # Flask 配置
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    DEBUG = os.getenv('DEBUG', 'false').lower() == 'true'
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # 微信支付配置
    WECHAT_APPID = os.getenv('WECHAT_APPID', '')
    WECHAT_MCHID = os.getenv('WECHAT_MCHID', '')
    WECHAT_API_V3_SECRET = os.getenv('WECHAT_API_V3_SECRET', '')
    WECHAT_CERT_PATH = os.getenv('WECHAT_CERT_PATH', '/path/to/apiclient_cert.pem')
    
    # 支付宝配置
    ALIPAY_APPID = os.getenv('ALIPAY_APPID', '')
    ALIPAY_PUBLIC_KEY_PATH = os.getenv('ALIPAY_PUBLIC_KEY_PATH', '/path/to/alipay_public_key.pem')
    ALIPAY_PRIVATE_KEY_PATH = os.getenv('ALIPAY_PRIVATE_KEY_PATH', '/path/to/private_key.pem')
    
    # 数据库配置
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///payment.db')
    
    return {
        'redis': {
            'host': REDIS_HOST,
            'port': REDIS_PORT,
            'db': REDIS_DB,
            'password': REDIS_PASSWORD,
            'prefix': REDIS_PREFIX,
        },
        'flask': {
            'env': FLASK_ENV,
            'debug': DEBUG,
            'secret_key': SECRET_KEY,
        },
        'wechat': {
            'appid': WECHAT_APPID,
            'mchid': WECHAT_MCHID,
            'api_v3_secret': WECHAT_API_V3_SECRET,
            'cert_path': WECHAT_CERT_PATH,
        },
        'alipay': {
            'app_id': ALIPAY_APPID,
            'public_key_path': ALIPAY_PUBLIC_KEY_PATH,
            'private_key_path': ALIPAY_PRIVATE_KEY_PATH,
        },
        'database': {
            'url': DATABASE_URL,
        }
    }


def get_redis_config():
    """获取 Redis 配置"""
    return get_settings()['redis']


def get_wechat_config():
    """获取微信支付配置"""
    return get_settings()['wechat']


def get_alipay_config():
    """获取支付宝配置"""
    return get_settings()['alipay']
