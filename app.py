import os
from datetime import datetime, date

import bcrypt
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import uuid
import time

from models import User, Record, ExchangeRecord
from extension import db
from predictiffull.predict import predictbypath

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:123456@118.193.38.84:10188/BOTTLE'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['JWT_SECRET_KEY'] = 'jwt_secret_key'  # 配置JWT密钥
CORS(app)

db.init_app(app)
# 简单内存缓存
tokens = {}

@app.route('/api/get_login_token')
def get_login_token():
    token = str(uuid.uuid4())
    tokens[token] = {'status': 'pending', 'created': time.time(),'user_id':-1}
    return jsonify({'token': token})

@app.route('/api/check_token')
def check_token():
    token = request.args.get('token')
    if token not in tokens:
        print(token)
        print(111)
        print(tokens)
        return jsonify({'status': 'invalid'})
    else:
        print(token + "+" + tokens[token]['status'])
        return jsonify({'status': tokens[token]['status'],'user_id': tokens[token]['user_id']})

@app.route('/api/confirm_login', methods=['POST'])
def confirm_login():
    data = request.json
    token = data.get('token')
    if token in tokens:
        tokens[token]['status'] = 'success'
        return jsonify({'message': '登录成功'})
    return jsonify({'message': '无效 token'}), 400


@app.route('/api/scan_login', methods=['POST'])
def scan_login():
    data = request.get_json()
    token = data.get('token')
    username = data.get('username')  # 可通过手机号、微信ID等
    email = data.get('email')

    user = User.query.filter_by(username=username).first()
    if not user:
        user = User(username=username, email=email)
        db.session.add(user)

    # 绑定 token 到该用户
    user.token = token
    db.session.commit()
    return jsonify({'message': '扫码绑定成功'})

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 确保上传目录存在
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/api/recycle', methods=['POST'])
def recycle():
    print(request.files)
    if 'file' not in request.files:
        return jsonify({'error': '没有文件上传'}), 400
    user_id = request.form.get('id')
    print(user_id)
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '文件名为空'}), 400

    # 生成安全的文件名
    from werkzeug.utils import secure_filename
    filename = secure_filename(file.filename)

    # 保存文件
    save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(save_path)

    # 示例：你可以在这记录数据库，做分类，返积分等逻辑
    print(f"用户 {user_id} 上传了文件：{filename}")
    conf,label = predictbypath(save_path)
    if label == 'full':
        point = 10
        ifwater = True
    else:
        point = 20
        ifwater = False
    newrecord = Record(point = point,user_id = user_id, ifwater = ifwater, posttime = datetime.fromtimestamp(time.time()))
    db.session.add(newrecord)
    db.session.commit()
    return jsonify({
        'message': '扫描完成',
        'ifwater':label,
        'conf':float(conf),
        'point':point
    })
@app.route('/api/mobile-register', methods=['POST'])
def register():

    data = request.get_json()
    phone = data.get('phone')
    password = data.get('password')
    username = data.get('username')
    print(data)
    # 检查手机号是否已存在
    user = User.query.filter_by(phone=phone).first()
    if user:
        return jsonify({'success': False, 'message': '手机号已存在'}), 400

    # 密码加密
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    # 保存新用户
    new_user = User(phone=phone, password=hashed_password,username=username)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'success': True, 'message': '注册成功'})

@app.route('/api/mobile-login', methods=['POST'])
def login():
    data = request.get_json()

    phone = data.get('phone')
    password = data.get('password')
    token = data.get('token')
    print(data)
    # 查找用户
    user = User.query.filter_by(phone=phone).first()
    print(user)
    if token in tokens:
        tokens[token]['status'] = 'success'
        tokens[token]['user_id'] = user.id
        print(tokens[token]['user_id'])
        if user is None:
            return jsonify({'success': False,'message':"没有此用户！"})
        if user and bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
            return jsonify({'success': True, 'message': '登录成功','id':user.id})
        else:
            return jsonify({'success': False, 'message': '手机号或密码错误'}), 400
    return jsonify({'message': '无效 token'}), 400

@app.route('/api/recyclerecord',methods = ['GET'])
def recyclerecord():
    user_id = request.args.get('user_id')
    print(user_id)
    records = Record.query.filter_by(user_id=user_id).all()
    record_dicts = [r.to_dict() for r in records]
    return jsonify({'success':True,'message':' ','data':record_dicts})

@app.route('/api/getuserinfo',methods = ['GET'])
def getuserinfo():
    user_id = request.args.get('user_id')

    user = User.query.filter_by(id=user_id).first()
    records = Record.query.filter_by(user_id=user_id).all()
    exchange = ExchangeRecord.query.filter_by(user_id=user_id).all()
    print(len(records))
    total_point = 0
    for r in records:
        total_point += r.point
    for r in exchange:
        total_point -= r.consume
    return jsonify({'success':True,'message':' ','username':user.username,'point':total_point})
@app.route('/api/get_todayinfo',methods = ['GET'])
def get_todayinfo():
    today = date.today()
    user_id = request.args.get('user_id')
    # 获取今天 00:00:00 的时间
    start = datetime.combine(today, datetime.min.time())
    # 获取明天 00:00:00 的时间，方便用于小于判断
    end = datetime.combine(today, datetime.max.time())
    user = User.query.filter_by(id=user_id).first()
    # 查询今天的 Record
    records = Record.query.filter(
        Record.user_id == user_id,
        Record.posttime >= start,
        Record.posttime <= end
    ).all()
    print(len(records))
    total_point = 0
    for r in records:
        total_point += r.point
    return jsonify({'success':True,'message':' ','nums':len(records),'point':total_point})

@app.route('/api/exchange',methods = ['POST'])
def exchange():
    data = request.get_json()
    name = data.get('name')
    point = data.get('point')
    user_id = data.get('user_id')
    print(f"id:{user_id}")
    exchange = ExchangeRecord(content=name, consume=point,user_id=user_id,recordtime = datetime.fromtimestamp(time.time()))
    db.session.add(exchange)
    db.session.commit()
    return jsonify({'success':True,'message':' ','id':user_id})


if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')
