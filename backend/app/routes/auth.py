from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, get_jwt
from functools import wraps
from app import db
from app.models import Admin, Student, Teacher

auth_bp = Blueprint('auth', __name__)

def admin_required(f):
    """管理员权限装饰器"""
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        try:
            claims = get_jwt()
            if claims.get('type') != 'admin':
                return jsonify({'message': '需要管理员权限'}), 403
            return f(*args, **kwargs)
        except Exception as e:
            return jsonify({'message': '身份验证失败'}), 401
    return decorated_function

def teacher_required(f):
    """教师权限装饰器"""
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        try:
            claims = get_jwt()
            if claims.get('type') != 'teacher':
                return jsonify({'message': '需要教师权限'}), 403
            return f(*args, **kwargs)
        except Exception as e:
            return jsonify({'message': '身份验证失败'}), 401
    return decorated_function

def student_required(f):
    """学生权限装饰器"""
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        try:
            claims = get_jwt()
            if claims.get('type') != 'student':
                return jsonify({'message': '需要学生权限'}), 403
            return f(*args, **kwargs)
        except Exception as e:
            return jsonify({'message': '身份验证失败'}), 401
    return decorated_function

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    用户登录接口
    ---
    tags:
      - 用户认证
    summary: 用户登录
    description: 支持管理员、教师、学生三种用户类型的统一登录接口
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - username
            - password
            - user_type
          properties:
            username:
              type: string
              description: 用户名（管理员用户名/教师工号/学号）
              example: "admin"
            password:
              type: string
              description: 登录密码
              example: "123456"
            user_type:
              type: string
              enum: [admin, teacher, student]
              description: 用户类型
              example: "admin"
    responses:
      200:
        description: 登录成功
        schema:
          type: object
          properties:
            message:
              type: string
              example: "登录成功"
            access_token:
              type: string
              description: JWT访问令牌
              example: "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
            user:
              type: object
              description: 用户信息
              properties:
                id:
                  type: string
                  description: 用户ID
                name:
                  type: string
                  description: 用户姓名
                type:
                  type: string
                  description: 用户类型
      400:
        description: 请求参数错误
        schema:
          type: object
          properties:
            message:
              type: string
              example: "用户名、密码和用户类型不能为空"
      401:
        description: 用户名或密码错误
        schema:
          type: object
          properties:
            message:
              type: string
              example: "用户名或密码错误"
      500:
        description: 服务器内部错误
        schema:
          type: object
          properties:
            message:
              type: string
              example: "登录失败: 详细错误信息"
    """
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('password') or not data.get('user_type'):
        return jsonify({'message': '用户名、密码和用户类型不能为空'}), 400
    
    username = data['username']
    password = data['password']
    user_type = data['user_type']  # 'admin', 'teacher', 'student'
    
    user = None
    user_info = {}
    
    try:
        if user_type == 'admin':
            user = Admin.query.filter_by(username=username).first()
            if user and user.check_password(password):
                user_info = {
                    'id': user.admin_id,
                    'name': user.name,
                    'username': user.username,
                    'type': 'admin'
                }
        
        elif user_type == 'teacher':
            user = Teacher.query.filter_by(teacher_id=username).first()
            if user and user.check_password(password):
                user_info = {
                    'id': user.teacher_id,
                    'name': user.name,
                    'gender': user.gender,
                    'age': user.age,
                    'title': user.title,
                    'phone': user.phone,
                    'type': 'teacher'
                }
        elif user_type == 'student':
            user = Student.query.filter_by(student_id=username).first()
            if user and user.check_password(password):
                user_info = {
                    'id': user.student_id,
                    'name': user.name,
                    'gender': user.gender,
                    'age': user.age,
                    'hometown': user.hometown,
                    'total_credits': user.total_credits,
                    'class_id': user.class_id,
                    'type': 'student'
                }
                # 安全地获取班级名称
                try:
                    if user.class_info:
                        user_info['class_name'] = user.class_info.class_name
                    else:
                        user_info['class_name'] = ''
                except:
                    user_info['class_name'] = ''
        
        if user and user_info:
            # 创建访问令牌，使用用户ID作为identity
            access_token = create_access_token(
                identity=user_info['id'],
                additional_claims={'type': user_type, 'user_data': user_info}
            )
            
            return jsonify({
                'message': '登录成功',
                'access_token': access_token,
                'user': user_info
            }), 200
        else:
            return jsonify({'message': '用户名或密码错误'}), 401
    
    except Exception as e:
        return jsonify({'message': f'登录失败: {str(e)}'}), 500

@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """修改密码"""
    current_user_id = get_jwt_identity()
    claims = get_jwt()
    user_type = claims.get('type')
    
    data = request.get_json()
    
    if not data or not data.get('old_password') or not data.get('new_password'):
        return jsonify({'message': '旧密码和新密码不能为空'}), 400
    
    old_password = data['old_password']
    new_password = data['new_password']
    
    try:
        user = None
        
        if user_type == 'admin':
            user = Admin.query.filter_by(admin_id=current_user_id).first()
        elif user_type == 'teacher':
            user = Teacher.query.filter_by(teacher_id=current_user_id).first()
        elif user_type == 'student':
            user = Student.query.filter_by(student_id=current_user_id).first()
        
        if not user:
            return jsonify({'message': '用户不存在'}), 404
        
        if not user.check_password(old_password):
            return jsonify({'message': '旧密码错误'}), 400
        
        # 设置新密码
        user.set_password(new_password)
        db.session.commit()
        
        return jsonify({'message': '密码修改成功'}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'密码修改失败: {str(e)}'}), 500

@auth_bp.route('/verify-token', methods=['POST'])
@jwt_required()
def verify_token():
    """验证token有效性"""
    current_user_id = get_jwt_identity()
    claims = get_jwt()
    return jsonify({
        'message': 'Token有效',
        'user_id': current_user_id,
        'user_type': claims.get('type'),
        'user_data': claims.get('user_data')
    }), 200
