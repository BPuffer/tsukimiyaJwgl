# api.py
from datetime import datetime, timezone
import time
from flask import Blueprint, request, current_app
from app.models import Announcement, Event, SuperUser
from app.middleware import check_ip_limit
from app.auth import auth_minlvl, get_current_bearer, verify
from app.utils import generate_token, get_cors_headers, ResponseJson, has_all_keys, is_valid_date
from app.extensions import db
from app.const import Errors

api_bp = Blueprint('api', __name__)

@api_bp.before_request
def before_proxy_request():
    """代理请求前的IP检查"""
    from app.extensions import redis_client
    return check_ip_limit(redis_client, current_app.config)

@api_bp.after_request
def after_proxy_request(response):
    """代理请求后的处理"""
    cors_headers = get_cors_headers(current_app.config)
    for key, value in cors_headers.items():
        response.headers[key] = value
    return response

@api_bp.route('/server', methods=['GET'])
def info_serverinfo():
    """返回服务器信息"""
    from app.extensions import redis_client
    return ResponseJson({
        "announcements": Announcement.get_all_json_cached(redis_client), 
        "events": Event.get_all_json_cached(redis_client)
    }, 200)

@api_bp.route('/addsu', methods=['POST'])
@auth_minlvl(3)
def add_super():
    """
    POST /api/addsu
    添加一个新的超级用户到系统。

    请求体（json）：
    - username (str): 要添加的用户名，必须是ASCII字符串。
    - level (str, null): 用户的等级，必须是字符串表示的整数，范围在1到3之间。默认为1。
    - comment (str, null): 注释。

    成功响应（状态码200）：
    返回JSON对象，包含：
    - error: 0
    - message: ""
    - data: 对象，包含添加用户的username、token（系统生成的密码）和level。

    错误响应：
    - error: 1
    - message: 错误信息
    """
    # 参数抽取
    data = request.get_json()
    if not has_all_keys(data, ['username']):
        return ResponseJson({"error": 1, "message": Errors.MISSING_PARAMETER}, 400) 
    
    # 参数验证
    username_to_add: str = data['username']
    level_to_add: str = data.get('level', 1)
    comment_to_add: str = data.get('comment', '')
    if not username_to_add.isascii():
        return ResponseJson({"error": 1, "message": Errors.INVALID_PARAMETER + "(username)"}, 400)

    try:
        if not 1 <= (level_to_add_int := int(level_to_add)) <= 3:
            raise ValueError
    except (ValueError, TypeError):
        return ResponseJson({"error": 1, "message": Errors.INVALID_PARAMETER + "(level)"}, 400)
    if SuperUser.query.filter_by(username=username_to_add).first():
        return ResponseJson({"error": 1, "message": Errors.USERNAME_EXISTS}, 400)
    
    # 生成密码
    token_to_add = generate_token()
    
    # 创建新用户（默认等级1）
    new_user = SuperUser(
        username=username_to_add,  # type: ignore
        token=token_to_add,  # type: ignore
        level=level_to_add_int,  # type: ignore
        comment=comment_to_add  # type: ignore
        # 我记得有一个检查dataclass-like class的装饰器用来类型提示，
        # 但flask-sqlalchemy没支持，我也忘了。。想起来再说吧。
    )
    try:
        db.session.add(new_user)
        db.session.commit()
        return ResponseJson({
            "error": 0, "message": "", 
            "data": {
                "username": username_to_add, 
                "token": token_to_add, 
                "level": level_to_add}
            }, 200)
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"添加超级用户时出错: {e}")
        return ResponseJson({"error": 1, "message": Errors.DB_ERROR}, 500)

@api_bp.route('/lstsu', methods=['GET'])
@auth_minlvl(3)
def list_super():
    """
    GET /api/lstsu
    返回所有超级用户的信息列表。

    成功响应（状态码200）：
    返回JSON对象，包含：
    - error: 0
    - message: ""
    - data: 列表，每个元素是一个对象，包含username，level和comment。

    错误响应：
    - error: 1
    - message: 错误信息
    """
    # 查询所有超级用户
    try:
        super_users = SuperUser.query.all()
        user_list = [{
            "username": user.username,
            "level": user.level,
            "comment": user.comment or '-'
        } for user in super_users]
        
        return ResponseJson({
            "error": 0, 
            "message": "", 
            "data": user_list
        }, 200)
    except Exception as e:
        current_app.logger.error(f"查询超级用户列表时出错: {e}")
        return ResponseJson({"error": 1, "message": Errors.DB_ERROR}, 500)

