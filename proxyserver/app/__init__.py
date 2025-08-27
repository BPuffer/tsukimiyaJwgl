import os
from flask import Flask
from config import Config
from app.extensions import db, init_redis
from app.routes.api import api_bp
from app.routes.proxy import proxy_bp

def create_app(config_class=Config):
    print(f"--- 运行位置: {os.getcwd()} ---")

    print("--- 初始化app ---")

    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # 初始化扩展
    print(f"--- 初始化sqlite({app.config['SQLALCHEMY_DATABASE_URI']}) ---")
    db.init_app(app)
    print("--- 初始化redis ---")
    init_redis(app)
    from app.extensions import redis_client
    assert redis_client, "Redis初始化异常"

    # 确保数据库表存在
    with app.app_context():
        from app.models import Announcement
        try:
            Announcement.query.limit(1).all()
        except Exception as e:
            if "no such table" in str(e):
                print("初始化数据库表...")
                db.create_all()
                print("数据库表创建完成")
            else:
                raise e
    
    # 注册蓝图
    print("--- 注册蓝图 ---")
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(proxy_bp, url_prefix=f'/{app.config["PROXY_PATH"]}')
    
    # 注册根路由
    @app.route('/', methods=['GET', 'POST'])
    def root():
        from flask import request
        from app.utils import get_error_html
        return get_error_html(request.host, app.config['PROXY_PATH'])
    
    print("--- 初始化完成 ---")
    return app