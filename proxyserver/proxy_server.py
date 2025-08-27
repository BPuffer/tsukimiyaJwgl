from app import create_app
from config import Config

app = create_app(Config)

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=app.config['PORT'], debug=False)
    except Exception as e:
        app.logger.error(f"启动失败: {e}")