from datetime import datetime
import secrets
import re
import json
from urllib.parse import urlparse
from flask import Response as ResponseFlaskBase, request

def generate_token():
    """生成随机36位密码（字母和数字）"""
    alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    return ''.join(secrets.choice(alphabet) for _ in range(36))

def get_cors_headers(app_config):
    """根据请求来源生成CORS头部，检查白名单"""
    origin = request.headers.get('Origin', '')

    if not origin:
        return {}  # 非CORS请求不返回跨域头
    
    # 提取来源的host部分（不含协议和端口）
    try:
        origin_host = urlparse(origin).hostname
        if not origin_host:
            return {}  # Origin 无法解析的
        if not any(
            origin_host.endswith(domain)
            for domain in app_config['ACCESS_ORIGINS']
        ):
            return {}  # Origin 不在白名单中
    except:
        return {}  # Origin 无法解析的

    return  {
        'Access-Control-Allow-Origin': origin,
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization',
        'Access-Control-Allow-Credentials': 'true',
        'Vary': 'Origin'
    }

def process_set_cookie(cookie_header, target_domain, forwarded_proto, proxy_path):
    """
    处理Set-Cookie字段，使其储存到代理
    """
    new_cookie_headers = []
    for cookie in cookie_header.split(','):
        fields = list(map(lambda x: x.strip(), cookie.split(';')))
        new_fields = []
        has_path_field = False
        for field in fields:
            if '=' in field:  # 键值对字段
                key, value = field.split('=', 1)
                key_lower = key.strip().lower()
                if key_lower == 'domain':
                    continue
                if key_lower == 'path':
                    value = f"/{proxy_path}/{target_domain}{value}"
                    has_path_field = True
                if key_lower == 'samesite':
                    value = 'Lax'

                new_fields.append(f"{key}={value}")
            else:  # 无值字段直接加
                if not forwarded_proto=='https' and field.strip().lower() == 'secure':
                    continue
                new_fields.append(field)
        if not has_path_field:
            new_fields.append(f"Path=/{proxy_path}/{target_domain}")
        new_cookie_headers.append('; '.join(new_fields).strip())
    
    return new_cookie_headers

def proxy_to(host, url, forwarded_proto, proxy_path):
    """
    URL转换函数，将目标URL转换为代理URL格式
    示例: https://e.cn/path -> https://proxy.cn/e.cn/path
    """
    if not url:
        return ''
    
    parsed = urlparse(url)
    proxy_path = f"{forwarded_proto}://{host}/{proxy_path}/{parsed.netloc}{parsed.path if parsed.path else ''}"
    if parsed.query:
        proxy_path += f"?{parsed.query}"
    if parsed.fragment:
        proxy_path += f"#{parsed.fragment}"
    
    return proxy_path

def get_error_html(host, proxy_path):
    return f"""
<!DOCTYPE html><html><head><title>代理服务运行中</title></head><body style="font-famil
y:Arial,sans-serif;text-align:center;margin-top:50px;color:#333;"><div style="max-widt
h:600px;margin:0 auto;"><h1 style="color:#d9534f;">代理服务运行中</h1><p>当前代理地址：
{host}/{proxy_path}/</p><p>如果您在调试时看到本页面，说明您可能触发了域名限制或并

发限制</p></div></body></html>
"""

class ResponseJson(ResponseFlaskBase):
    def __init__(self, data, status, mimetype='application/json', **kwargs):
        super().__init__(json.dumps(data), status=status, mimetype=mimetype, **kwargs)

def has_all_keys(data, keys):
    """检查data是否包含所有keys"""
    return all(key in data and data[key] for key in keys)

def is_valid_date(date_str: str) -> bool:
    """验证日期字符串是否为YYYY-MM-DD格式"""
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False
