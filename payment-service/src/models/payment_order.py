"""
支付订单模型
"""
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any
import json


class PaymentStatus(Enum):
    """订单状态枚举"""
    PENDING = "pending"           # 待支付
    PROCESSING = "processing"     # 处理中（回调已接收）
    PAID = "paid"                # 已支付
    FAILED = "failed"            # 支付失败
    EXPIRED = "expired"          # 已过期
    CANCELLED = "cancelled"      # 已取消


class PaymentType(Enum):
    """支付方式枚举"""
    WECHAT_PAY = "wechat_pay"    # 微信支付
    ALIPAY = "alipay"            # 支付宝


class Currency(Enum):
    """货币类型"""
    CNY = "CNY"
    USD = "USD"


class PaymentOrder:
    """支付订单模型"""
    
    def __init__(self, order_id: str, payment_type: PaymentType, 
                 amount: float, currency: Currency, user_id: str):
        self.order_id = order_id
        self.payment_type = payment_type
        self.amount = amount
        self.currency = currency
        self.user_id = user_id
        
        # 支付相关字段
        self.pay_request_no = ""     # 第三方支付请求号
        self.transaction_id = ""     # 第三方交易号（微信）/ orderNo (支付宝)
        self.out_trade_no = order_id  # 商户订单号
        
        # 状态
        self.status = PaymentStatus.PENDING
        self.callback_status = None  # 'pending', 'success', 'failed'
        
        # 时间
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        self.paid_at = None
        self.expired_at = None
        
        # 回调信息
        self.callback_data: Dict[str, Any] = {}
        self.retry_count = 0
        self.max_retries = 3
        self.last_callback_time = None
        
        # 存管账户字段
        self.custodian_account_id = ""
        self.custodian_status = "pending"  # 'pending', 'synced', 'error'
        
        # Redis 幂等性 key（用于缓存）
        self._idempotency_key: Optional[str] = None
    
    @property
    def amount_str(self) -> str:
        """格式化金额字符串"""
        return f"{self.amount:.2f}"
    
    @property
    def is_expired(self) -> bool:
        """检查订单是否过期"""
        if not self.expired_at:
            # 默认 30 分钟后过期
            self.expired_at = self.created_at.timestamp() + 1800
        
        return datetime.utcnow().timestamp() > self.expired_at
    
    def generate_idempotency_key(self) -> str:
        """生成幂等性 key"""
        from utils.idempotency import IdempotencyManager
        
        if not self._idempotency_key:
            manager = IdempotencyManager()
            
            kwargs = {}
            if self.payment_type == PaymentType.WECHAT_PAY:
                kwargs['out_trade_no'] = self.out_trade_no
                # transaction_id 在回调时设置
            elif self.payment_type == PaymentType.ALIPAY:
                kwargs['trade_no'] = ""
            
            self._idempotency_key = manager.generate_key(
                self.payment_type.value, **kwargs
            )
        
        return self._idempotency_key
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        result = {
            'order_id': self.order_id,
            'payment_type': self.payment_type.value,
            'amount': self.amount,
            'currency': self.currency.value,
            'user_id': self.user_id,
            'out_trade_no': self.out_trade_no,
            'transaction_id': self.transaction_id,
            'pay_request_no': self.pay_request_no,
            'status': self.status.value,
            'callback_status': self.callback_status,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'paid_at': self.paid_at.isoformat() if self.paid_at else None,
            'expired_at': self.expired_at.isoformat() if self.expired_at else None,
            'retry_count': self.retry_count,
            'custodian_account_id': self.custodian_account_id,
        }
        
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PaymentOrder':
        """从字典创建实例"""
        order = cls(
            order_id=data['order_id'],
            payment_type=PaymentType(data['payment_type']),
            amount=float(data['amount']),
            currency=Currency(data['currency']),
            user_id=data['user_id']
        )
        
        # 恢复状态字段
        if data.get('status'):
            try:
                order.status = PaymentStatus(data['status'])
            except ValueError:
                pass
        
        if 'paid_at' in data and data['paid_at']:
            order.paid_at = datetime.fromisoformat(data['paid_at'])
        
        return order
    
    def __repr__(self):
        return f"PaymentOrder({self.order_id}, {self.payment_type.value}, ¥{self.amount})"


class OrderRepository:
    """订单数据仓库（实际应用中应使用数据库 ORM）"""
    
    def __init__(self, db_url: str = None):
        # TODO: 集成 SQLAlchemy/Database
        self.db_url = db_url or "sqlite:///payment.db"
    
    def create(self, order: PaymentOrder) -> bool:
        """创建订单"""
        # 实际实现：使用数据库 INSERT 语句，包含唯一索引检查
        print(f"[DB] Creating order: {order.order_id}")
        
        # 生成幂等性 key 并设置缓存过期时间
        idempotency_key = order.generate_idempotency_key()
        order._idempotency_key = idempotency_key
        
        return True
    
    def get_by_order_id(self, order_id: str) -> Optional[PaymentOrder]:
        """根据订单 ID 获取"""
        print(f"[DB] Getting order by ID: {order_id}")
        
        # TODO: 实现数据库查询
        return None
    
    def update_status(self, order_id: str, status: PaymentStatus, callback_data: Dict = None) -> bool:
        """更新订单状态"""
        print(f"[DB] Updating status for {order_id}: {status.value}")
        
        # TODO: 实现数据库更新，包含唯一索引检查防止重复插入
        return True
    
    def check_unique(self, out_trade_no: str, transaction_id: str = None) -> bool:
        """检查订单号是否已存在"""
        print(f"[DB] Checking unique for {out_trade_no}")
        
        # TODO: 实现唯一性检查
        return False
