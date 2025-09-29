# models.py
from datetime import datetime, timezone

from .extensions import db
import json

class Announcement(db.Model):
    __tablename__ = 'announcements'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date = db.Column(db.Text, nullable=False)  # 格式规范是YYYY-MM-DD HH:MM:SS，但模糊的也可以自定义
    timestamp = db.Column(db.Integer, default=lambda: int(datetime.now(timezone.utc).timestamp()))  # 用于排序的确切时间
    tag = db.Column(db.String(50), nullable=False)
    hue = db.Column(db.Integer, nullable=False)
    publisher = db.Column(db.String(50), nullable=True)

    category = db.Column(db.String(20), default='normal')
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'date': self.date,
            'timestamp': self.timestamp,  # 转换为时间戳
            'tag': self.tag,
            'hue': self.hue,
            'category': self.category,
            'updated_at': self.updated_at.timestamp()  # 转换为时间戳
        }
    
    @classmethod
    def get_all_json_cached(cls, redis_client):
        """获取所有公告的JSON格式数据，使用Redis缓存"""
        cache_key = f"announcements:all"
        cached_data = redis_client.get(cache_key)
        if cached_data:
            return json.loads(cached_data)
        # 缓存未命中，从数据库获取
        announcements = cls.query.order_by(cls.id.desc()).all()
        result = {
            "normal": [ann.to_dict() for ann in announcements if ann.category == 'normal']
        }
        # 缓存
        redis_client.setex(cache_key, 300, json.dumps(result))
        return result
    
    @classmethod
    def db_v1_3_update(cls):
        """
        版本更新: v1.2->v1.3
        - 添加发布者字段的数据库迁移方法
        """
        from app.extensions import db
        from sqlalchemy import inspect, text
        
        inspector = inspect(db.engine)
        columns = [col['name'] for col in inspector.get_columns('announcements')]
        if 'publisher' not in columns:
            with db.engine.connect() as conn:
                conn.execute(text('ALTER TABLE announcements ADD COLUMN publisher VARCHAR(50)'))
                conn.commit()
            print("已成功为 announcements 表添加 publisher 列")
        else:
            print("announcements 表已存在 publisher 列，无需更新")


class Event(db.Model):
    __tablename__ = 'events'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.Integer, nullable=False)
    date_tag = db.Column(db.String(100), nullable=False)
    # 用于展示，可以随便改的
    # 推荐格式：YYYY.MM.DD报名, YYYY.MM.DD - YYYY.MM.DD
    # 也可以直接写：YYYY.MM.DD - YYYY.MM.DD

    prevImg = db.Column(db.String(200), nullable=False)
    publisher = db.Column(db.String(50), nullable=True)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'timestamp': self.timestamp,
            'date_tag': self.date_tag,
            'prevImg': self.prevImg
        }
    
    @classmethod
    def get_all_json_cached(cls, redis_client):
        """获取所有活动的JSON格式数据，使用Redis缓存"""
        cache_key = f"events:all"
        cached_data = redis_client.get(cache_key)
        if cached_data:
            return json.loads(cached_data)
        # 缓存未命中，从数据库获取
        events = cls.query.order_by(cls.id.desc()).all()
        result = {str(event.id): event.to_dict() for event in events}
        # 缓存
        redis_client.setex(cache_key, 300, json.dumps(result))
        return result
    
    @classmethod
    def db_v1_3_update(cls):
        """
        版本更新: v1.2->v1.3
        - 添加发布者字段的数据库迁移方法
        """
        from app.extensions import db
        from sqlalchemy import inspect, text

        inspector = inspect(db.engine)
        if 'publisher' not in [column['name'] for column in inspector.get_columns('events')]:
            with db.engine.connect() as conn:
                conn.execute(text('ALTER TABLE events ADD COLUMN publisher VARCHAR(50)'))
                conn.commit()
            print("已成功为 events 表添加 publisher 列")
        else:
            print("events 表已存在 publisher 列，无需更新")


class SuperUser(db.Model):
    __tablename__ = 'super_users'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    token = db.Column(db.String(36), nullable=False)
    level = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))