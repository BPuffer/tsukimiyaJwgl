import os
from flask import Flask, request, Response, make_response
import requests
from urllib.parse import urlparse, urljoin
import urllib3
urllib3.disable_warnings()
import re
import json
from dotenv import load_dotenv
load_dotenv()
import redis

# 环境配置
# 代理域名，用于处理重定向问题，作用于3XX Location字段的URL转换
# 如proxy.tsukimiya.site
PROXY_URL = '[DEPRECATED]env.PROXY_URL'
# 前端域名，用于处理跨域问题，作用于响应头中跨域目标字段
# 如www.tsukimiya.site
FRONTEND_ORIGIN = '[DEPRECATED]env.FRONTEND_ORIGIN'
# 前端域名白名单，用于处理跨域问题，处于这些白名单中的Origin予以通过
ACCESS_ORIGINS_str = os.environ.get("ACCESS_ORIGINS", '192.168.43.88;localhost;yku.tsukimiya.site;82.156.135.94')
ACCESS_ORIGINS = list(map(str.strip, ACCESS_ORIGINS_str.split(';')))

# 端口号。本地服务开放时使用的端口号。默认5000
PORT = int(os.getenv('PORT', 20081))
# 是否允许HTTPS连接，如果否，拦截转发Cookie中的Secure字段，
SSL_VERIFY = os.getenv('SSL_VERIFY', 'False').lower() == 'true'
# 转发时是否验证SSL证书
SSL_VERIFY_TARGET = os.getenv('SSL_VERIFY_TARGET', str(SSL_VERIFY)).lower() == 'true'


# Redis配置
REDIS_HOST = 'localhost'  # IP限制用Redis，可以固定在本地
REDIS_PORT = 6379
REDIS_DB = 0
# 初始化Redis连接
redis_client = None
try:
    redis_client = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        db=REDIS_DB,
        socket_timeout=1,  # 超时时间1秒
        socket_connect_timeout=1  # 连接超时1秒
    )
    # 测试连接是否正常
    redis_client.ping()
    print("Redis连接成功")
except Exception as e:
    print(f"Redis连接失败: {e}")
    redis_client = None
if not redis_client: 
    raise Exception("Redis服务器连接失败！IP访问限制必须启用！")

# IP访问限制配置
RATE_LIMIT_PER_MINUTE = 60  # 每分钟最大请求数
RATE_LIMIT_PER_HOUR = 300   # 每小时最大请求数

def is_ip_limited(ip):
    """
    检查IP是否超过访问频率限制
    返回True表示需要限制，False表示允许访问
    """
    if not ip:
        return False  # 比较危险，但是不得不这么做，毕竟没有X-Real-IP这个事可能性并不大

    assert redis_client, "我Redis呢"
    
    try:
        # 每分钟请求计数
        minute_key = f"rate_limit_minute:{ip}"
        minute_count = redis_client.incrby(minute_key, 1)
        if minute_count == 1:
            redis_client.expire(minute_key, 60)  # 首次设置时添加60秒过期
        
        # 每小时请求计数
        hour_key = f"rate_limit_hour:{ip}"
        hour_count = redis_client.incrby(hour_key, 1)
        if hour_count == 1:
            redis_client.expire(hour_key, 3600)  # 首次设置时添加3600秒过期
        
        # 检查是否超过限制
        if minute_count > RATE_LIMIT_PER_MINUTE or hour_count > RATE_LIMIT_PER_HOUR:  # type: ignore
            return True
        return False
    except redis.RedisError as e:
        print(f"Redis操作错误: {e}")
        return False  # Redis出错时不做限制

serverinfo = {}
try:
    path = None
    if os.path.exists('./server.json'):
        path = './server.json'
    elif os.path.exists('./proxyserver/server.json'):
        path = './proxyserver/server.json'
    if path:
        with open(path, 'r', encoding='utf-8') as f:
            serverinfo = json.load(f)

    print("server info: " + str(serverinfo)[:40] + "...")
except Exception as e:
    print("Failed to load server info: ", e)



app = Flask(__name__)

assert type(SSL_VERIFY_TARGET) == bool, f"环境问题：SSL_VERIFY_TARGET的类型为{type(SSL_VERIFY_TARGET)}"
print(f"{SSL_VERIFY_TARGET=}")

PROXY_PATH = 'proxy'  # 代理路径常量
DOMAIN_WL_ENDS = ['example.com', 'yku.edu.cn']  # 代理域名白名单后缀
scheme = 'https' if SSL_VERIFY else 'http'

def get_error_html(host):
    return f"""
<!DOCTYPE html><html><head><title>代理服务运行中</title></head><body style="font-famil
y:Arial,sans-serif;text-align:center;margin-top:50px;color:#333;"><div style="max-widt
h:600px;margin:0 auto;"><h1 style="color:#d9534f;">代理服务运行中</h1><p>当前代理地址：
{host}/{PROXY_PATH}/</p><p>如果您在调试时看到本页面，说明您可能触发了域名限制或并

发限制</p></div></body></html>
"""

