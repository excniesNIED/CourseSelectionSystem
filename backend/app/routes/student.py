from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app import db
from app.models import Student, Course, CourseOffering, Enrollment, Teacher
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
        # 检查开课是否存在
        offering = CourseOffering.query.filter_by(offering_id=offering_id).first()
        if not offering:
            return jsonify({'message': '开课不存在'}), 404
        
        # 检查是否已经选过这门课
        existing_enrollment = Enrollment.query.filter_by(
            offering_id=offering_id,
            student_id=student_id
        ).first()
        if existing_enrollment:
            return jsonify({'message': '已经选过这门课'}), 400
        
        # 检查是否选过同一门课程的其他班级
        same_course_enrollment = db.session.query(Enrollment).join(CourseOffering).filter(
            CourseOffering.course_id == offering.course_id,
            Enrollment.student_id == student_id
        ).first()
        if same_course_enrollment:
            return jsonify({'message': '已经选过此课程的其他班级'}), 400
        
        # 检查是否还有名额
        if offering.current_students >= offering.max_students:
            return jsonify({'message': '课程人数已满'}), 400
        
        # 创建选课记录
        enrollment = Enrollment(
            offering_id=offering_id,
            student_id=student_id
        )
        
        # 更新当前选课人数
        offering.current_students += 1
        
        db.session.add(enrollment)
        db.session.commit()
        
        return jsonify({'message': '选课成功'}), 201
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
        # 查找选课记录
        enrollment = Enrollment.query.filter_by(
            offering_id=offering_id,
            student_id=student_id
        ).first()
        
        if not enrollment:
            return jsonify({'message': '未选择此课程'}), 404
        
        # 检查是否已有成绩
        if enrollment.score is not None:
            return jsonify({'message': '已有成绩，无法退选'}), 400
        
        # 获取开课信息
        offering = CourseOffering.query.filter_by(offering_id=offering_id).first()
        if offering:
            offering.current_students = max(0, offering.current_students - 1)
        
        # 删除选课记录
        db.session.delete(enrollment)
        db.session.commit()
        
        return jsonify({'message': '退选成功'}), 200
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
        student = Student.query.filter_by(student_id=student_id).first()
        if not student:
            return jsonify({'message': '学生不存在'}), 404
        
        # 统计选课数量
        total_enrollments = Enrollment.query.filter_by(student_id=student_id).count()
        
        # 统计有成绩的课程数量
        graded_courses = Enrollment.query.filter(
            Enrollment.student_id == student_id,
            Enrollment.score.isnot(None)
        ).count()
        
        # 统计及格课程数量
        passed_courses = Enrollment.query.filter(
            Enrollment.student_id == student_id,
            Enrollment.score >= 60
        ).count()
        
        # 计算平均分
        avg_score_result = db.session.query(
            func.avg(Enrollment.score)
        ).filter(
            Enrollment.student_id == student_id,
            Enrollment.score.isnot(None)
        ).scalar()
        
        avg_score = round(avg_score_result, 2) if avg_score_result else 0
        
        return jsonify({
            'total_credits': student.total_credits,
            'total_enrollments': total_enrollments,
            'graded_courses': graded_courses,
            'passed_courses': passed_courses,
            'failed_courses': graded_courses - passed_courses,
            'avg_score': avg_score,
            'pass_rate': round(passed_courses / graded_courses * 100, 2) if graded_courses > 0 else 0
        }), 200
    except Exception as e:
        return jsonify({'message': f'获取统计信息失败: {str(e)}'}), 500