@api_bp.route('/delsu', methods=['POST'])
@auth_minlvl(3)
def del_super():
    """
    POST /api/delsu
    删除指定的超级用户。

    请求体（json）：
    - bearer (str): 认证令牌，要求权限等级3。
    - username (str): 要删除的用户名，必须是ASCII字符串。

    成功响应（状态码200）：
    返回JSON对象，包含：
    - error: 0
    - message: ""

    错误响应：
    - error: 1
    - message: 错误信息
    """
    # 参数抽取
    data = request.get_json()
    if not has_all_keys(data, ['username']):
        return ResponseJson({"error": 1, "message": Errors.MISSING_PARAMETER}, 400)
    
    # 参数验证
    username_to_delete = data['username']
    if not username_to_delete.isascii():
        return ResponseJson({"error": 1, "message": Errors.INVALID_PARAMETER}, 400)
    
    # 检查要删除的用户是否存在
    user_to_delete = SuperUser.query.filter_by(username=username_to_delete).first()
    if not user_to_delete:
        return ResponseJson({"error": 1, "message": Errors.USER_NOT_FOUND}, 400)

    # 执行删除操作
    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        return ResponseJson({
            "error": 0, 
            "message": ""
        }, 200)
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"删除超级用户时出错: {e}")
        return ResponseJson({"error": 1, "message": Errors.DB_ERROR}, 500)

@api_bp.route('/addan', methods=['POST'])
@auth_minlvl(1)
def add_announcement():
    """
    POST /api/addan
    添加一个新的系统公告。

    请求体（json）：
    - announcement (object): 公告对象，包含以下字段：
        - title (str): 公告标题，必须是可打印字符串
        - content (str): 公告内容，必须是可打印字符串
        - date (str): 公告日期，必须是可打印字符串
        - hue (str): 色调值，必须是0-360之间的整数
        - tag (str, null): 公告标签，必须是可打印字符串，默认为空
        - category (str, null): 公告类别，必须是normal/important/hidden之一，默认为normal

    成功响应（状态码200）：
    返回JSON对象，包含：
    - error: 0
    - message: ""
    - data: 对象，包含新公告的id

    错误响应：
    - error: 1
    - message: 错误信息
    """
    from app.extensions import redis_client
    
    # 参数抽取
    data = request.get_json()
    if not has_all_keys(data, ['announcement']):
        return ResponseJson({"error": 1, "message": Errors.MISSING_PARAMETER + "(announcement)"}, 400)
    
    # 参数验证
    ann_json = data['announcement']
    if not 'tag' in ann_json: ann_json['tag'] = ''
    if not 'category' in ann_json: ann_json['category'] = 'normal'
    if not has_all_keys(ann_json, ['title', 'content', 'date', 'hue']):
        return ResponseJson({"error": 1, "message": Errors.MISSING_PARAMETER + "(announcement)"}, 400)


    # 验证字段内容
    for field in ['title', 'date', 'tag']:
        if not isinstance(ann_json[field], str) or not ann_json[field].isprintable():
            return ResponseJson({"error": 1, "message": Errors.INVALID_PARAMETER + f"({field} 包含非法字符如换行)"}, 400)
    
    # 验证hue字段
    try:
        hue_int = int(ann_json['hue'])
        if not 0 <= hue_int <= 360:
            raise ValueError
    except (ValueError, TypeError):
        return ResponseJson({"error": 1, "message": Errors.INVALID_PARAMETER + f"(hue={ann_json['hue']})"}, 400)
    
    # 验证category字段
    if ann_json['category'] not in ['normal', 'important', 'hidden']:
        return ResponseJson({"error": 1, "message": Errors.INVALID_PARAMETER + f"(category={ann_json['category']})"}, 400)
    
    un, _ = get_current_bearer()
    new_ann = Announcement(
        title=ann_json['title'],  # type: ignore
        content=ann_json['content'],  # type: ignore
        date=ann_json['date'],  # type: ignore
        tag=ann_json['tag'],  # type: ignore
        hue=hue_int,  # type: ignore
        category=ann_json['category'],  # type: ignore
        publisher=un,  # type: ignore
    )
    
    # 数据库操作
    try:
        db.session.add(new_ann)
        db.session.commit()
        
        # 清除缓存
        try:
            redis_client.delete("announcements:all")
        except Exception as e:
            pass
        
        return ResponseJson({
            "error": 0, 
            "message": "",
            "data": {"id": new_ann.id}
        }, 200)
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"添加公告时出错: {e}")
        return ResponseJson({"error": 1, "message": Errors.DB_ERROR}, 500)

