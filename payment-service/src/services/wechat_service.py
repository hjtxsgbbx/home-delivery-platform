"""
微信支付服务集成
支持 v2 和 v3 接口，重点实现回调处理和幂等性保护
"""
import requests
from typing import Dict, Any, Optional
from datetime import datetime
import hmac
import hashlib
import time
import base64
import os

try:
    from wechatpay import api, v3
except ImportError:
    # 使用纯 Python 实现，不依赖微信官方 SDK
    pass

from models.payment_order import PaymentOrder, PaymentStatus, Currency
from utils.redis_lock import RedisDistributedLock


class WeChatPayService:
    """微信支付服务"""
    
    def __init__(self):
        config = {
            'appid': os.getenv('WECHAT_APPID'),
            'mchid': os.getenv('WECHAT_MCHID'),
            'api_v3_key': os.getenv('WECHAT_API_V3_SECRET'),
            'cert_path': os.getenv('WECHAT_CERT_PATH', '/path/to/apiclient_cert.pem')
        }
        
        self.appid = config['appid']
        self.mchid = config['mchid']
        self.api_v3_key = config['api_v3_key']
        self.cert_path = config['cert_path']
    
    def create_order(self, order: PaymentOrder) -> Optional[Dict[str, Any]]:
        """
        创建微信支付订单
        
        Args:
            order: 支付订单
            
        Returns:
            预支付交易结果，包含 prepay_id
        """
        # TODO: 实现微信 v3 接口调用
        print(f"[WeChat] Creating payment for order {order.order_id}")
        
        return {
            'out_trade_no': order.out_trade_no,
            'transaction_id': '',  # 创建后由支付回调返回
            'prepay_id': ''  # TODO: 实际调用微信 API 获取
        }
    
    def get_payment_url(self, order: PaymentOrder) -> str:
        """
        生成微信支付 URL（H5/JSAPI）
        
        Args:
            order: 支付订单
            
        Returns:
            支付 URL
        """
        # TODO: 实现
        return f"https://pay.weixin.qq.com/pay?order_id={order.order_id}"
    
    def verify_signature(self, body: str, signature: str) -> bool:
        """
        验证微信 v3 签名
        
        Args:
            body: JSON body（不包含签名字段）
            signature: 签名
            
        Returns:
            True 如果签名有效
        """
        # 对 body 进行 HMAC-SHA256 加密
        h = hmac.new(
            self.api_v3_key.encode('utf-8'),
            body.encode('utf-8'),
            hashlib.sha256
        )
        
        expected_signature = base64.b64encode(h.digest()).decode('utf-8')
        
        return signature == expected_signature
    
    def verify_notification(self, request_body: str) -> Dict[str, Any]:
        """
        验证微信回调请求
        
        Args:
            request_body: 原始请求体（包含签名）
            
        Returns:
            {'success': True/False, 'data': {...}, 'error': error_msg}
        """
        # TODO: 实现 v3 接口回调验证
        print("[WeChat] Verifying notification signature")
        
        return {
            'success': False,  # TODO: 实际验证后返回结果
            'data': {},
            'error': 'Not implemented'
        }


class WeChatCallbackHandler:
    """微信支付回调处理器（重点实现幂等性）"""
    
    def __init__(self):
        self.order_repo = None
        self.lock_manager = RedisDistributedLock(prefix='wechat_callback')
    
    def handle(self, request_body: str) -> Dict[str, Any]:
        """
        处理微信支付回调
        
        Args:
            request_body: 回调请求体
            
        Returns:
            {'success': bool, 'error': error_msg}
        """
        print(f"[WeChat Callback] Received notification")
        
        # TODO: 
        # 1. 验证签名
        # 2. 解析回调数据
        # 3. 使用分布式锁处理幂等性
        # 4. 更新订单状态
        # 5. 对接存管账户
        
        return {
            'success': False,
            'error': 'Not implemented'
        }


def parse_wechat_callback_body(body: str) -> Dict[str, Any]:
    """解析微信回调 body"""
    try:
        import json
        data = json.loads(body)
        
        # 微信 v3 接口格式不同，这里兼容两种格式
        if 'resource' in data:
            # v2 接口格式
            return {
                'out_trade_no': data.get('out_trade_no', ''),
                'transaction_id': data.get('transaction_id', '') or data.get('transaction_id', ''),
                'trade_state': data.get('trade_state', ''),
                'amount': data.get('total_fee', 0) / 100,  # v2 金额单位是分
                'success_time': datetime.fromtimestamp(data.get('time_end', 0)) if data.get('time_end') else None,
            }
        elif 'encrypted_data' in data:
            # v3 接口格式（加密传输）
            return {
                'out_trade_no': '',  # TODO: 解密获取
                'transaction_id': '',  # TODO: 解密获取
                'trade_state': '',  # TODO: 解密获取
                'amount': 0,  # TODO: 解密获取
            }
        
        return {}
    
    except Exception as e:
        print(f"[WeChat] Failed to parse callback body: {e}")
        return {}
