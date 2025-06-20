from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import Admin, Student, Teacher, Course, Class, CourseOffering, Enrollment
from sqlalchemy import func, desc

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    """管理员权限装饰器"""
    def decorated_function(*args, **kwargs):
        current_user = get_jwt_identity()
        if current_user['type'] != 'admin':
            return jsonify({'message': '权限不足，需要管理员权限'}), 403
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

# 教师管理
@admin_bp.route('/teachers', methods=['GET'])
@jwt_required()
@admin_required
def get_teachers():
    """获取教师列表"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        search = request.args.get('search', '')
        
        query = Teacher.query
        if search:
            query = query.filter(
                (Teacher.name.contains(search)) |
                (Teacher.teacher_id.contains(search))
            )
        
        teachers = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'teachers': [{
                'teacher_id': t.teacher_id,
                'name': t.name,
                'gender': t.gender,
                'age': t.age,
                'title': t.title,
                'phone': t.phone,
                'created_at': t.created_at.isoformat() if t.created_at else None
            } for t in teachers.items],
            'total': teachers.total,
            'pages': teachers.pages,
            'current_page': page
        }), 200
    except Exception as e:
        return jsonify({'message': f'获取教师列表失败: {str(e)}'}), 500

@admin_bp.route('/teachers', methods=['POST'])
@jwt_required()
@admin_required
def add_teacher():
    """添加教师"""
    data = request.get_json()
    
    required_fields = ['teacher_id', 'name', 'gender', 'age', 'title', 'phone', 'password']
    if not all(field in data for field in required_fields):
        return jsonify({'message': '所有字段都是必填的'}), 400
    
    try:
        # 检查教师编号是否已存在
        if Teacher.query.filter_by(teacher_id=data['teacher_id']).first():
            return jsonify({'message': '教师编号已存在'}), 400
        
        teacher = Teacher(
            teacher_id=data['teacher_id'],
            name=data['name'],
            gender=data['gender'],
            age=data['age'],
            title=data['title'],
            phone=data['phone']
        )
        teacher.set_password(data['password'])
        
        db.session.add(teacher)
        db.session.commit()
        
        return jsonify({'message': '教师添加成功'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'添加教师失败: {str(e)}'}), 500

@admin_bp.route('/teachers/<teacher_id>', methods=['PUT'])
@jwt_required()
@admin_required
def update_teacher(teacher_id):
    """修改教师信息"""
    data = request.get_json()
    
    try:
        teacher = Teacher.query.filter_by(teacher_id=teacher_id).first()
        if not teacher:
            return jsonify({'message': '教师不存在'}), 404
        
        # 更新字段
        if 'name' in data:
            teacher.name = data['name']
        if 'gender' in data:
            teacher.gender = data['gender']
        if 'age' in data:
            teacher.age = data['age']
        if 'title' in data:
            teacher.title = data['title']
        if 'phone' in data:
            teacher.phone = data['phone']
        if 'password' in data:
            teacher.set_password(data['password'])
        
        db.session.commit()
        
        return jsonify({'message': '教师信息更新成功'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'更新教师信息失败: {str(e)}'}), 500

@admin_bp.route('/teachers/<teacher_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_teacher(teacher_id):
    """删除教师"""
    try:
        teacher = Teacher.query.filter_by(teacher_id=teacher_id).first()
        if not teacher:
            return jsonify({'message': '教师不存在'}), 404
        
        # 检查是否有相关的开课记录
        if teacher.offerings:
            return jsonify({'message': '该教师有相关开课记录，无法删除'}), 400
        
        db.session.delete(teacher)
        db.session.commit()
        
        return jsonify({'message': '教师删除成功'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'删除教师失败: {str(e)}'}), 500

# 学生管理
@admin_bp.route('/students', methods=['GET'])
@jwt_required()
@admin_required
def get_students():
    """获取学生列表"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        search = request.args.get('search', '')
        class_id = request.args.get('class_id', '')
        
        query = Student.query.join(Class)
        if search:
            query = query.filter(
                (Student.name.contains(search)) |
                (Student.student_id.contains(search))
            )
        if class_id:
            query = query.filter(Student.class_id == class_id)
        
        students = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'students': [{
                'student_id': s.student_id,
                'name': s.name,
                'gender': s.gender,
                'age': s.age,
                'hometown': s.hometown,
                'total_credits': s.total_credits,
                'class_id': s.class_id,
                'class_name': s.class_info.class_name if s.class_info else '',
                'created_at': s.created_at.isoformat() if s.created_at else None
            } for s in students.items],
            'total': students.total,
            'pages': students.pages,
            'current_page': page
        }), 200
    except Exception as e:
        return jsonify({'message': f'获取学生列表失败: {str(e)}'}), 500