@api_bp.route('/delan', methods=['POST'])
@auth_minlvl(2)
def del_announcement():
    """
    POST /api/delan
    删除指定的系统公告。

    请求体（json）：
    - id (str): 要删除的公告ID，必须是有效的整数

    成功响应（状态码200）：
    返回JSON对象，包含：
    - error: 0
    - message: ""

    错误响应：
    - error: 1
    - message: 错误信息
    """
    from app.extensions import redis_client
    
    # 参数抽取
    data = request.get_json()
    if not has_all_keys(data, ['id']):
        return ResponseJson({"error": 1, "message": Errors.MISSING_PARAMETER}, 400)
    
    # 参数验证
    ann_id = data['id']
    try:
        ann_id_int = int(ann_id)
    except (ValueError, TypeError):
        return ResponseJson({"error": 1, "message": Errors.INVALID_PARAMETER}, 400)
    
    # 查找要删除的公告
    ann = Announcement.query.get(ann_id_int)
    if not ann:
        return ResponseJson({"error": 1, "message": Errors.ANNOUNCEMENT_NOT_FOUND}, 400)
    
    # 数据库操作
    try:
        db.session.delete(ann)
        db.session.commit()
        
        # 清除缓存
        try:
            redis_client.delete("announcements:all")
        except Exception as e:
            pass
        
        return ResponseJson({
            "error": 0, 
            "message": ""
        }, 200)
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"删除公告时出错: {e}")
        return ResponseJson({"error": 1, "message": Errors.DB_ERROR}, 500)

