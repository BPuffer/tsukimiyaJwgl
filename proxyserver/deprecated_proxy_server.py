from datetime import datetime, timezone
import os
import secrets
from flask import Flask, jsonify, request, Response, make_response
import requests
from urllib.parse import urlparse, urljoin
import urllib3
urllib3.disable_warnings()
import re
import json
from dotenv import load_dotenv
load_dotenv()
import redis

from flask_sqlachemy import SQLAlchemy  # type: ignore

# 环境配置
# 前端域名白名单，用于处理跨域问题，处于这些白名单中的Origin予以通过
ACCESS_ORIGINS_str = os.environ.get("ACCESS_ORIGINS", '192.168.43.88;localhost;yku.tsukimiya.site;82.156.135.94')
ACCESS_ORIGINS = list(map(str.strip, ACCESS_ORIGINS_str.split(';')))

# 端口号。本地服务开放时使用的端口号。默认5000
PORT = int(os.getenv('PORT', 20081))
# 转发时是否验证SSL证书
SSL_VERIFY_TARGET = os.getenv('SSL_VERIFY_TARGET', 'False').lower() == 'true'
# 是否跳过429检查
NO_LIMIT = os.getenv('NO_LIMIT', 'False').lower() == 'true'

# Redis配置
REDIS_HOST = 'localhost'  # IP限制用Redis，可以固定在本地
REDIS_PORT = 6379
REDIS_DB = 0
# 初始化Redis连接
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
    raise e

assert redis_client, "Redis服务器连接失败！IP访问限制必须启用！"

# IP访问限制配置
RATE_LIMIT_PER_MINUTE = 60  # 每分钟最大请求数
RATE_LIMIT_PER_HOUR = 300   # 每小时最大请求数

def is_ip_limited(ip):
    """
    检查IP是否超过访问频率限制
    返回True表示需要限制，False表示允许访问
    """
    if not ip or NO_LIMIT:
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

print(f"{SSL_VERIFY_TARGET=}")

PROXY_PATH = 'proxy'  # 代理路径常量
DOMAIN_WL_ENDS = ['example.com', 'yku.edu.cn']  # 代理域名白名单后缀



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI', 'sqlite:///data.db')
db = SQLAlchemy(app)

class Announcement(db.Model):
    __tablename__ = 'announcements'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date = db.Column(db.String(10), nullable=False)  # 格式: YYYY-MM-DD
    tag = db.Column(db.String(20), nullable=False)
    hue = db.Column(db.Integer, nullable=False)
    category = db.Column(db.String(20), default='normal')
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'date': self.date,
            'tag': self.tag,
            'hue': self.hue
        }
    
    @classmethod
    def get_all_json_cached(cls):
        """获取所有公告的JSON格式数据，使用Redis缓存"""
        cache_key = f"announcements:all"
        cached_data = redis_client.get(cache_key)
        if cached_data:
            return json.loads(cached_data)  # type: ignore
        # 缓存未命中，从数据库获取
        announcements = cls.query.order_by(cls.id.desc()).all()
        result = {
            "normal": [ann.to_dict() for ann in announcements if ann.category == 'normal']
        }
        # 缓存
        redis_client.setex(cache_key, 300, json.dumps(result))  # 缓存5分钟
        return result


class Event(db.Model):
    __tablename__ = 'events'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    dateStartReg = db.Column(db.String(10), nullable=False)  # 格式: YYYY-MM-DD
    dateStart = db.Column(db.String(10), nullable=False)    # 格式: YYYY-MM-DD
    dateEnd = db.Column(db.String(10), nullable=False)      # 格式: YYYY-MM-DD
    prevImg = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'dateStartReg': self.dateStartReg,
            'dateStart': self.dateStart,
            'dateEnd': self.dateEnd,
            'prevImg': self.prevImg
        }
    
    @classmethod
    def get_all_json_cached(cls):
        """获取所有活动的JSON格式数据，使用Redis缓存"""
        cache_key = f"events:all"
        cached_data = redis_client.get(cache_key)
        if cached_data:
            return json.loads(cached_data)  # type: ignore
        # 缓存未命中，从数据库获取
        events = cls.query.order_by(cls.id.desc()).all()
        result = {str(event.id): event.to_dict() for event in events}
        # 缓存
        redis_client.setex(cache_key, 300, json.dumps(result))  # 缓存5分钟
        return result


