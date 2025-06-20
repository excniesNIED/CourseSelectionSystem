from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import Teacher, Course, CourseOffering, Enrollment, Student, Class
from sqlalchemy import func, desc, and_

teacher_bp = Blueprint('teacher', __name__)

def teacher_required(f):
    """教师权限装饰器"""
    def decorated_function(*args, **kwargs):
        current_user = get_jwt_identity()
        if current_user['type'] != 'teacher':
            return jsonify({'message': '权限不足，需要教师权限'}), 403
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@teacher_bp.route('/profile', methods=['GET'])
@jwt_required()
@teacher_required
def get_profile():
    """获取个人信息"""
    current_user = get_jwt_identity()
    teacher_id = current_user['id']
    
    try:
        teacher = Teacher.query.filter_by(teacher_id=teacher_id).first()
        if not teacher:
            return jsonify({'message': '教师不存在'}), 404
        
        return jsonify({
            'teacher_id': teacher.teacher_id,
            'name': teacher.name,
            'gender': teacher.gender,
            'age': teacher.age,
            'title': teacher.title,
            'phone': teacher.phone
        }), 200
    except Exception as e:
        return jsonify({'message': f'获取个人信息失败: {str(e)}'}), 500

@teacher_bp.route('/courses', methods=['GET'])
@jwt_required()
@teacher_required
def get_my_courses():
    """查看任课信息"""
    current_user = get_jwt_identity()
    teacher_id = current_user['id']
    
    try:
        academic_year = request.args.get('academic_year', '')
        semester = request.args.get('semester', '', type=int)
        
        query = CourseOffering.query.filter_by(teacher_id=teacher_id).join(Course)
        
        if academic_year:
            query = query.filter(CourseOffering.academic_year == academic_year)
        if semester in [0, 1]:
            query = query.filter(CourseOffering.semester == bool(semester))
        
        offerings = query.all()
        
        return jsonify([{
            'offering_id': o.offering_id,
            'course_id': o.course_id,
            'course_name': o.course.course_name,
            'hours': o.course.hours,
            'credits': o.course.credits,
            'academic_year': o.academic_year,
            'semester': o.semester,
            'max_students': o.max_students,
            'current_students': o.current_students,
            'exam_type': o.course.exam_type
        } for o in offerings]), 200
    except Exception as e:
        return jsonify({'message': f'获取任课信息失败: {str(e)}'}), 500

@teacher_bp.route('/courses', methods=['POST'])
@jwt_required()
@teacher_required
def create_course_offering():
    """开设课程"""
    current_user = get_jwt_identity()
    teacher_id = current_user['id']
    
    data = request.get_json()
    required_fields = ['course_id', 'academic_year', 'semester', 'max_students']
    
    if not all(field in data for field in required_fields):
        return jsonify({'message': '所有字段都是必填的'}), 400
    
    try:
        # 检查课程是否存在
        course = Course.query.filter_by(course_id=data['course_id']).first()
        if not course:
            return jsonify({'message': '课程不存在'}), 400
        
        # 生成开课编号
        offering_id = f"{data['academic_year']}-{data['semester']}-{data['course_id']}-{teacher_id}"
        
        # 检查是否已经开设过相同的课程
        if CourseOffering.query.filter_by(offering_id=offering_id).first():
            return jsonify({'message': '该学期已开设此课程'}), 400
        
        offering = CourseOffering(
            offering_id=offering_id,
            course_id=data['course_id'],
            teacher_id=teacher_id,
            academic_year=data['academic_year'],
            semester=bool(data['semester']),
            max_students=data['max_students']
        )
        
        db.session.add(offering)
        db.session.commit()
        
        return jsonify({'message': '课程开设成功'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'开设课程失败: {str(e)}'}), 500

@teacher_bp.route('/courses/<offering_id>', methods=['DELETE'])
@jwt_required()
@teacher_required
def cancel_course_offering(offering_id):
    """取消开课"""
    current_user = get_jwt_identity()
    teacher_id = current_user['id']
    
    try:
        offering = CourseOffering.query.filter_by(
            offering_id=offering_id, 
            teacher_id=teacher_id
        ).first()
        
        if not offering:
            return jsonify({'message': '开课记录不存在或无权限'}), 404
        
        # 检查是否有学生选课
        if offering.current_students > 0:
            return jsonify({'message': '已有学生选课，无法取消'}), 400
        
        db.session.delete(offering)
        db.session.commit()
        
        return jsonify({'message': '课程取消成功'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'取消课程失败: {str(e)}'}), 500

@teacher_bp.route('/students/class/<class_id>', methods=['GET'])
@jwt_required()
@teacher_required
def get_class_students_ranking():
    """按行政班级查看学生均绩及排名"""
    try:
        class_info = Class.query.filter_by(class_id=class_id).first()
        if not class_info:
            return jsonify({'message': '班级不存在'}), 404
        
        # 查询班级学生及其平均成绩
        students_with_avg = db.session.query(
            Student,
            func.avg(Enrollment.score).label('avg_score'),
            func.count(Enrollment.score).label('course_count')
        ).outerjoin(Enrollment).filter(
            Student.class_id == class_id,
            Enrollment.score.isnot(None)
        ).group_by(Student.student_id).all()
        
        # 处理没有成绩的学生
        all_students = Student.query.filter_by(class_id=class_id).all()
        student_scores = {s.student_id: {'avg_score': avg or 0, 'course_count': count or 0} 
                         for s, avg, count in students_with_avg}
        
        result = []
        for student in all_students:
            score_info = student_scores.get(student.student_id, {'avg_score': 0, 'course_count': 0})
            result.append({
                'student_id': student.student_id,
                'name': student.name,
                'gender': student.gender,
                'total_credits': student.total_credits,
                'avg_score': round(score_info['avg_score'], 2) if score_info['avg_score'] else 0,
                'course_count': score_info['course_count']
            })
        
        # 按平均成绩排序
        result.sort(key=lambda x: x['avg_score'], reverse=True)
        
        # 添加排名
        for i, student in enumerate(result):
            student['rank'] = i + 1
        
        return jsonify({
            'class_id': class_id,
            'class_name': class_info.class_name,
            'students': result
        }), 200
    except Exception as e:
        return jsonify({'message': f'获取班级学生排名失败: {str(e)}'}), 500

