from flask_sqlalchemy import SQLAlchemy
import redis

db = SQLAlchemy()
redis_client = None

def init_redis(app):
    global redis_client
    try:
        redis_client = redis.Redis(
            host=app.config['REDIS_HOST'],
            port=app.config['REDIS_PORT'],
            db=app.config['REDIS_DB'],
            socket_timeout=1,
            socket_connect_timeout=1
        )
        redis_client.ping()
        app.logger.info("Redis连接成功")
        return redis_client
    except Exception as e:
        app.logger.error(f"Redis连接失败: {e}")
        raise e