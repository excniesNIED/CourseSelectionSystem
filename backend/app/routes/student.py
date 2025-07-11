from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app import db
from app.models import Student, Course, CourseOffering, Enrollment, Teacher
from app.services.student_service import StudentService
from app.services.exceptions import ServiceError
from app.services.statistics_service import CourseStatisticsService
from sqlalchemy import and_, func, desc

student_bp = Blueprint('student', __name__)

def student_required(f):
    """学生权限装饰器"""
    def decorated_function(*args, **kwargs):
        try:
            claims = get_jwt()
            if claims.get('type') != 'student':
                return jsonify({'message': '需要学生权限'}), 403
            return f(*args, **kwargs)
        except Exception as e:
            return jsonify({'message': '身份验证失败'}), 401
    decorated_function.__name__ = f.__name__
    return decorated_function

@student_bp.route('/profile', methods=['GET'])
@jwt_required()
@student_required
def get_profile():
    """查看个人信息"""
    student_id = get_jwt_identity()
    
    try:
        student = Student.query.filter_by(student_id=student_id).first()
        if not student:
            return jsonify({'message': '学生不存在'}), 404
        
        return jsonify({
            'student_id': student.student_id,
            'name': student.name,
            'gender': student.gender,
            'age': student.age,
            'hometown': student.hometown,
            'total_credits': student.total_credits,
            'class_id': student.class_id,
            'class_name': student.class_info.class_name if student.class_info else ''
        }), 200
    except Exception as e:
        return jsonify({'message': f'获取个人信息失败: {str(e)}'}), 500

@student_bp.route('/courses', methods=['GET'])
@jwt_required()
@student_required
def get_my_courses():
    """查看本人课程"""
    student_id = get_jwt_identity()
    
    try:
        academic_year = request.args.get('academic_year', '')
        semester = request.args.get('semester', '', type=int)
        
        query = db.session.query(
            Enrollment, CourseOffering, Course, Teacher
        ).join(CourseOffering, Enrollment.offering_id == CourseOffering.offering_id)\
         .join(Course, CourseOffering.course_id == Course.course_id)\
         .join(Teacher, CourseOffering.teacher_id == Teacher.teacher_id)\
         .filter(Enrollment.student_id == student_id)
        
        if academic_year:
            query = query.filter(CourseOffering.academic_year == academic_year)
        if semester in [0, 1]:
            query = query.filter(CourseOffering.semester == bool(semester))
        
        enrollments = query.all()
        
        result = []
        for enrollment, offering, course, teacher in enrollments:
            result.append({
                'offering_id': offering.offering_id,
                'course_id': course.course_id,
                'course_name': course.course_name,
                'teacher_id': teacher.teacher_id,
                'teacher_name': teacher.name,
                'teacher_title': teacher.title,
                'hours': course.hours,
                'credits': course.credits,
                'exam_type': course.exam_type,
                'academic_year': offering.academic_year,
                'semester': offering.semester,
                'score': enrollment.score,
                'enrollment_date': enrollment.enrollment_date.isoformat() if enrollment.enrollment_date else None
            })
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'message': f'获取课程信息失败: {str(e)}'}), 500

@student_bp.route('/courses/available', methods=['GET'])
@jwt_required()
@student_required
def get_available_courses():
    """获取可选课程列表"""
    student_id = get_jwt_identity()
    
    try:
        academic_year = request.args.get('academic_year', '2024')
        semester = request.args.get('semester', 1, type=int)
        
        # 查询所有开课
        all_offerings = db.session.query(
            CourseOffering, Course, Teacher
        ).join(Course).join(Teacher).filter(
            CourseOffering.academic_year == academic_year,
            CourseOffering.semester == bool(semester)
        ).all()
        
        # 查询学生已选课程
        enrolled_offerings = db.session.query(
            Enrollment.offering_id
        ).filter_by(student_id=student_id).all()
        enrolled_ids = [e[0] for e in enrolled_offerings]
        
        # 查询学生已选的课程ID（防止选择同一门课的不同教师）
        enrolled_courses = db.session.query(
            CourseOffering.course_id
        ).join(Enrollment).filter(
            Enrollment.student_id == student_id
        ).all()
        enrolled_course_ids = [c[0] for c in enrolled_courses]
        
        result = []
        for offering, course, teacher in all_offerings:
            # 跳过已选的开课
            if offering.offering_id in enrolled_ids:
                continue
            
            # 跳过已选过的同一门课程
            if course.course_id in enrolled_course_ids:
                continue
            
            # 检查是否还有名额
            available = offering.current_students < offering.max_students
            
            result.append({
                'offering_id': offering.offering_id,
                'course_id': course.course_id,
                'course_name': course.course_name,
                'teacher_id': teacher.teacher_id,
                'teacher_name': teacher.name,
                'teacher_title': teacher.title,
                'hours': course.hours,
                'credits': course.credits,
                'exam_type': course.exam_type,
                'max_students': offering.max_students,
                'current_students': offering.current_students,
                'available': available
            })
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'message': f'获取可选课程失败: {str(e)}'}), 500