@teacher_bp.route('/courses/<offering_id>/students', methods=['GET'])
@jwt_required()
@teacher_required
def get_course_students():
    """按任课课程查询学生单门成绩及排名"""
    current_user = get_jwt_identity()
    teacher_id = current_user['id']
    
    try:
        offering = CourseOffering.query.filter_by(
            offering_id=offering_id,
            teacher_id=teacher_id
        ).first()
        
        if not offering:
            return jsonify({'message': '开课记录不存在或无权限'}), 404
        
        # 查询选课学生及成绩
        enrollments = db.session.query(
            Enrollment, Student, Class
        ).join(Student).join(Class).filter(
            Enrollment.offering_id == offering_id
        ).order_by(desc(Enrollment.score)).all()
        
        result = []
        for i, (enrollment, student, class_info) in enumerate(enrollments):
            result.append({
                'rank': i + 1 if enrollment.score else None,
                'student_id': student.student_id,
                'name': student.name,
                'class_id': student.class_id,
                'class_name': class_info.class_name,
                'score': enrollment.score,
                'enrollment_date': enrollment.enrollment_date.isoformat() if enrollment.enrollment_date else None
            })
        
        return jsonify({
            'offering_id': offering_id,
            'course_name': offering.course.course_name,
            'academic_year': offering.academic_year,
            'semester': offering.semester,
            'total_students': len(result),
            'students': result
        }), 200
    except Exception as e:
        return jsonify({'message': f'获取课程学生信息失败: {str(e)}'}), 500

@teacher_bp.route('/courses/<offering_id>/scores', methods=['PUT'])
@jwt_required()
@teacher_required
def update_scores():
    """录入/修改学生成绩"""
    current_user = get_jwt_identity()
    teacher_id = current_user['id']
    
    data = request.get_json()
    if not data or 'scores' not in data:
        return jsonify({'message': '成绩数据不能为空'}), 400
    
    try:
        offering = CourseOffering.query.filter_by(
            offering_id=offering_id,
            teacher_id=teacher_id
        ).first()
        
        if not offering:
            return jsonify({'message': '开课记录不存在或无权限'}), 404
        
        # 批量更新成绩
        for score_data in data['scores']:
            if 'student_id' not in score_data or 'score' not in score_data:
                continue
            
            enrollment = Enrollment.query.filter_by(
                offering_id=offering_id,
                student_id=score_data['student_id']
            ).first()
            
            if enrollment:
                old_score = enrollment.score
                enrollment.score = score_data['score']
                
                # 如果是新及格的成绩，更新学生总学分
                if old_score is None or old_score < 60:
                    if score_data['score'] >= 60:
                        student = Student.query.filter_by(student_id=score_data['student_id']).first()
                        if student:
                            student.total_credits += offering.course.credits
                # 如果从及格变为不及格，减少学分
                elif old_score >= 60 and score_data['score'] < 60:
                    student = Student.query.filter_by(student_id=score_data['student_id']).first()
                    if student:
                        student.total_credits -= offering.course.credits
        
        db.session.commit()
        return jsonify({'message': '成绩录入成功'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'录入成绩失败: {str(e)}'}), 500

@teacher_bp.route('/statistics/courses', methods=['GET'])
@jwt_required()
@teacher_required
def get_course_statistics():
    """按学年查询个人教授课程的平均成绩"""
    current_user = get_jwt_identity()
    teacher_id = current_user['id']
    
    try:
        academic_year = request.args.get('academic_year', '')
        
        query = db.session.query(
            CourseOffering,
            Course,
            func.avg(Enrollment.score).label('avg_score'),
            func.count(Enrollment.score).label('student_count')
        ).join(Course).outerjoin(Enrollment).filter(
            CourseOffering.teacher_id == teacher_id,
            Enrollment.score.isnot(None)
        )
        
        if academic_year:
            query = query.filter(CourseOffering.academic_year == academic_year)
        
        results = query.group_by(CourseOffering.offering_id).all()
        
        course_stats = []
        for offering, course, avg_score, student_count in results:
            course_stats.append({
                'offering_id': offering.offering_id,
                'course_id': course.course_id,
                'course_name': course.course_name,
                'academic_year': offering.academic_year,
                'semester': offering.semester,
                'avg_score': round(avg_score, 2) if avg_score else 0,
                'student_count': student_count or 0
            })
        
        # 计算总平均分
        total_avg = sum(stat['avg_score'] for stat in course_stats) / len(course_stats) if course_stats else 0
        
        return jsonify({
            'academic_year': academic_year or '所有学年',
            'total_avg_score': round(total_avg, 2),
            'course_count': len(course_stats),
            'courses': course_stats
        }), 200
    except Exception as e:
        return jsonify({'message': f'获取课程统计失败: {str(e)}'}), 500