def proxy_to(host, url):
    """
    URL转换函数，将目标URL转换为代理URL格式
    示例: https://e.cn/path -> https://proxy.cn/e.cn/path
    """
    if not url:
        return ''
    
    parsed = urlparse(url)
    proxy_path = f"{scheme}://{host}/{PROXY_PATH}/{parsed.netloc}{parsed.path if parsed.path else ''}"
    if parsed.query:
        proxy_path += f"?{parsed.query}"
    if parsed.fragment:
        proxy_path += f"#{parsed.fragment}"
    
    return proxy_path

def get_cors_headers():
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
            for domain in ACCESS_ORIGINS
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

def process_set_cookie(cookie_header, target_domain):
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
                    value = f"/{PROXY_PATH}/{target_domain}{value}"
                    has_path_field = True
                if key_lower == 'samesite':
                    value = 'Lax'

                new_fields.append(f"{key}={value}")
            else:  # 无值字段直接加
                if not SSL_VERIFY and field.strip().lower() == 'secure':
                    continue
                new_fields.append(field)
        if not has_path_field:
            new_fields.append(f"Path=/{PROXY_PATH}/{target_domain}")
        new_cookie_headers.append('; '.join(new_fields).strip())
    
    return new_cookie_headers

@app.before_request
def check_ip_limit():
    """在每个请求处理前检查IP访问频率"""
    # 客户端真实IP
    client_ip = request.headers.get('X-Real-IP', request.remote_addr)
    
    # 检查IP限制
    if not client_ip:
        print("警告：这人没有ip")
    if is_ip_limited(client_ip):
        cors_headers = get_cors_headers()
        return Response(
            get_error_html(request.host),
            status=429,
            mimetype='text/html',
            headers=cors_headers
        )
    return None  # 继续正常处理请求

@app.route(f'/api/server', methods=['GET'])
def info_serverinfo():
    """返回服务器信息"""
    cors_headers = get_cors_headers()
    return Response(
        json.dumps(serverinfo),
        mimetype='application/json',
        headers=cors_headers
    )


@app.route(f'/{PROXY_PATH}/', methods=['GET', 'POST'])
def proxy_root():
    """处理直接访问/proxy/的情况（返回HTML错误页面）"""
    cors_headers = get_cors_headers()
    return Response(
        get_error_html(request.host),
        status=400,
        mimetype='text/html',
        headers=cors_headers
    )

@app.route(f'/{PROXY_PATH}/<path:path>', methods=['GET', 'POST'])
def proxy(path):
    """
    处理代理请求，将请求转发到目标服务器
    """

    target_domain = path.split('/')[0]
    host = request.host
    # 目标域名白名单检查
    if not any(
        target_domain.endswith(domain)
        for domain in DOMAIN_WL_ENDS
    ):
        cors_headers = get_cors_headers()
        return Response(
            'Forbidden: Proxy access to this domain is not allowed',
            status=403,
            headers=cors_headers
        )
    
    # 构建目标URL
    target_url = f"https://{path}"
    if request.query_string:
        target_url += f"?{request.query_string.decode('utf-8')}"
    
    # 准备请求头
    headers = {}
    for key, value in request.headers:
        if key.lower() in ['referer']:
            # headers[key] = revert_referer(value)
            continue
        # 过滤掉Flask自动添加的头
        if key.lower() in ['host', 'content-length']:
            continue
        else:
            headers[key] = value
    
    # 转发请求
    try:
        resp = requests.request(
            method=request.method,
            url=target_url,
            headers=headers,
            data=request.get_data(),
            cookies=request.cookies,
            allow_redirects=False,
            verify=SSL_VERIFY_TARGET,
            timeout=30
        )
    except requests.exceptions.RequestException as e:
        print(f"请求目标服务器失败: {e}")
        cors_headers = get_cors_headers()
        return Response(
            f"Proxy error: {str(e)}",
            status=502,
            headers=cors_headers
        )
    
    # 处理响应
    response = Response(resp.content, resp.status_code)
    
    # 处理其他响应头
    for key, value in resp.headers.items():
        key_lower = key.lower()
        
        if key_lower in ['content-encoding', 'content-length', 'transfer-encoding', 'connection']:
            continue
            
        if key_lower == 'set-cookie':
            for cookie in process_set_cookie(value, target_domain):
                response.headers.add('Set-Cookie', cookie)
            continue
            
        if key_lower == 'location':
            # 处理重定向
            new_location = proxy_to(request.host, value)
            response.headers[key] = new_location
            continue
        
        response.headers[key] = value
    
    # 添加CORS头部
    for key, value in get_cors_headers().items():
        response.headers[key] = value
    
    return response

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=PORT, debug=False)
    except:
        pass

if __name__ == '__main__1':
    print(proxy_to('192.168.43.88', 'http://jwgl.yku.edu.cn/sso.jsp?ticket=ST-3509-Eqor2q3ApswJA8SIMRYw-7Q4huolocalhost'))