@student_bp.route('/courses/<offering_id>/enroll', methods=['POST'])
@jwt_required()
@student_required
def enroll_course(offering_id):
    """选课"""
    student_id = get_jwt_identity()
    
    try:
        result = StudentService.enroll_in_course(student_id, offering_id)
        return jsonify(result), 201
    except ServiceError as e:
        return jsonify({'message': e.message}), e.code
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'选课失败: {str(e)}'}), 500

@student_bp.route('/courses/<offering_id>/drop', methods=['DELETE'])
@jwt_required()
@student_required
def drop_course(offering_id):
    """退选"""
    student_id = get_jwt_identity()
    
    try:
        result = StudentService.drop_course(student_id, offering_id)
        return jsonify(result), 200
    except ServiceError as e:
        return jsonify({'message': e.message}), e.code
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'退选失败: {str(e)}'}), 500

@student_bp.route('/scores', methods=['GET'])
@jwt_required()
@student_required
def get_scores():
    """按学年查询考试成绩"""
    student_id = get_jwt_identity()
    
    try:
        academic_year = request.args.get('academic_year', '')
        semester = request.args.get('semester', '', type=int)

        query = db.session.query(
            Enrollment.score,
            Course.course_name,
            Course.credits,
            Course.exam_type,
            Teacher.name.label('teacher_name'),
            CourseOffering.academic_year,
            CourseOffering.semester
        ).join(CourseOffering, Enrollment.offering_id == CourseOffering.offering_id)\
         .join(Course, CourseOffering.course_id == Course.course_id)\
         .join(Teacher, CourseOffering.teacher_id == Teacher.teacher_id)\
         .filter(
            Enrollment.student_id == student_id,
            Enrollment.score.isnot(None)
        )

        if academic_year:
            query = query.filter(CourseOffering.academic_year == academic_year)
        if semester in [0, 1]:
            query = query.filter(CourseOffering.semester == bool(semester))
        
        enrollments = query.order_by(
            CourseOffering.academic_year.desc(),
            CourseOffering.semester.desc()
        ).all()
        
        result = []
        total_credits = 0
        total_score_credits = 0
        
        for enrollment in enrollments:
            score_data = {
                'offering_id': enrollment.offering_id,
                'course_id': enrollment.course_id,
                'course_name': enrollment.course_name,
                'teacher_name': enrollment.teacher_name,
                'academic_year': enrollment.academic_year,
                'semester': enrollment.semester,
                'credits': enrollment.credits,
                'score': enrollment.score,
                'exam_type': enrollment.exam_type,
                'passed': enrollment.score >= 60
            }
            result.append(score_data)
            
            # 计算GPA相关数据
            if enrollment.score >= 60:
                total_credits += enrollment.credits
                total_score_credits += enrollment.score * enrollment.credits
        
        # 计算加权平均分
        gpa = total_score_credits / total_credits if total_credits > 0 else 0
        
        # 按学年学期分组
        grouped_scores = {}
        for score in result:
            key = f"{score['academic_year']}-{score['semester']}"
            if key not in grouped_scores:
                grouped_scores[key] = {
                    'academic_year': score['academic_year'],
                    'semester': score['semester'],
                    'courses': [],
                    'semester_credits': 0,
                    'semester_gpa': 0
                }
            grouped_scores[key]['courses'].append(score)
        
        # 计算每学期GPA
        for semester_data in grouped_scores.values():
            semester_credits = 0
            semester_score_credits = 0
            for course in semester_data['courses']:
                if course['passed']:
                    semester_credits += course['credits']
                    semester_score_credits += course['score'] * course['credits']
            
            semester_data['semester_credits'] = semester_credits
            semester_data['semester_gpa'] = round(
                semester_score_credits / semester_credits if semester_credits > 0 else 0, 2
            )
        
        return jsonify({
            'total_credits': total_credits,
            'overall_gpa': round(gpa, 2),
            'semesters': list(grouped_scores.values()),
            'all_scores': result
        }), 200
    except Exception as e:
        return jsonify({'message': f'获取成绩信息失败: {str(e)}'}), 500

@student_bp.route('/statistics', methods=['GET'])
@jwt_required()
@student_required
def get_student_statistics():
    """获取学生统计信息"""
    student_id = get_jwt_identity()
    
    try:
        stats = CourseStatisticsService.get_student_course_statistics(student_id)
        return jsonify(stats), 200
    except Exception as e:
        return jsonify({'message': f'获取学生统计信息失败: {str(e)}'}), 500

@student_bp.route('/schedule', methods=['GET'])
@jwt_required()
@student_required
def get_schedule():
    """获取学生课表"""
    student_id = get_jwt_identity()
    
    try:
        schedule = StudentService.get_student_schedule(student_id)
        return jsonify(schedule), 200
    except ServiceError as e:
        return jsonify({'message': e.message}), e.code
    except Exception as e:
        return jsonify({'message': f'获取课表失败: {str(e)}'}), 500
