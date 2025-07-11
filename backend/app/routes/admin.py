from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from functools import wraps
from app import db
from app.models import Admin, Student, Teacher, Course, Class, CourseOffering, Enrollment
from sqlalchemy import func, desc
from app.services.statistics_service import CourseStatisticsService

admin_bp = Blueprint('admin', 'admin')

def admin_required(f):
    """管理员权限装饰器"""
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        try:
            claims = get_jwt()
            if claims.get('type') != 'admin':
                return jsonify({'message': '权限不足，需要管理员权限'}), 403
            return f(*args, **kwargs)
        except Exception as e:
            return jsonify({'message': '身份验证失败'}), 401
    return decorated_function

# 个人信息

@admin_bp.route('/profile', methods=['GET'])
@admin_required
def get_admin_profile():
    """获取管理员个人信息"""
    admin_id = get_jwt_identity()
    try:
        admin = Admin.query.filter_by(admin_id=admin_id).first()
        if not admin:
            return jsonify({'message': '管理员不存在'}), 404
        return jsonify({
            'admin_id': admin.admin_id,
            'username': admin.username,
            'name': admin.name,
            'created_at': admin.created_at.isoformat() if admin.created_at else None
        }), 200
    except Exception as e:
        return jsonify({'message': f'获取管理员信息失败: {str(e)}'}), 500

@admin_bp.route('/profile', methods=['PUT'])
@admin_required
def update_admin_profile():
    """更新管理员个人信息（仅可修改用户名和姓名）"""
    admin_id = get_jwt_identity()
    data = request.get_json()
    if not data:
        return jsonify({'message': '请求体不能为空'}), 400
    try:
        admin = Admin.query.filter_by(admin_id=admin_id).first()
        if not admin:
            return jsonify({'message': '管理员不存在'}), 404
        # 可选字段
        if 'username' in data and data['username']:
            # 检查用户名冲突
            if Admin.query.filter(Admin.username == data['username'], Admin.admin_id != admin_id).first():
                return jsonify({'message': '用户名已被占用'}), 400
            admin.username = data['username']
        if 'name' in data and data['name']:
            admin.name = data['name']
        db.session.commit()
        return jsonify({'message': '信息更新成功'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'更新管理员信息失败: {str(e)}'}), 500
# 教师管理
@admin_bp.route('/teachers', methods=['GET'])
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
            'current_page': teachers.page
        }), 200
    except Exception as e:
        return jsonify({'message': f'获取教师列表失败: {str(e)}'}), 500