@admin_bp.route('/students', methods=['POST'])
@jwt_required()
@admin_required
def add_student():
    """添加学生"""
    data = request.get_json()
    
    required_fields = ['student_id', 'name', 'gender', 'age', 'hometown', 'password', 'class_id']
    if not all(field in data for field in required_fields):
        return jsonify({'message': '所有字段都是必填的'}), 400
    
    try:
        # 检查学号是否已存在
        if Student.query.filter_by(student_id=data['student_id']).first():
            return jsonify({'message': '学号已存在'}), 400
        
        # 检查班级是否存在
        if not Class.query.filter_by(class_id=data['class_id']).first():
            return jsonify({'message': '班级不存在'}), 400
        
        student = Student(
            student_id=data['student_id'],
            name=data['name'],
            gender=data['gender'],
            age=data['age'],
            hometown=data['hometown'],
            total_credits=data.get('total_credits', 0),
            class_id=data['class_id']
        )
        student.set_password(data['password'])
        
        db.session.add(student)
        db.session.commit()
        
        return jsonify({'message': '学生添加成功'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'添加学生失败: {str(e)}'}), 500

@admin_bp.route('/students/<student_id>', methods=['PUT'])
@jwt_required()
@admin_required
def update_student(student_id):
    """修改学生信息"""
    data = request.get_json()
    
    try:
        student = Student.query.filter_by(student_id=student_id).first()
        if not student:
            return jsonify({'message': '学生不存在'}), 404
        
        # 更新字段
        if 'name' in data:
            student.name = data['name']
        if 'gender' in data:
            student.gender = data['gender']
        if 'age' in data:
            student.age = data['age']
        if 'hometown' in data:
            student.hometown = data['hometown']
        if 'total_credits' in data:
            student.total_credits = data['total_credits']
        if 'class_id' in data:
            # 检查班级是否存在
            if not Class.query.filter_by(class_id=data['class_id']).first():
                return jsonify({'message': '班级不存在'}), 400
            student.class_id = data['class_id']
        if 'password' in data:
            student.set_password(data['password'])
        
        db.session.commit()
        
        return jsonify({'message': '学生信息更新成功'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'更新学生信息失败: {str(e)}'}), 500

