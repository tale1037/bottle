
from datetime import datetime

from extension import db


class User(db.Model):
    __tablename__ = 'user'  # 数据库中的表名

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(255))  # 如果你要用账号密码登录
    token = db.Column(db.String(255))  # 扫码用的临时 token
    last_login = db.Column(db.DateTime, default=datetime.utcnow)

class Record(db.Model):
    __tablename__ = 'record'
    record_id = db.Column(db.Integer, primary_key=True)
    point = db.Column(db.Integer, unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    ifwater = db.Column(db.Boolean, nullable=False)
    posttime = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'ifwater': self.ifwater,
            'user_id': self.user_id,
            'point':self.point,
            'timestamp': self.posttime.isoformat()  # 日期字段要格式化
        }

class ExchangeRecord(db.Model):
    __tablename__ = 'exchange_record'
    exid = db.Column(db.Integer, primary_key=True)
    consume = db.Column(db.Integer, unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.String(255), nullable=False)
    recordtime = db.Column(db.DateTime, default=datetime.utcnow)