@admin_bp.route('/teachers', methods=['POST'])
@admin_required
def create_teacher():
    """创建教师"""
    try:
        data = request.get_json()
        
        # 验证必填字段
        required_fields = ['teacher_id', 'name', 'gender', 'age', 'title', 'phone', 'password']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'message': f'{field} 不能为空'}), 400
        
        # 检查教师编号是否已存在
        if Teacher.query.filter_by(teacher_id=data['teacher_id']).first():
            return jsonify({'message': '教师编号已存在'}), 400
        
        # 创建教师
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
        
        return jsonify({
            'message': '教师创建成功',
            'teacher': {
                'teacher_id': teacher.teacher_id,
                'name': teacher.name,
                'gender': teacher.gender,
                'age': teacher.age,
                'title': teacher.title,
                'phone': teacher.phone
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'创建教师失败: {str(e)}'}), 500

@admin_bp.route('/teachers/<teacher_id>', methods=['PUT'])
@admin_required
def update_teacher(teacher_id):
    """更新教师信息"""
    try:
        teacher = Teacher.query.get_or_404(teacher_id)
        data = request.get_json()
        
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
        if 'password' in data and data['password']:
            teacher.set_password(data['password'])
        
        db.session.commit()
        
        return jsonify({
            'message': '教师信息更新成功',
            'teacher': {
                'teacher_id': teacher.teacher_id,
                'name': teacher.name,
                'gender': teacher.gender,
                'age': teacher.age,
                'title': teacher.title,
                'phone': teacher.phone
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'更新教师信息失败: {str(e)}'}), 500

@admin_bp.route('/teachers/<teacher_id>', methods=['DELETE'])
@admin_required
def delete_teacher(teacher_id):
    """删除教师"""
    try:
        teacher = Teacher.query.get_or_404(teacher_id)
        
        # 检查是否有关联的课程开设
        if teacher.offerings:
            return jsonify({'message': '该教师有关联的课程开设记录，无法删除'}), 400
        
        db.session.delete(teacher)
        db.session.commit()
        
        return jsonify({'message': '教师删除成功'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'删除教师失败: {str(e)}'}), 500

# 学生管理
@admin_bp.route('/students', methods=['GET'])
@admin_required
def get_students():
    """获取学生列表"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        search = request.args.get('search', '')
        class_id = request.args.get('class_id', '')
        
        query = Student.query
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
            'current_page': students.page
        }), 200
    except Exception as e:
        return jsonify({'message': f'获取学生列表失败: {str(e)}'}), 500

@admin_bp.route('/students', methods=['POST'])
@admin_required
def create_student():
    """创建学生"""
    try:
        data = request.get_json()
        
        # 验证必填字段
        required_fields = ['student_id', 'name', 'gender', 'age', 'hometown', 'class_id', 'password']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'message': f'{field} 不能为空'}), 400
        
        # 检查学号是否已存在
        if Student.query.filter_by(student_id=data['student_id']).first():
            return jsonify({'message': '学号已存在'}), 400
        
        # 检查班级是否存在
        if not Class.query.filter_by(class_id=data['class_id']).first():
            return jsonify({'message': '班级不存在'}), 400
        
        # 创建学生
        student = Student(
            student_id=data['student_id'],
            name=data['name'],
            gender=data['gender'],
            age=data['age'],
            hometown=data['hometown'],
            class_id=data['class_id'],
            total_credits=0
        )
        student.set_password(data['password'])
        
        db.session.add(student)
        db.session.commit()
        
        return jsonify({
            'message': '学生创建成功',
            'student': {
                'student_id': student.student_id,
                'name': student.name,
                'gender': student.gender,
                'age': student.age,
                'hometown': student.hometown,
                'class_id': student.class_id,
                'total_credits': student.total_credits
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'创建学生失败: {str(e)}'}), 500

@admin_bp.route('/students/<student_id>', methods=['PUT'])
@admin_required
def update_student(student_id):
    """更新学生信息"""
    try:
        student = Student.query.get_or_404(student_id)
        data = request.get_json()
        
        # 更新字段
        if 'name' in data:
            student.name = data['name']
        if 'gender' in data:
            student.gender = data['gender']
        if 'age' in data:
            student.age = data['age']
        if 'hometown' in data:
            student.hometown = data['hometown']
        if 'class_id' in data:
            # 检查班级是否存在
            if not Class.query.filter_by(class_id=data['class_id']).first():
                return jsonify({'message': '班级不存在'}), 400
            student.class_id = data['class_id']
        if 'password' in data and data['password']:
            student.set_password(data['password'])
        
        db.session.commit()
        
        return jsonify({
            'message': '学生信息更新成功',
            'student': {
                'student_id': student.student_id,
                'name': student.name,
                'gender': student.gender,
                'age': student.age,
                'hometown': student.hometown,
                'class_id': student.class_id,
                'total_credits': student.total_credits
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'更新学生信息失败: {str(e)}'}), 500

@admin_bp.route('/students/<student_id>', methods=['DELETE'])
@admin_required
def delete_student(student_id):
    """删除学生"""
    try:
        student = Student.query.get_or_404(student_id)
        
        # 删除学生会自动删除关联的选课记录（cascade设置）
        db.session.delete(student)
        db.session.commit()
        
        return jsonify({'message': '学生删除成功'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'删除学生失败: {str(e)}'}), 500

# 课程管理
@admin_bp.route('/courses', methods=['GET'])
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
                'exam_type': '考试' if c.exam_type else '考查',
                'credits': c.credits,
                'created_at': c.created_at.isoformat() if c.created_at else None
            } for c in courses.items],
            'total': courses.total,
            'pages': courses.pages,
            'current_page': courses.page
        }), 200
    except Exception as e:
        return jsonify({'message': f'获取课程列表失败: {str(e)}'}), 500

@admin_bp.route('/courses', methods=['POST'])
@admin_required
def create_course():
    """创建课程"""
    try:
        data = request.get_json()
        
        # 验证必填字段
        required_fields = ['course_id', 'course_name', 'hours', 'exam_type', 'credits']
        for field in required_fields:
            if data.get(field) is None:
                return jsonify({'message': f'{field} 不能为空'}), 400
        
        # 检查课程编号是否已存在
        if Course.query.filter_by(course_id=data['course_id']).first():
            return jsonify({'message': '课程编号已存在'}), 400
        
        # 创建课程
        course = Course(
            course_id=data['course_id'],
            course_name=data['course_name'],
            hours=data['hours'],
            exam_type=bool(data['exam_type']),
            credits=float(data['credits'])
        )
        
        db.session.add(course)
        db.session.commit()
        
        return jsonify({
            'message': '课程创建成功',
            'course': {
                'course_id': course.course_id,
                'course_name': course.course_name,
                'hours': course.hours,
                'exam_type': course.exam_type,
                'credits': course.credits
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'创建课程失败: {str(e)}'}), 500

@admin_bp.route('/courses/<course_id>', methods=['PUT'])
@admin_required
def update_course(course_id):
    """更新课程信息"""
    try:
        course = Course.query.get_or_404(course_id)
        data = request.get_json()
        
        # 更新字段
        if 'course_name' in data:
            course.course_name = data['course_name']
        if 'hours' in data:
            course.hours = data['hours']
        if 'exam_type' in data:
            course.exam_type = bool(data['exam_type'])
        if 'credits' in data:
            course.credits = float(data['credits'])
        
        db.session.commit()
        
        return jsonify({
            'message': '课程信息更新成功',
            'course': {
                'course_id': course.course_id,
                'course_name': course.course_name,
                'hours': course.hours,
                'exam_type': course.exam_type,
                'credits': course.credits
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'更新课程信息失败: {str(e)}'}), 500

@admin_bp.route('/courses/<course_id>', methods=['DELETE'])
@admin_required
def delete_course(course_id):
    """删除课程"""
    try:
        course = Course.query.get_or_404(course_id)
        
        # 检查是否有关联的课程开设
        if course.offerings:
            return jsonify({'message': '该课程有关联的开设记录，无法删除'}), 400
        
        db.session.delete(course)
        db.session.commit()
        
        return jsonify({'message': '课程删除成功'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'删除课程失败: {str(e)}'}), 500

# 班级管理
@admin_bp.route('/classes', methods=['GET'])
@admin_required
def get_classes():
    """获取班级列表"""
    try:
        classes = Class.query.all()
        return jsonify([{
            'class_id': c.class_id,
            'class_name': c.class_name,
            'description': getattr(c, 'description', ''),
            'student_count': len(c.students),
            'created_at': c.created_at.isoformat() if c.created_at else None
        } for c in classes]), 200
    except Exception as e:
        return jsonify({'message': f'获取班级列表失败: {str(e)}'}), 500

@admin_bp.route('/classes', methods=['POST'])
@admin_required
def create_class():
    """创建班级"""
    try:
        data = request.get_json()
        
        # 验证必填字段
        if not data.get('class_id') or not data.get('class_name'):
            return jsonify({'message': '班级编号和班级名称不能为空'}), 400
        
        # 检查班级编号是否已存在
        if Class.query.filter_by(class_id=data['class_id']).first():
            return jsonify({'message': '班级编号已存在'}), 400
        
        # 创建班级
        class_obj = Class(
            class_id=data['class_id'],
            class_name=data['class_name']
        )
        
        db.session.add(class_obj)
        db.session.commit()
        
        return jsonify({
            'message': '班级创建成功',
            'class': {
                'class_id': class_obj.class_id,
                'class_name': class_obj.class_name
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'创建班级失败: {str(e)}'}), 500

@admin_bp.route('/classes/<class_id>', methods=['PUT'])
@admin_required
def update_class(class_id):
    """更新班级信息"""
    try:
        class_obj = Class.query.get_or_404(class_id)
        data = request.get_json()
        
        # 更新字段
        if 'class_name' in data:
            class_obj.class_name = data['class_name']
        
        db.session.commit()
        
        return jsonify({
            'message': '班级信息更新成功',
            'class': {
                'class_id': class_obj.class_id,
                'class_name': class_obj.class_name
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'更新班级信息失败: {str(e)}'}), 500

@admin_bp.route('/classes/<class_id>', methods=['DELETE'])
@admin_required
def delete_class(class_id):
    """删除班级"""
    try:
        class_obj = Class.query.get_or_404(class_id)
        
        # 检查是否有学生
        if class_obj.students:
            return jsonify({'message': '该班级还有学生，无法删除'}), 400
        
        db.session.delete(class_obj)
        db.session.commit()
        
        return jsonify({'message': '班级删除成功'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'删除班级失败: {str(e)}'}), 500

@admin_bp.route('/classes/<class_id>/students', methods=['GET'])
@admin_required
def get_class_students(class_id):
    """获取班级学生列表"""
    try:
        class_obj = Class.query.get_or_404(class_id)
        students = Student.query.filter_by(class_id=class_id).all()
        
        return jsonify([{
            'student_id': s.student_id,
            'name': s.name,
            'gender': s.gender,
            'age': s.age,
            'hometown': s.hometown,
            'total_credits': s.total_credits
        } for s in students]), 200
    except Exception as e:
        return jsonify({'message': f'获取班级学生失败: {str(e)}'}), 500

# 统计信息
@admin_bp.route('/statistics', methods=['GET'])
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

# 统计分析
@admin_bp.route('/statistics/overview', methods=['GET'])
@admin_required
def get_system_statistics():
    """获取系统总体统计信息"""
    try:
        academic_year = request.args.get('academic_year', '2024')
        semester = request.args.get('semester', type=int)
        
        # 获取课程选课统计
        course_stats = CourseStatisticsService.get_course_enrollment_statistics(
            academic_year, semester
        )
        
        # 获取热门课程
        popular_courses = CourseStatisticsService.get_popular_courses(
            academic_year, semester, limit=5
        )
        
        # 获取时间冲突分析
        conflict_analysis = CourseStatisticsService.get_time_conflict_analysis(
            academic_year, semester
        )
        
        # 基本统计
        total_students = Student.query.count()
        total_teachers = Teacher.query.count()
        total_courses = Course.query.count()
        total_classes = Class.query.count()
        
        return jsonify({
            'basic_stats': {
                'total_students': total_students,
                'total_teachers': total_teachers,
                'total_courses': total_courses,
                'total_classes': total_classes
            },
            'course_stats': course_stats,
            'popular_courses': popular_courses,
            'conflict_analysis': conflict_analysis
        }), 200
    except Exception as e:
        return jsonify({'message': f'获取统计信息失败: {str(e)}'}), 500

@admin_bp.route('/statistics/courses', methods=['GET'])
@admin_required
def get_course_statistics():
    """获取课程详细统计信息"""
    try:
        academic_year = request.args.get('academic_year', '2024')
        semester = request.args.get('semester', type=int)
        
        course_stats = CourseStatisticsService.get_course_enrollment_statistics(
            academic_year, semester
        )
        
        popular_courses = CourseStatisticsService.get_popular_courses(
            academic_year, semester
        )
        
        return jsonify({
            'statistics': course_stats,
            'popular_courses': popular_courses
        }), 200
    except Exception as e:
        return jsonify({'message': f'获取课程统计失败: {str(e)}'}), 500

# 数据库初始化
@admin_bp.route('/init-data', methods=['POST'])
def init_database_data():
    """初始化数据库数据"""
    try:
        # 清空现有数据
        db.drop_all()
        db.create_all()
        
        # 创建管理员
        admin = Admin(
            admin_id='admin001',
            username='admin',
            name='系统管理员'
        )
        admin.set_password('123456')
        db.session.add(admin)
        
        # 创建班级
        classes = [
            Class(class_id='CS01', class_name='计算机科学与技术1班'),
            Class(class_id='CS02', class_name='计算机科学与技术2班'),
            Class(class_id='SE01', class_name='软件工程1班'),
        ]
        db.session.add_all(classes)
        
        # 创建课程
        courses = [
            Course(course_id='CS101', course_name='数据结构', hours=64, exam_type=True, credits=4.0),
            Course(course_id='CS102', course_name='算法设计与分析', hours=48, exam_type=True, credits=3.0),
            Course(course_id='CS103', course_name='数据库原理', hours=64, exam_type=True, credits=4.0),
            Course(course_id='CS104', course_name='计算机网络', hours=48, exam_type=True, credits=3.0),
            Course(course_id='CS105', course_name='软件工程', hours=48, exam_type=False, credits=3.0),
        ]
        db.session.add_all(courses)
        
        # 创建教师
        teachers = [
            Teacher(teacher_id='T001', name='张教授', gender='男', age=45, title='教授', phone='13800138001'),
            Teacher(teacher_id='T002', name='李副教授', gender='女', age=38, title='副教授', phone='13800138002'),
            Teacher(teacher_id='T003', name='王讲师', gender='男', age=32, title='讲师', phone='13800138003'),
            Teacher(teacher_id='T004', name='赵博士', gender='女', age=35, title='讲师', phone='13800138004'),
        ]
        for teacher in teachers:
            teacher.set_password('123456')
        db.session.add_all(teachers)
        
        # 创建学生
        students = [
            Student(student_id='2021001001', name='张三', gender='男', age=20, hometown='北京', class_id='CS01'),
            Student(student_id='2021001002', name='李四', gender='女', age=19, hometown='上海', class_id='CS01'),
            Student(student_id='2021001003', name='王五', gender='男', age=20, hometown='广州', class_id='CS02'),
            Student(student_id='2021001004', name='赵六', gender='女', age=19, hometown='深圳', class_id='CS02'),
            Student(student_id='2021001005', name='钱七', gender='男', age=20, hometown='杭州', class_id='SE01'),
        ]
        for student in students:
            student.set_password('123456')
        db.session.add_all(students)
        
        db.session.commit()
        
        return jsonify({
            'message': '数据初始化成功',
            'data': {
                'admin_count': 1,
                'class_count': 3,
                'course_count': 5,
                'teacher_count': 4,
                'student_count': 5
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'数据初始化失败: {str(e)}'}), 500
