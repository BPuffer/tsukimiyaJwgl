class Errors:
    UNEXPECTED_ERROR = "服务器错误"
    MISSING_PARAMETER = "缺少参数"
    INVALID_PARAMETER = "无效参数"
    FORBIDDEN = "权限不足"
    USERNAME_EXISTS = "用户名已存在"
    INVALID_BEARER = "无效的Bearer"
    DB_ERROR = UNEXPECTED_ERROR  # 避免攻击
    USER_NOT_FOUND = INVALID_PARAMETER  # 避免攻击
    ANNOUNCEMENT_NOT_FOUND = "公告不存在"
    EVENT_NOT_FOUND = "活动不存在"
    INVALID_TIMEORDER = "时间顺序无效"
    INVALID_MODIFYING_FIELD = "正在修改的字段无效"




