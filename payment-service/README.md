# Payment Service

支付服务集成微信支付和支付宝，支持创建订单、处理回调、幂等性保证。

## 功能特性

- ✅ 微信支付接口集成
- ✅ 支付宝接口集成
- ✅ 创建支付订单
- ✅ 微信/支付宝回调处理（幂等性）
- ✅ Redis 分布式锁防止并发问题
- ✅ 存管账户对接逻辑
- ✅ 查询支付状态

## 项目结构

```
payment-service/
├── src/
│   ├── config/
│   │   └── settings.py          # 配置管理
│   ├── models/
│   │   └── payment_order.py     # 订单模型
│   ├── services/
│   │   ├── __init__.py
│   │   ├── base_service.py      # 基础服务类
│   │   ├── wechat_service.py    # 微信支付服务
│   │   └── alipay_service.py    # 支付宝服务
│   ├── utils/
│   │   ├── redis_lock.py        # Redis 分布式锁工具
│   │   ├── idempotency.py       # 幂等性处理
│   │   └── crypto_utils.py      # 加密解密工具
│   └── app.py                   # Flask 应用入口
├── tests/                       # 测试文件
├── requirements.txt            # Python 依赖
├── pyproject.toml              # 项目配置
└── README.md                   # 说明文档
```

## 快速开始

1. 安装依赖：
```bash
pip install -e ".[dev]"
```

2. 配置环境变量（`.env`）：
```env
# Redis 配置
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# 微信支付配置
WECHAT_APPID=wx_appid_here
WECHAT_MCHID=mch_id_here
WECHAT_API_KEY=wechat_api_key
WECHAT_CERT_PATH=/path/to/cert.pem

# 支付宝配置
ALIAPPID=alipay_appid
ALIPUBKEY=alipay_public_key
ALIPRIVATEKEY=ali_private_key
```

3. 启动服务：
```bash
python src/app.py
```

## API 文档

### 创建支付订单

```http
POST /api/v1/payments/create
Content-Type: application/json

{
    "order_id": "ORD20240101001",
    "amount": 100.00,
    "currency": "CNY",
    "callback_url": "https://your-domain.com/callback"
}
```

### 处理回调（自动触发）

- 微信支付：`/api/v1/payments/wechat/callback`
- 支付宝：`/api/v1/payments/alipay/callback`

### 查询订单状态

```http
GET /api/v1/payments/{order_id}
Authorization: Bearer <token>
```

## 安全特性

- **幂等性保证**：通过 Redis + 数据库唯一索引防止重复处理回调
- **分布式锁**：使用 Redis SETNX 实现分布式锁，防止并发问题
- **签名验证**：所有回调请求都会进行签名验证
- **加密传输**：敏感数据使用 AES/RSA 加密
