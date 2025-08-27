from flask import Blueprint, request, Response, current_app
import requests
from app.middleware import check_ip_limit
from app.utils import get_cors_headers, process_set_cookie, proxy_to, get_error_html

proxy_bp = Blueprint('proxy', __name__)

@proxy_bp.before_request
def before_proxy_request():
    """代理请求前的IP检查"""
    from app.extensions import redis_client
    return check_ip_limit(redis_client, current_app.config)

@proxy_bp.route('/', methods=['GET', 'POST'])
def root():
    """处理直接访问/proxy/的情况"""
    from flask import current_app
    cors_headers = get_cors_headers(current_app.config)
    return Response(
        get_error_html(request.host, current_app.config['PROXY_PATH']),
        status=400,
        mimetype='text/html',
        headers=cors_headers
    )


@proxy_bp.route('/<path:path>', methods=['GET', 'POST'])
def proxy(path):
    """
    处理代理请求，将请求转发到目标服务器
    """

    target_domain = path.split('/')[0]
    forwarded_proto = request.headers.get("X-Forwarded-Proto", "http")
    # 目标域名白名单检查
    if not any(
        target_domain.endswith(domain)
        for domain in current_app.config['DOMAIN_WL_ENDS']
    ):
        cors_headers = get_cors_headers(current_app.config)
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
        # 过滤掉Flask自动添加的头和nginx的头
        if key.lower() in ['host', 'content-length', 'X-Real-IP', 'X-Forwarded-For', 'X-Forwarded-Proto']:
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
            verify=current_app.config['SSL_VERIFY_TARGET'],
            timeout=30
        )
    except requests.exceptions.RequestException as e:
        print(f"请求目标服务器失败: {e}")
        cors_headers = get_cors_headers(current_app.config)
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
            for cookie in process_set_cookie(value, target_domain, forwarded_proto, current_app.config['PROXY_PATH']):
                response.headers.add('Set-Cookie', cookie)
            continue
            
        if key_lower == 'location':
            # 处理重定向
            new_location = proxy_to(request.host, value, forwarded_proto, current_app.config['PROXY_PATH'])
            response.headers[key] = new_location
            continue
        
        response.headers[key] = value
    
    # 添加CORS头部
    for key, value in get_cors_headers(current_app.config).items():
        response.headers[key] = value
    
    return response