from functools import wraps
from typing import Literal
from flask import request

from app.utils import ResponseJson
from app.models import SuperUser
from app.const import Errors

def get_current_bearer():
    """从请求头中获取当前认证"""
    bearer = request.headers.get('Authorization')
    if not bearer or '+' not in bearer:
        return (None, None)
    
    try:
        un, tk = bearer.split("+", 1)
        return un, tk
    except Exception:
        return (None, None)

def verify(un: str|None|Literal[0xDEADBEEF]=0xDEADBEEF, tk: str|None=None):
    """验证bearer token并返回用户等级"""
    # return 3
    try:
        if un == 0xDEADBEEF:
            un, tk = get_current_bearer()
        if not un or not tk:
            return 0
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
            request_level = verify(*get_current_bearer())
            if request_level < level:
                return ResponseJson({"error": 1, "message": Errors.FORBIDDEN}, 403)
            return func(*args, **kwargs)
        return wrapper
    return decorator