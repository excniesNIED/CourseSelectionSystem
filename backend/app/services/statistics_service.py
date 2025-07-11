"""
课程统计服务
提供课程相关的统计数据和分析功能
"""
from sqlalchemy import func, and_, desc
from app import db
from app.models import Course, CourseOffering, Enrollment, Student, Teacher, Class


class CourseStatisticsService:
    """课程统计服务类"""
    
    @staticmethod
    def get_course_enrollment_statistics(academic_year=None, semester=None):
        """
        获取课程选课统计信息
        
        Args:
            academic_year: 学年 (可选)
            semester: 学期 (可选)
            
        Returns:
            dict: 包含各种统计数据的字典
        """
        query = db.session.query(CourseOffering)
        
        if academic_year:
            query = query.filter(CourseOffering.academic_year == academic_year)
        if semester is not None:
            query = query.filter(CourseOffering.semester == bool(semester))
            
        offerings = query.all()
        
        total_offerings = len(offerings)
        total_capacity = sum(offering.max_students for offering in offerings)
        total_enrolled = sum(offering.current_students for offering in offerings)
        
        # 计算课程状态分布
        full_courses = sum(1 for offering in offerings if offering.current_students >= offering.max_students)
        available_courses = total_offerings - full_courses
        
        # 计算平均选课率
        avg_enrollment_rate = (total_enrolled / total_capacity * 100) if total_capacity > 0 else 0
        
        return {
            'total_offerings': total_offerings,
            'total_capacity': total_capacity,
            'total_enrolled': total_enrolled,
            'full_courses': full_courses,
            'available_courses': available_courses,
            'avg_enrollment_rate': round(avg_enrollment_rate, 2)
        }
    
    @staticmethod
    def get_popular_courses(academic_year=None, semester=None, limit=10):
        """
        获取热门课程列表 (按选课人数排序)
        
        Args:
            academic_year: 学年 (可选)
            semester: 学期 (可选)
            limit: 返回课程数量限制
            
        Returns:
            list: 热门课程列表
        """
        query = db.session.query(
            CourseOffering,
            Course,
            Teacher
        ).join(Course).join(Teacher)
        
        if academic_year:
            query = query.filter(CourseOffering.academic_year == academic_year)
        if semester is not None:
            query = query.filter(CourseOffering.semester == bool(semester))
            
        offerings = query.order_by(desc(CourseOffering.current_students)).limit(limit).all()
        
        result = []
        for offering, course, teacher in offerings:
            enrollment_rate = (offering.current_students / offering.max_students * 100) if offering.max_students > 0 else 0
            
            result.append({
                'offering_id': offering.offering_id,
                'course_id': course.course_id,
                'course_name': course.course_name,
                'teacher_name': teacher.name,
                'teacher_title': teacher.title,
                'current_students': offering.current_students,
                'max_students': offering.max_students,
                'enrollment_rate': round(enrollment_rate, 2),
                'academic_year': offering.academic_year,
                'semester': offering.semester
            })
            
        return result
    
    @staticmethod
    def get_teacher_course_statistics(teacher_id, academic_year=None, semester=None):
        """
        获取教师课程统计信息
        
        Args:
            teacher_id: 教师ID
            academic_year: 学年 (可选)
            semester: 学期 (可选)
            
        Returns:
            dict: 教师课程统计数据
        """
        query = db.session.query(CourseOffering).filter(CourseOffering.teacher_id == teacher_id)
        
        if academic_year:
            query = query.filter(CourseOffering.academic_year == academic_year)
        if semester is not None:
            query = query.filter(CourseOffering.semester == bool(semester))
            
        offerings = query.all()
        
        total_courses = len(offerings)
        total_students = sum(offering.current_students for offering in offerings)
        total_capacity = sum(offering.max_students for offering in offerings)
        
        # 计算已评分的学生数量
        scored_students = db.session.query(func.count(Enrollment.student_id)).join(CourseOffering).filter(
            CourseOffering.teacher_id == teacher_id,
            Enrollment.score.isnot(None)
        ).scalar() or 0
        
        # 计算平均成绩
        avg_score = db.session.query(func.avg(Enrollment.score)).join(CourseOffering).filter(
            CourseOffering.teacher_id == teacher_id,
            Enrollment.score.isnot(None)
        ).scalar() or 0
        
        return {
            'total_courses': total_courses,
            'total_students': total_students,
            'total_capacity': total_capacity,
            'scored_students': scored_students,
            'unscored_students': total_students - scored_students,
            'avg_score': round(float(avg_score), 2) if avg_score else 0,
            'avg_enrollment_rate': round((total_students / total_capacity * 100), 2) if total_capacity > 0 else 0
        }
    
    @staticmethod
    def get_student_course_statistics(student_id):
        """
        获取学生课程统计信息
        
        Args:
            student_id: 学生ID
            
        Returns:
            dict: 学生课程统计数据
        """
        # 查询学生所有选课记录
        enrollments = db.session.query(
            Enrollment, CourseOffering, Course
        ).join(CourseOffering, Enrollment.offering_id == CourseOffering.offering_id)\
         .join(Course, CourseOffering.course_id == Course.course_id)\
         .filter(Enrollment.student_id == student_id)\
         .all()
        
        total_enrollments = len(enrollments)
        total_credits = sum(course.credits for _, _, course in enrollments)
        
        # 计算已评分课程
        scored_enrollments = [e for e, _, _ in enrollments if e.score is not None]
        scored_credits = sum(course.credits for enrollment, _, course in enrollments if enrollment.score is not None)
        
        # 计算平均分
        if scored_enrollments:
            # 按学分加权计算平均分
            weighted_score_sum = sum(
                enrollment.score * course.credits 
                for enrollment, _, course in enrollments 
                if enrollment.score is not None
            )
            avg_score = weighted_score_sum / scored_credits if scored_credits > 0 else 0
        else:
            avg_score = 0
        
        # 按成绩等级分类
        grade_distribution = {
            'excellent': 0,  # 90-100
            'good': 0,       # 80-89
            'fair': 0,       # 70-79
            'pass': 0,       # 60-69
            'fail': 0        # <60
        }
        
        for enrollment, _, _ in enrollments:
            if enrollment.score is not None:
                score = enrollment.score
                if score >= 90:
                    grade_distribution['excellent'] += 1
                elif score >= 80:
                    grade_distribution['good'] += 1
                elif score >= 70:
                    grade_distribution['fair'] += 1
                elif score >= 60:
                    grade_distribution['pass'] += 1
                else:
                    grade_distribution['fail'] += 1
        
        return {
            'total_enrollments': total_enrollments,
            'total_credits': total_credits,
            'scored_courses': len(scored_enrollments),
            'unscored_courses': total_enrollments - len(scored_enrollments),
            'scored_credits': scored_credits,
            'avg_score': round(avg_score, 2),
            'grade_distribution': grade_distribution
        }
    
    @staticmethod
    def get_time_conflict_analysis(academic_year=None, semester=None):
        """
        分析课程时间冲突情况
        
        Args:
            academic_year: 学年 (可选)
            semester: 学期 (可选)
            
        Returns:
            dict: 时间冲突分析结果
        """
        query = db.session.query(CourseOffering).filter(
            CourseOffering.day_of_week.isnot(None),
            CourseOffering.start_time.isnot(None),
            CourseOffering.end_time.isnot(None)
        )
        
        if academic_year:
            query = query.filter(CourseOffering.academic_year == academic_year)
        if semester is not None:
            query = query.filter(CourseOffering.semester == bool(semester))
            
        offerings = query.all()
        
        # 按时间段分组统计
        time_slots = {}
        conflicts = []
        
        for offering in offerings:
            time_key = f"{offering.day_of_week}_{offering.start_time}_{offering.end_time}"
            
            if time_key not in time_slots:
                time_slots[time_key] = []
            time_slots[time_key].append(offering)
            
            # 检查是否有多个课程在同一时间段
            if len(time_slots[time_key]) > 1:
                conflict_info = {
                    'day_of_week': offering.day_of_week,
                    'start_time': str(offering.start_time),
                    'end_time': str(offering.end_time),
                    'courses': []
                }
                
                for conflicted_offering in time_slots[time_key]:
                    course = Course.query.get(conflicted_offering.course_id)
                    teacher = Teacher.query.get(conflicted_offering.teacher_id)
                    
                    conflict_info['courses'].append({
                        'offering_id': conflicted_offering.offering_id,
                        'course_name': course.course_name if course else '未知',
                        'teacher_name': teacher.name if teacher else '未知'
                    })
                
                conflicts.append(conflict_info)
        
        return {
            'total_scheduled_courses': len(offerings),
            'unique_time_slots': len(time_slots),
            'conflict_count': len(conflicts),
            'conflicts': conflicts
        }
