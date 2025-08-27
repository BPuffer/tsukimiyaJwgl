
from warnings import warn
from flask import request, Response
import redis
from .utils import get_error_html, get_cors_headers

def check_ip_limit(redis_client, app_config):
    """IP限制检查装饰器"""
    client_ip = request.headers.get('X-Real-IP', request.remote_addr)

    if not client_ip:
        warn("警告：这人没有ip")
    
    if is_ip_limited(redis_client, app_config, client_ip):
        cors_headers = get_cors_headers(app_config)
        return Response(
            get_error_html(request.host, app_config['PROXY_PATH']),
            status=429,
            mimetype='text/html',
            headers=cors_headers
        )

def is_ip_limited(redis_client, app_config, ip):
    """检查IP是否超过访问频率限制"""
    if not ip or app_config['NO_LIMIT']:
        return False
    
    try:
        # 每分钟请求计数
        minute_key = f"rate_limit_minute:{ip}"
        minute_count = redis_client.incrby(minute_key, 1)
        if minute_count == 1:
            redis_client.expire(minute_key, 60)
        
        # 每小时请求计数
        hour_key = f"rate_limit_hour:{ip}"
        hour_count = redis_client.incrby(hour_key, 1)
        if hour_count == 1:
            redis_client.expire(hour_key, 3600)
        
        print(f"IP: {ip}, 分钟请求数: {minute_count}, 小时请求数: {hour_count}")
        
        # 检查是否超过限制
        if minute_count > app_config['RATE_LIMIT_PER_MINUTE'] or hour_count > app_config['RATE_LIMIT_PER_HOUR']:
            return True
        return False
    except redis.RedisError as e:
        warn(f"Redis操作错误: {e}")
        return False