@admin_bp.route('/students/<student_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_student(student_id):
    """删除学生"""
    try:
        student = Student.query.filter_by(student_id=student_id).first()
        if not student:
            return jsonify({'message': '学生不存在'}), 404
        
        db.session.delete(student)
        db.session.commit()
        
        return jsonify({'message': '学生删除成功'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'删除学生失败: {str(e)}'}), 500

# 课程管理
@admin_bp.route('/courses', methods=['GET'])
@jwt_required()
@admin_required
def get_courses():
    """获取课程列表"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        search = request.args.get('search', '')
        
        query = Course.query
        if search:
            query = query.filter(
                (Course.course_name.contains(search)) |
                (Course.course_id.contains(search))
            )
        
        courses = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'courses': [{
                'course_id': c.course_id,
                'course_name': c.course_name,
                'hours': c.hours,
                'exam_type': c.exam_type,
                'credits': c.credits,
                'created_at': c.created_at.isoformat() if c.created_at else None
            } for c in courses.items],
            'total': courses.total,
            'pages': courses.pages,
            'current_page': page
        }), 200
    except Exception as e:
        return jsonify({'message': f'获取课程列表失败: {str(e)}'}), 500

@admin_bp.route('/courses', methods=['POST'])
@jwt_required()
@admin_required
def add_course():
    """添加课程"""
    data = request.get_json()
    
    required_fields = ['course_id', 'course_name', 'hours', 'exam_type', 'credits']
    if not all(field in data for field in required_fields):
        return jsonify({'message': '所有字段都是必填的'}), 400
    
    try:
        # 检查课程编号是否已存在
        if Course.query.filter_by(course_id=data['course_id']).first():
            return jsonify({'message': '课程编号已存在'}), 400
        
        course = Course(
            course_id=data['course_id'],
            course_name=data['course_name'],
            hours=data['hours'],
            exam_type=data['exam_type'],
            credits=data['credits']
        )
        
        db.session.add(course)
        db.session.commit()
        
        return jsonify({'message': '课程添加成功'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'添加课程失败: {str(e)}'}), 500

@admin_bp.route('/courses/<course_id>', methods=['PUT'])
@jwt_required()
@admin_required
def update_course(course_id):
    """修改课程信息"""
    data = request.get_json()
    
    try:
        course = Course.query.filter_by(course_id=course_id).first()
        if not course:
            return jsonify({'message': '课程不存在'}), 404
        
        # 更新字段
        if 'course_name' in data:
            course.course_name = data['course_name']
        if 'hours' in data:
            course.hours = data['hours']
        if 'exam_type' in data:
            course.exam_type = data['exam_type']
        if 'credits' in data:
            course.credits = data['credits']
        
        db.session.commit()
        
        return jsonify({'message': '课程信息更新成功'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'更新课程信息失败: {str(e)}'}), 500

@admin_bp.route('/courses/<course_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_course(course_id):
    """删除课程"""
    try:
        course = Course.query.filter_by(course_id=course_id).first()
        if not course:
            return jsonify({'message': '课程不存在'}), 404
        
        # 检查是否有相关的开课记录
        if course.offerings:
            return jsonify({'message': '该课程有相关开课记录，无法删除'}), 400
        
        db.session.delete(course)
        db.session.commit()
        
        return jsonify({'message': '课程删除成功'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'删除课程失败: {str(e)}'}), 500

# 班级管理
@admin_bp.route('/classes', methods=['GET'])
@jwt_required()
@admin_required
def get_classes():
    """获取班级列表"""
    try:
        classes = Class.query.all()
        return jsonify([{
            'class_id': c.class_id,
            'class_name': c.class_name,
            'student_count': len(c.students)
        } for c in classes]), 200
    except Exception as e:
        return jsonify({'message': f'获取班级列表失败: {str(e)}'}), 500

@admin_bp.route('/classes', methods=['POST'])
@jwt_required()
@admin_required
def add_class():
    """添加班级"""
    data = request.get_json()
    
    if not data or not data.get('class_id') or not data.get('class_name'):
        return jsonify({'message': '班级编号和班级名称不能为空'}), 400
    
    try:
        # 检查班级编号是否已存在
        if Class.query.filter_by(class_id=data['class_id']).first():
            return jsonify({'message': '班级编号已存在'}), 400
        
        class_obj = Class(
            class_id=data['class_id'],
            class_name=data['class_name']
        )
        
        db.session.add(class_obj)
        db.session.commit()
        
        return jsonify({'message': '班级添加成功'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'添加班级失败: {str(e)}'}), 500

# 统计信息
@admin_bp.route('/statistics', methods=['GET'])
@jwt_required()
@admin_required
def get_statistics():
    """获取系统统计信息"""
    try:
        teacher_count = Teacher.query.count()
        student_count = Student.query.count()
        course_count = Course.query.count()
        class_count = Class.query.count()
        offering_count = CourseOffering.query.count()
        enrollment_count = Enrollment.query.count()
        
        return jsonify({
            'teacher_count': teacher_count,
            'student_count': student_count,
            'course_count': course_count,
            'class_count': class_count,
            'offering_count': offering_count,
            'enrollment_count': enrollment_count
        }), 200
    except Exception as e:
        return jsonify({'message': f'获取统计信息失败: {str(e)}'}), 500