class SuperUser(db.Model):
    __tablename__ = 'super_users'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(36), nullable=False)
    level = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

def verify(bearer):
    """验证bearer token并返回用户等级"""
    try:
        # 从bearer token中提取用户名和密码
        if not bearer or '+' not in bearer:
            return 0
            
        un, pwd = bearer.split("+", 1)  # 只分割一次
        
        # 查询数据库验证用户
        user = SuperUser.query.filter_by(username=un, password=pwd).first()
        if user:
            return user.level
        return 0
    except Exception:
        return 0  # 等级0表示未认证或认证失败

def generate_password():
    """生成随机36位密码（字母和数字）"""
    alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    return ''.join(secrets.choice(alphabet) for _ in range(36))

@app.route('/api/addsu', methods=['POST'])
def add_super():
    """添加超级用户"""
    # 获取请求数据
    data = request.get_json()
    if not data or 'bearer' not in data or 'username' not in data:
        return jsonify({"error": 1, "message": "Missing parameters"})
    
    bearer = data['bearer']
    username_a = data['username']
    
    # 验证请求者权限
    request_level = verify(bearer)
    if request_level < 3:
        return jsonify({"error": 1, "message": "Insufficient permissions"})
    
    # 检查用户名是否已存在
    if SuperUser.query.filter_by(username=username_a).first():
        return jsonify({"error": 1, "message": "Username already exists"})
    
    # 生成密码
    password = generate_password()
    
    # 创建新用户（默认等级1）
    new_user = SuperUser(
        username=username_a,
        password=password,
        level=1
    )
    
    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"error": 0, "message": "User added", "password": password})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": 1, "message": f"Database error: {str(e)}"})

