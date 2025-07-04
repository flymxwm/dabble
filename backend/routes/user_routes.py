from flask import Blueprint, request, jsonify
from backend.models import db, User
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from functools import wraps

user_bp = Blueprint('user', __name__, url_prefix='/api/users')

# 登录认证装饰器
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(' ')[1]
        
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        
        try:
            data = jwt.decode(token, 'secret_key', algorithms=['HS256'])
            current_user = User.query.filter_by(id=data['user_id']).first()
        except:
            return jsonify({'message': 'Token is invalid!'}), 401
        
        return f(current_user, *args, **kwargs)
    return decorated

# 用户登录
@user_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    
    if not user or not check_password_hash(user.password, data['password']):
        return jsonify({'message': '用户名或密码错误'}), 401
    
    token = jwt.encode({
        'user_id': user.id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=8)
    }, 'secret_key')
    
    user.last_login = datetime.datetime.now()
    db.session.commit()
    
    return jsonify({
        'token': token,
        'user': user.to_dict()
    })

# 获取用户列表
@user_bp.route('', methods=['GET'])
@token_required
def get_users(current_user):
    # 管理员才能查看所有用户
    if current_user.role_id != 1:
        return jsonify({'message': '没有权限查看用户列表'}), 403
    
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])

# 创建新用户
@user_bp.route('', methods=['POST'])
@token_required
def create_user(current_user):
    if current_user.role_id != 1:
        return jsonify({'message': '没有权限创建用户'}), 403
    
    data = request.get_json()
    
    # 检查用户名是否已存在
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'message': '用户名已存在'}), 400
    
    hashed_password = generate_password_hash(data['password'], method='sha256')
    new_user = User(
        username=data['username'],
        password=hashed_password,
        role_id=data['role_id'],
        real_name=data.get('real_name'),
        department=data.get('department'),
        phone=data.get('phone')
    )
    
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({'message': '用户创建成功', 'user_id': new_user.id}), 201

# 更新用户信息
@user_bp.route('/<int:user_id>', methods=['PUT'])
@token_required
def update_user(current_user, user_id):
    if current_user.role_id != 1 and current_user.id != user_id:
        return jsonify({'message': '没有权限更新此用户'}), 403
    
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    
    if 'username' in data and data['username'] != user.username:
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'message': '用户名已存在'}), 400
        user.username = data['username']
    
    if 'password' in data:
        user.password = generate_password_hash(data['password'], method='sha256')
    
    if 'role_id' in data and current_user.role_id == 1:
        user.role_id = data['role_id']
    
    user.real_name = data.get('real_name', user.real_name)
    user.department = data.get('department', user.department)
    user.phone = data.get('phone', user.phone)
    user.is_active = data.get('is_active', user.is_active)
    
    db.session.commit()
    
    return jsonify({'message': '用户信息更新成功'})

# 删除用户
@user_bp.route('/<int:user_id>', methods=['DELETE'])
@token_required
def delete_user(current_user, user_id):
    if current_user.role_id != 1:
        return jsonify({'message': '没有权限删除用户'}), 403
    
    if current_user.id == user_id:
        return jsonify({'message': '不能删除当前登录用户'}), 400
    
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    
    return jsonify({'message': '用户已删除'})