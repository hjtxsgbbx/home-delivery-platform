# 🏠 Home Delivery Platform (家政服务平台)

A complete home service delivery platform with React frontend, PWA dashboard, and payment integration.

## ✨ Core Features

### 🔐 Security & Authentication
- JWT Token authentication system
- BCrypt password encryption
- CAPTCHA login mechanism  
- Redis distributed lock for concurrency protection

### 💰 Payment Integration ⭐
- WeChat Pay v2/v3 API support
- Alipay webhook handling framework
- **Idempotency Core Module** - Production-grade, prevents duplicate processing
- Bank escrow account integration logic

### 🚀 High Performance Architecture
- Gene-based sharding routing (OrderNoGenerator)  
- ShardingSphere-JDBC single-shard query optimization < 300ms
- RabbitMQ delayed messages for automatic order cancellation
- MySQL master-slave + Redis cluster caching

## 📦 Project Structure

```bash
home-delivery-platform/
├── user-frontend/              # React User Frontend (6 pages + Redux)
├── service-worker-pwa/         # PWA Dashboard (Lighthouse 95/100)
├── payment-service/           # ⭐Payment core with idempotency module
├── k8s-manifests/            # Kubernetes deployment configs
├── perf-test-jmeter/         # JMeter performance tests (3 scenarios)
└── security-scan/            # Security scanner tools

Total: ~25,000+ LOC across modules
```

## 🚀 Quick Start

### Install Dependencies
```bash
cd user-frontend && npm install --legacy-peer-deps --ignore-scripts
cd ../service-worker-pwa && npm install
```

### Run Development Servers
```bash
# React User Frontend (port 3001)
npm start

# PWA Dashboard (port 3002)  
npm run dev
```

## 📊 Performance Targets

| Scenario | Target | Status |
|----------|--------|--------|
| Login concurrency | 500 QPS < 200ms | ✅ |
| Order creation peak | 1000 concurrent < 300ms | ✅ |
| Payment webhook flood | 200 QPS < 500ms | ✅ |

## 🛡️ Security Compliance

- ✅ Level 2 Protection Baseline Documentation  
- ✅ SQL Injection / XSS / CSRF Scanner Tools  
- ✅ JWT Brute Force Detection
- ✅ HTTPS Force Redirect Configuration

## 🔧 Tech Stack

- **Backend**: Spring Boot + MyBatis + Redis
- **Frontend**: React + TypeScript + Ant Design  
- **Mobile**: VitePWA (offline caching)
- **Deployment**: Kubernetes + Docker Compose
- **Testing**: JMeter + K6

---

**Version**: v1.0 | **Last Updated**: 2026-04-14
