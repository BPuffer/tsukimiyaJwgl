import json
import os
from dotenv import load_dotenv

if not os.path.exists('.env'):
    raise FileNotFoundError(f".env文件不存在. 当前工作目录: {os.getcwd()}")

load_dotenv('.env')

class Config:
    # 环境配置
    ACCESS_ORIGINS = list(map(str.strip, os.environ.get("ACCESS_ORIGINS", '192.168.43.88;localhost;yku.tsukimiya.site;82.156.135.94').split(';')))
    PORT = int(os.getenv('PORT', 20081))
    SSL_VERIFY_TARGET = os.getenv('SSL_VERIFY_TARGET', 'False').lower() == 'true'
    if not SSL_VERIFY_TARGET:
        import urllib3
        urllib3.disable_warnings()

    NO_LIMIT = os.getenv('NO_LIMIT', 'False').lower() == 'true'
    
    # Redis配置
    REDIS_HOST = 'localhost'
    REDIS_PORT = 6379
    REDIS_DB = 0
    
    # 数据库配置
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI', 'sqlite:///data.db')
    
    # 代理配置
    PROXY_PATH = 'proxy'
    DOMAIN_WL_ENDS = ['example.com', 'yku.edu.cn']
    
    # 频率限制配置
    RATE_LIMIT_PER_MINUTE = 60
    RATE_LIMIT_PER_HOUR = 300