@api_bp.route('/modan', methods=['POST'])
@auth_minlvl(1)
def mod_announcement():
    """
    POST /api/modan
    修改指定的系统公告。

    请求体（json）：
    - id (int/str): 要修改的公告ID
    - announcement (object): 包含要更新字段的对象，可选字段包括：
    - title (str): 公告标题，必须是可打印字符串
    - content (str): 公告内容，必须是可打印字符串
    - date (str): 公告日期，必须是可打印字符串
    - tag (str): 公告标签，必须是可打印字符串
    - hue (str): 色调值，必须是0-360之间的整数
    - category (str): 公告类别，必须是normal/important/hidden之一

    成功响应（状态码200）：
    返回JSON对象，包含：
    - error: 0
    - message: ""

    错误响应：
    - error: 1
    - message: 错误信息
    """
    from app.extensions import redis_client
    from datetime import datetime, timezone
    
    # 参数抽取
    data = request.get_json()
    if not has_all_keys(data, ['id', 'announcement']):
        return ResponseJson({"error": 1, "message": Errors.MISSING_PARAMETER}, 400)
    
    # 参数验证
    ann_id = data['id']
    ann_json = data['announcement']
    
    if not isinstance(ann_id, (int, str)) or (isinstance(ann_id, str) and not ann_id.isdigit()):
        return ResponseJson({"error": 1, "message": Errors.INVALID_PARAMETER}, 400)
    
    # 转换为整数ID
    try:
        ann_id_int = int(ann_id)
    except (ValueError, TypeError):
        return ResponseJson({"error": 1, "message": Errors.INVALID_PARAMETER}, 400)
    
    # 查找要修改的公告
    ann = Announcement.query.get(ann_id_int)
    if not ann:
        return ResponseJson({"error": 1, "message": Errors.ANNOUNCEMENT_NOT_FOUND}, 400)
    
    # 检查权限：level1用户只能修改自己发布的公告
    un, tk = get_current_bearer()  # current_user 现在是非空的
    if ann.publisher and ann.publisher != un and verify(un, tk) == 1:
        return ResponseJson({"error": 1, "message": Errors.FORBIDDEN}, 403)
    
    # 不设置新的发布者。发布者在发布之初就已经决定好了。
    if not ann.publisher:
        ann.publisher = un  # 兼容旧的数据库，旧的 publisher 字段可能为空
    
    # 验证更新字段
    allowed_fields = ['title', 'content', 'date', 'tag', 'hue', 'category']
    for field in ann_json:
        if field not in allowed_fields:
            return ResponseJson({"error": 1, "message": Errors.INVALID_PARAMETER}, 400)
    
    # 验证字段内容
    for field in ['title', 'date', 'tag']:
        if field in ann_json and (not isinstance(ann_json[field], str) or not ann_json[field].isprintable()):
            return ResponseJson({"error": 1, "message": Errors.INVALID_PARAMETER}, 400)
    
    # 验证hue字段
    if 'hue' in ann_json:
        try:
            hue_int = int(ann_json['hue'])
            if not 0 <= hue_int <= 360:
                raise ValueError
            ann_json['hue'] = hue_int
        except (ValueError, TypeError):
            return ResponseJson({"error": 1, "message": Errors.INVALID_PARAMETER}, 400)
    
    # 验证category字段
    if 'category' in ann_json and ann_json['category'] not in ['normal', 'important', 'hidden']:
        return ResponseJson({"error": 1, "message": Errors.INVALID_PARAMETER}, 400)
    
    # 更新公告字段
    for field in allowed_fields:
        if field in ann_json:
            setattr(ann, field, ann_json[field])
    
    ann.updated_at = datetime.now(timezone.utc)
    
    # 数据库操作
    try:
        db.session.commit()
        
        # 清除缓存
        try:
            redis_client.delete("announcements:all")
        except Exception as e:
            pass
        
        return ResponseJson({
            "error": 0, 
            "message": ""
        }, 200)
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"修改公告时出错: {e}")
        return ResponseJson({"error": 1, "message": Errors.UNEXPECTED_ERROR}, 500)

@api_bp.route('/addev', methods=['POST'])
@auth_minlvl(1)
def add_event():
    """
    POST /api/addev
    添加一个新的活动。

    请求体（json）：
    - event (object): 活动对象，包含以下字段：
    - title (str): 活动标题
    - description (str): 活动描述
    - date_tag (str): 日期标签
    - prevImg (str): 预览图片URL
    
    成功响应（状态码200）：
    返回JSON对象，包含：
    - error: 0
    - message: ""
    - data: 对象，包含创建活动的ID

    错误响应：
    - error: 1
    - message: 错误信息
    """
    from app.extensions import redis_client
    
    # 参数抽取
    data = request.get_json()
    if not has_all_keys(data, ['event']):
        return ResponseJson({"error": 1, "message": Errors.MISSING_PARAMETER}, 400)
    
    # 参数验证
    eve_json = data['event']
    required_fields = ['title', 'description', 'date_tag', 'timestamp', 'prevImg']
    if not has_all_keys(eve_json, required_fields):
        return ResponseJson({"error": 1, "message": Errors.MISSING_PARAMETER}, 400)
    
    # 验证字段内容
    for field in ['title', 'prevImg']:
        if not isinstance(eve_json[field], str) or not eve_json[field].isprintable():
            return ResponseJson({"error": 1, "message": Errors.INVALID_PARAMETER}, 400)
    
    un, _ = get_current_bearer()
    new_event = Event(
        title=eve_json['title'],  # type: ignore
        description=eve_json['description'],  # type: ignore
        date_tag=eve_json['date_tag'],  # type: ignore
        timestamp=int(eve_json['timestamp']),  # type: ignore
        prevImg=eve_json['prevImg'],  # type: ignore
        publisher=un,  # type: ignore
    )
    
    # 数据库操作
    try:
        db.session.add(new_event)
        db.session.commit()
        
        # 清除缓存
        try:
            redis_client.delete("events:all")
        except Exception as e:
            pass
        
        return ResponseJson({
            "error": 0, 
            "message": "",
            "data": {"id": new_event.id}
        }, 200)
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"添加活动时出错: {e}")
        return ResponseJson({"error": 1, "message": Errors.DB_ERROR}, 500)