@app.route('/api/delsu', methods=['POST'])
def del_super():
    """删除超级用户"""
    data = request.get_json()
    if not data or 'bearer' not in data or 'username' not in data:
        return jsonify({"error": 1, "message": "Missing parameters"})
    
    bearer = data['bearer']
    username_a = data['username']
    
    # 验证请求者权限
    request_level = verify(bearer)
    if request_level < 3:
        return jsonify({"error": 1, "message": "Insufficient permissions"})
    
    # 查找要删除的用户
    user = SuperUser.query.filter_by(username=username_a).first()
    if not user:
        return jsonify({"error": 1, "message": "User not found"})
    
    # 不能删除自己
    request_un, _ = bearer.split("+", 1)
    if user.username == request_un:
        return jsonify({"error": 1, "message": "Cannot delete yourself"})
    
    try:
        db.session.delete(user)
        db.session.commit()
        return jsonify({"error": 0, "message": "User deleted"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": 1, "message": f"Database error: {str(e)}"})

@app.route('/api/addan', methods=['POST'])
def add_announcement():
    """添加公告"""
    data = request.get_json()
    if not data or 'bearer' not in data or 'announcement' not in data:
        return jsonify({"error": 1, "message": "Missing parameters"})
    
    bearer = data['bearer']
    ann_json = data['announcement']
    
    # 验证请求者权限
    request_level = verify(bearer)
    if request_level < 1:
        return jsonify({"error": 1, "message": "Insufficient permissions"})
    
    # 验证公告数据
    required_fields = ['title', 'content', 'date', 'tag', 'hue']
    for field in required_fields:
        if field not in ann_json:
            return jsonify({"error": 1, "message": f"Missing field: {field}"})
    
    # 创建新公告
    new_ann = Announcement(
        title=ann_json['title'],
        content=ann_json['content'],
        date=ann_json['date'],
        tag=ann_json['tag'],
        hue=ann_json['hue'],
        category=ann_json.get('category', 'normal')
    )
    
    try:
        db.session.add(new_ann)
        db.session.commit()
        
        # 清除缓存
        redis_client.delete("announcements:all")
        
        return jsonify({"error": 0, "message": "Announcement added", "id": new_ann.id})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": 1, "message": f"Database error: {str(e)}"})

@app.route('/api/delan', methods=['POST'])
def del_announcement():
    """删除公告"""
    data = request.get_json()
    if not data or 'bearer' not in data or 'id' not in data:
        return jsonify({"error": 1, "message": "Missing parameters"})
    
    bearer = data['bearer']
    ann_id = data['id']
    
    # 验证请求者权限
    request_level = verify(bearer)
    if request_level < 2:
        return jsonify({"error": 1, "message": "Insufficient permissions"})
    
    # 查找要删除的公告
    ann = Announcement.query.get(ann_id)
    if not ann:
        return jsonify({"error": 1, "message": "Announcement not found"})
    
    try:
        db.session.delete(ann)
        db.session.commit()
        
        # 清除缓存
        redis_client.delete("announcements:all")
        
        return jsonify({"error": 0, "message": "Announcement deleted"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": 1, "message": f"Database error: {str(e)}"})

@app.route('/api/modan', methods=['POST'])
def mod_announcement():
    """修改公告"""
    data = request.get_json()
    if not data or 'bearer' not in data or 'id' not in data or 'announcement' not in data:
        return jsonify({"error": 1, "message": "Missing parameters"})
    
    bearer = data['bearer']
    ann_id = data['id']
    ann_json = data['announcement']
    
    # 验证请求者权限
    request_level = verify(bearer)
    if request_level < 2:
        return jsonify({"error": 1, "message": "Insufficient permissions"})
    
    # 查找要修改的公告
    ann = Announcement.query.get(ann_id)
    if not ann:
        return jsonify({"error": 1, "message": "Announcement not found"})
    
    # 更新公告字段
    if 'title' in ann_json:
        ann.title = ann_json['title']
    if 'content' in ann_json:
        ann.content = ann_json['content']
    if 'date' in ann_json:
        ann.date = ann_json['date']
    if 'tag' in ann_json:
        ann.tag = ann_json['tag']
    if 'hue' in ann_json:
        ann.hue = ann_json['hue']
    if 'category' in ann_json:
        ann.category = ann_json['category']
    
    ann.updated_at = datetime.now(timezone.utc)
    
    try:
        db.session.commit()
        
        # 清除缓存
        redis_client.delete("announcements:all")
        
        return jsonify({"error": 0, "message": "Announcement updated"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": 1, "message": f"Database error: {str(e)}"})

@app.route('/api/addev', methods=['POST'])
def add_event():
    """添加活动"""
    data = request.get_json()
    if not data or 'bearer' not in data or 'event' not in data:
        return jsonify({"error": 1, "message": "Missing parameters"})
    
    bearer = data['bearer']
    eve_json = data['event']
    
    # 验证请求者权限
    request_level = verify(bearer)
    if request_level < 1:
        return jsonify({"error": 1, "message": "Insufficient permissions"})
    
    # 验证活动数据
    required_fields = ['title', 'description', 'dateStartReg', 'dateStart', 'dateEnd', 'prevImg']
    for field in required_fields:
        if field not in eve_json:
            return jsonify({"error": 1, "message": f"Missing field: {field}"})
    
    # 创建新活动
    new_event = Event(
        title=eve_json['title'],
        description=eve_json['description'],
        dateStartReg=eve_json['dateStartReg'],
        dateStart=eve_json['dateStart'],
        dateEnd=eve_json['dateEnd'],
        prevImg=eve_json['prevImg']
    )
    
    try:
        db.session.add(new_event)
        db.session.commit()
        
        # 清除缓存
        redis_client.delete("events:all")
        
        return jsonify({"error": 0, "message": "Event added", "id": new_event.id})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": 1, "message": f"Database error: {str(e)}"})

@app.route('/api/delev', methods=['POST'])
def del_event():
    """删除活动"""
    data = request.get_json()
    if not data or 'bearer' not in data or 'id' not in data:
        return jsonify({"error": 1, "message": "Missing parameters"})
    
    bearer = data['bearer']
    eve_id = data['id']
    
    # 验证请求者权限
    request_level = verify(bearer)
    if request_level < 2:
        return jsonify({"error": 1, "message": "Insufficient permissions"})
    
    # 查找要删除的活动
    event = Event.query.get(eve_id)
    if not event:
        return jsonify({"error": 1, "message": "Event not found"})
    
    try:
        db.session.delete(event)
        db.session.commit()
        
        # 清除缓存
        redis_client.delete("events:all")
        
        return jsonify({"error": 0, "message": "Event deleted"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": 1, "message": f"Database error: {str(e)}"})

@app.route('/api/modev', methods=['POST'])
def mod_event():
    """修改活动"""
    data = request.get_json()
    if not data or 'bearer' not in data or 'id' not in data or 'event' not in data:
        return jsonify({"error": 1, "message": "Missing parameters"})
    
    bearer = data['bearer']
    eve_id = data['id']
    eve_json = data['event']
    
    # 验证请求者权限
    request_level = verify(bearer)
    if request_level < 2:
        return jsonify({"error": 1, "message": "Insufficient permissions"})
    
    # 查找要修改的活动
    event = Event.query.get(eve_id)
    if not event:
        return jsonify({"error": 1, "message": "Event not found"})
    
    # 更新活动字段
    if 'title' in eve_json:
        event.title = eve_json['title']
    if 'description' in eve_json:
        event.description = eve_json['description']
    if 'dateStartReg' in eve_json:
        event.dateStartReg = eve_json['dateStartReg']
    if 'dateStart' in eve_json:
        event.dateStart = eve_json['dateStart']
    if 'dateEnd' in eve_json:
        event.dateEnd = eve_json['dateEnd']
    if 'prevImg' in eve_json:
        event.prevImg = eve_json['prevImg']
    
    event.updated_at = datetime.now(timezone.utc)
    
    try:
        db.session.commit()
        
        # 清除缓存
        redis_client.delete("events:all")
        
        return jsonify({"error": 0, "message": "Event updated"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": 1, "message": f"Database error: {str(e)}"})


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

def process_set_cookie(cookie_header, target_domain, forwarded_proto):
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
                if not forwarded_proto=='https' and field.strip().lower() == 'secure':
                    continue
                new_fields.append(field)
        if not has_path_field:
            new_fields.append(f"Path=/{PROXY_PATH}/{target_domain}")
        new_cookie_headers.append('; '.join(new_fields).strip())
    
    return new_cookie_headers

def proxy_to(host, url, forwarded_proto):
    """
    URL转换函数，将目标URL转换为代理URL格式
    示例: https://e.cn/path -> https://proxy.cn/e.cn/path
    """
    if not url:
        return ''
    
    parsed = urlparse(url)
    proxy_path = f"{forwarded_proto}://{host}/{PROXY_PATH}/{parsed.netloc}{parsed.path if parsed.path else ''}"
    if parsed.query:
        proxy_path += f"?{parsed.query}"
    if parsed.fragment:
        proxy_path += f"#{parsed.fragment}"
    
    return proxy_path

def get_error_html(host):
    return f"""
<!DOCTYPE html><html><head><title>代理服务运行中</title></head><body style="font-famil
y:Arial,sans-serif;text-align:center;margin-top:50px;color:#333;"><div style="max-widt
h:600px;margin:0 auto;"><h1 style="color:#d9534f;">代理服务运行中</h1><p>当前代理地址：
{host}/{PROXY_PATH}/</p><p>如果您在调试时看到本页面，说明您可能触发了域名限制或并

发限制</p></div></body></html>
"""

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
@app.route(f'/', methods=['GET', 'POST'])
def root():
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
    forwarded_proto = request.headers.get("X-Forwarded-Proto", "http")
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
            for cookie in process_set_cookie(value, target_domain, forwarded_proto):
                response.headers.add('Set-Cookie', cookie)
            continue
            
        if key_lower == 'location':
            # 处理重定向
            new_location = proxy_to(request.host, value, forwarded_proto)
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
    print(proxy_to('192.168.43.88', 'http://jwgl.yku.edu.cn/sso.jsp?ticket=ST-3509-Eqor2q3ApswJA8SIMRYw-7Q4huolocalhost', 'http'))
