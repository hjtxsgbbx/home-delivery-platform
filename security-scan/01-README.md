# 安全渗透测试套件 (Security Penetration Testing Suite)

## 📋 概述

本目录包含完整的 Web 应用安全扫描脚本，涵盖 OWASP Top 10 主要漏洞类型：
- SQL 注入检测 (SQL Injection)
- XSS 攻击检测 (Cross-Site Scripting)
- CSRF 防护验证 (Cross-Site Request Forgery)
- JWT 暴力破解测试 (JWT Brute Force)
- 敏感数据泄露检查 (Sensitive Data Exposure)

## 🛠️ 工具依赖

```bash
# Python 库安装
pip install -r requirements.txt

# 可选：OWASP ZAP / BurpSuite CLI
# 推荐使用 Python 模拟攻击，无需额外 GUI 工具
```

## 🚀 快速开始

### 1. SQL 注入扫描
```bash
python3 scripts/sql_injection_scan.py --target-url http://localhost:8000 \
    --test-cases basic,advanced,bypass
```

### 2. XSS 攻击检测
```bash
python3 scripts/xss_scan.py --target-url http://localhost:8000 \
    --scan-page login,search,profile,detail
```

### 3. CSRF 防护验证
```bash
python3 scripts/csrf_validation.py --target-url http://localhost:8000 \
    --test-actions form-post,ajax-request,file-upload
```

### 4. JWT 暴力破解测试
```bash
python3 scripts/jwt_bruteforce.py --jwt-secret "your-secret-key" \
    --token-pattern "{id},{salt}" --concurrent-threads 10
```

### 5. 敏感数据检查
```bash
python3 scripts/sensitive_data_check.py --target-url http://localhost:8000 \
    --check-types email,phone,id-card,bank-info,passwords
```

## 📊 报告输出

所有扫描结果将自动保存到 `reports/` 目录：
- `{test_name}_report.json` - 原始 JSON 数据
- `{test_name}_report.html` - HTML 可视化报告
- `summary_report.md` - Markdown 格式总结报告

## ⚠️ 使用警告

**重要提示：**
1. **仅在授权的测试环境中运行**，生产环境使用前必须获得书面授权
2. 所有扫描脚本均包含防误伤机制，会检查是否已存在防护
3. JWT 暴力破解测试需要设置合理的并发限制，避免造成拒绝服务

## 📁 脚本清单

| 文件名 | 功能描述 | 严重等级 |
|--------|---------|----------|
| `sql_injection_scan.py` | SQL 注入全维度扫描 | 🔴 Critical |
| `xss_scan.py` | XSS 漏洞检测 | 🔴 Critical |
| `csrf_validation.py` | CSRF 防护有效性验证 | 🟠 High |
| `jwt_bruteforce.py` | JWT Token 暴力破解测试 | 🔴 Critical |
| `sensitive_data_check.py` | 敏感数据泄露检查 | 🟡 Medium |
| `run_all_scans.sh` | 一键运行所有扫描脚本 | - |

## 📖 参考标准

- OWASP Top 10 2023
- CWE/SANS Top 25 Worst Programming Errors
- PCI DSS 4.0 Compliance Requirements
