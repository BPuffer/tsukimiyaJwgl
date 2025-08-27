from functools import wraps
from flask import request

from app.utils import ResponseJson
from app.models import SuperUser
from app.const import Errors

def verify(bearer):
    """验证bearer token并返回用户等级"""
    # return 3
    try:
        if not bearer or '+' not in bearer:
            return 0
            
        un, tk = bearer.split("+", 1)
        
        # 查询数据库验证用户
        user = SuperUser.query.filter_by(username=un, token=tk).first()
        if user:
            return user.level
        return 0
    except Exception:
        return 0


def auth_minlvl(level):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            request_level = verify(request.headers.get('Authorization'))
            if request_level < level:
                return ResponseJson({"error": 1, "message": Errors.FORBIDDEN}, 403)
            return func(*args, **kwargs)
        return wrapper
    return decorator