@api_bp.route('/delev', methods=['POST'])
@auth_minlvl(2)
def del_event():
    """
    POST /api/delev
    删除指定的活动。

    请求体（json）：
    - id (str): 要删除的活动ID，必须是数字字符串。

    成功响应（状态码200）：
    返回JSON对象，包含：
    - error: 0
    - message: ""

    错误响应：
    - error: 1
    - message: 错误信息
    """
    from app.extensions import redis_client
    
    # 参数抽取
    data = request.get_json()
    if not has_all_keys(data, ['id']):
        return ResponseJson({"error": 1, "message": Errors.MISSING_PARAMETER}, 400)
    
    # 参数验证
    try:
        eve_id_int = int(data['id'])
    except (ValueError, TypeError):
        return ResponseJson({"error": 1, "message": Errors.INVALID_PARAMETER}, 400)
    
    # 查找要删除的活动
    event = Event.query.get(eve_id_int)
    if not event:
        return ResponseJson({"error": 1, "message": Errors.EVENT_NOT_FOUND}, 400)
    
    # 数据库操作
    try:
        db.session.delete(event)
        db.session.commit()
        
        # 清除缓存
        try:
            redis_client.delete("events:all")
        except Exception as e:
            pass
        
        return ResponseJson({
            "error": 0, 
            "message": ""
        }, 200)
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"删除活动时出错: {e}")
        return ResponseJson({"error": 1, "message": Errors.DB_ERROR}, 500)

@api_bp.route('/modev', methods=['POST'])
@auth_minlvl(1)
def mod_event():
    """
    POST /api/modev
    修改指定活动的信息。

    请求体（json）：
    - id (str): 要修改的活动ID
    - event (object): 包含要更新字段的对象
    
    成功响应（状态码200）：
    返回JSON对象，包含：
    - error: 0
    - message: ""

    错误响应：
    - error: 1
    - message: 错误信息
    """
    from app.extensions import redis_client
    
    # 参数抽取
    data = request.get_json()
    if not has_all_keys(data, ['id', 'event']):
        return ResponseJson({"error": 1, "message": Errors.MISSING_PARAMETER}, 400)
    
    try:
        eve_id_int = int(data['id'])
    except (ValueError, TypeError):
        return ResponseJson({"error": 1, "message": Errors.INVALID_PARAMETER}, 400)
    
    # 查找要修改的活动
    event = Event.query.get(eve_id_int)
    if not event:
        return ResponseJson({"error": 1, "message": Errors.EVENT_NOT_FOUND}, 400)
    
    # 检查权限：level2用户只能修改自己发布的活动
    un, tk = get_current_bearer()  # current_user 现在是非空的 
    if event.publisher != un and verify(un, tk) == 1:
        return ResponseJson({"error": 1, "message": Errors.FORBIDDEN}, 403)
    
    # 不设置新的发布者。发布者在发布之初就已经决定好了。
    if not event.publisher:
        event.publisher = un  # 兼容旧的数据库，旧的 publisher 字段可能为空
    
    eve_json = data['event']
    allowed_fields = ['title', 'description', 'date_tag', 'timestamp', 'prevImg']
    
    for field in eve_json:
        if field not in allowed_fields:
            return ResponseJson({"error": 1, "message": Errors.INVALID_MODIFYING_FIELD + f"({field})"}, 400)
    
    for field in ['title', 'prevImg']:
        if field in eve_json and (not isinstance(eve_json[field], str) or not eve_json[field].isprintable()):
            return ResponseJson({"error": 1, "message": Errors.INVALID_PARAMETER}, 400)
    
    # 更新活动字段
    for field in allowed_fields:
        if field in eve_json:
            setattr(event, field, eve_json[field])
    
    # 更新修改时间
    event.updated_at = datetime.now(timezone.utc)
    
    # 数据库操作
    try:
        db.session.commit()
        
        # 清除缓存
        try:
            redis_client.delete("events:all")
        except Exception as e:
            pass
        
        return ResponseJson({
            "error": 0, 
            "message": ""
        }, 200)
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"修改活动时出错: {e}")
        return ResponseJson({"error": 1, "message": Errors.DB_ERROR}, 500)
