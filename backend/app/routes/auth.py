from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from app import db
from app.models import Admin, Student, Teacher

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    """统一登录接口"""
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
                    'class_name': user.class_info.class_name if user.class_info else '',
                    'type': 'student'
                }
        
        if user:
            # 创建访问令牌
            access_token = create_access_token(
                identity={'id': user_info['id'], 'type': user_type}
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
    current_user = get_jwt_identity()
    data = request.get_json()
    
    if not data or not data.get('old_password') or not data.get('new_password'):
        return jsonify({'message': '旧密码和新密码不能为空'}), 400
    
    old_password = data['old_password']
    new_password = data['new_password']
    
    try:
        user = None
        user_type = current_user['type']
        user_id = current_user['id']
        
        if user_type == 'admin':
            user = Admin.query.filter_by(admin_id=user_id).first()
        elif user_type == 'teacher':
            user = Teacher.query.filter_by(teacher_id=user_id).first()
        elif user_type == 'student':
            user = Student.query.filter_by(student_id=user_id).first()
        
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
    current_user = get_jwt_identity()
    return jsonify({
        'message': 'Token有效',
        'user': current_user
    }), 200
