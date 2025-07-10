from app import db
from app.models import Student, Course, CourseOffering, Enrollment
from .exceptions import (
    CourseFullError, TimeConflictError, AlreadyEnrolledError,
    PrerequisiteNotMetError, CourseNotFoundError, StudentNotFoundError
)
from datetime import datetime, time
from sqlalchemy import and_

class StudentService:
    """学生业务逻辑服务"""
    
    @staticmethod
    def enroll_in_course(student_id, offering_id):
        """
        学生选课核心业务逻辑
        
        Args:
            student_id: 学生ID
            offering_id: 开课ID
            
        Returns:
            dict: 选课结果信息
            
        Raises:
            CourseNotFoundError: 课程不存在
            StudentNotFoundError: 学生不存在
            AlreadyEnrolledError: 已经选课
            CourseFullError: 课程人数已满
            TimeConflictError: 时间冲突
            PrerequisiteNotMetError: 先修课程要求未满足
        """
        
        # 1. 验证学生是否存在
        student = Student.query.filter_by(student_id=student_id).first()
        if not student:
            raise StudentNotFoundError()
        
        # 2. 验证开课是否存在
        offering = CourseOffering.query.filter_by(offering_id=offering_id).first()
        if not offering:
            raise CourseNotFoundError("开课不存在")
        
        # 3. 检查是否已经选过这门课
        existing_enrollment = Enrollment.query.filter_by(
            offering_id=offering_id,
            student_id=student_id
        ).first()
        if existing_enrollment:
            raise AlreadyEnrolledError("已经选过这门课")
        
        # 4. 检查是否选过同一门课程的其他班级
        same_course_enrollment = db.session.query(Enrollment).join(CourseOffering).filter(
            CourseOffering.course_id == offering.course_id,
            Enrollment.student_id == student_id
        ).first()
        if same_course_enrollment:
            raise AlreadyEnrolledError("已经选过此课程的其他班级")
        
        # 5. 检查是否还有名额
        if offering.current_students >= offering.max_students:
            raise CourseFullError()
        
        # 6. 检查时间冲突
        StudentService._check_time_conflict(student_id, offering)
        
        # 7. 检查先修课程要求
        StudentService._check_prerequisites(student_id, offering.course_id)
        
        # 8. 创建选课记录
        enrollment = Enrollment(
            offering_id=offering_id,
            student_id=student_id
        )
        
        # 9. 更新当前选课人数
        offering.current_students += 1
        
        # 10. 更新课程状态
        if offering.current_students >= offering.max_students:
            offering.status = '名额已满'
        
        # 11. 保存到数据库
        db.session.add(enrollment)
        db.session.commit()
        
        return {
            'message': '选课成功',
            'enrollment_id': f"{offering_id}-{student_id}",
            'course_name': offering.course.course_name,
            'teacher_name': offering.teacher.name,
            'current_students': offering.current_students,
            'max_students': offering.max_students
        }
    
    @staticmethod
    def _check_time_conflict(student_id, new_offering):
        """
        检查时间冲突
        
        Args:
            student_id: 学生ID
            new_offering: 新的开课对象
            
        Raises:
            TimeConflictError: 时间冲突时抛出异常
        """
        # 如果新开课没有设置时间，跳过冲突检查
        if not all([new_offering.day_of_week, new_offering.start_time, new_offering.end_time]):
            return
        
        # 查询学生已选课程的时间安排
        enrolled_offerings = db.session.query(CourseOffering).join(Enrollment).filter(
            Enrollment.student_id == student_id,
            CourseOffering.day_of_week.isnot(None),
            CourseOffering.start_time.isnot(None),
            CourseOffering.end_time.isnot(None)
        ).all()
        
        for existing_offering in enrolled_offerings:
            # 检查是否为同一天
            if existing_offering.day_of_week == new_offering.day_of_week:
                # 检查时间是否重叠
                if StudentService._is_time_overlap(
                    existing_offering.start_time, existing_offering.end_time,
                    new_offering.start_time, new_offering.end_time
                ):
                    raise TimeConflictError(
                        f"与课程《{existing_offering.course.course_name}》时间冲突"
                    )
    
    @staticmethod
    def _is_time_overlap(start1, end1, start2, end2):
        """
        检查两个时间段是否重叠
        
        Args:
            start1, end1: 第一个时间段
            start2, end2: 第二个时间段
            
        Returns:
            bool: 是否重叠
        """
        return not (end1 <= start2 or end2 <= start1)
    
    @staticmethod
    def _check_prerequisites(student_id, course_id):
        """
        检查先修课程要求
        
        Args:
            student_id: 学生ID
            course_id: 课程ID
            
        Raises:
            PrerequisiteNotMetError: 先修课程要求未满足时抛出异常
        """
        # 获取课程的先修课程
        course = Course.query.filter_by(course_id=course_id).first()
        if not course:
            return
        
        prerequisites = course.prerequisites.all()
        if not prerequisites:
            return  # 没有先修课程要求
        
        # 检查学生是否已完成所有先修课程（成绩>=60分）
        for prereq_course in prerequisites:
            # 查询学生是否已修过此先修课程且成绩合格
            completed = db.session.query(Enrollment).join(CourseOffering).filter(
                CourseOffering.course_id == prereq_course.course_id,
                Enrollment.student_id == student_id,
                Enrollment.score.isnot(None),
                Enrollment.score >= 60
            ).first()
            
            if not completed:
                raise PrerequisiteNotMetError(
                    f"需要先完成课程《{prereq_course.course_name}》"
                )
    
    @staticmethod
    def drop_course(student_id, offering_id):
        """
        学生退课
        
        Args:
            student_id: 学生ID
            offering_id: 开课ID
            
        Returns:
            dict: 退课结果信息
            
        Raises:
            CourseNotFoundError: 未选择此课程
            AlreadyGradedError: 已有成绩，无法退选
        """
        # 查找选课记录
        enrollment = Enrollment.query.filter_by(
            offering_id=offering_id,
            student_id=student_id
        ).first()
        
        if not enrollment:
            raise CourseNotFoundError("未选择此课程")
        
        # 检查是否已有成绩
        if enrollment.score is not None:
            raise AlreadyEnrolledError("已有成绩，无法退选")
        
        # 获取开课信息并更新人数
        offering = CourseOffering.query.filter_by(offering_id=offering_id).first()
        if offering:
            offering.current_students = max(0, offering.current_students - 1)
            # 更新状态
            if offering.current_students < offering.max_students:
                offering.status = '开放选课'
        
        # 删除选课记录
        db.session.delete(enrollment)
        db.session.commit()
        
        return {
            'message': '退选成功',
            'course_name': offering.course.course_name if offering else '未知课程'
        }
    
    @staticmethod
    def get_student_schedule(student_id):
        """
        获取学生课表信息
        
        Args:
            student_id: 学生ID
            
        Returns:
            list: 学生课表信息列表
        """
        # 查询学生已选课程及其时间安排
        enrolled_courses = db.session.query(
            CourseOffering, Course, Enrollment
        ).join(Course, CourseOffering.course_id == Course.course_id)\
         .join(Enrollment, CourseOffering.offering_id == Enrollment.offering_id)\
         .filter(Enrollment.student_id == student_id)\
         .all()
        
        schedule = []
        for offering, course, enrollment in enrolled_courses:
            schedule.append({
                'offering_id': offering.offering_id,
                'course_id': course.course_id,
                'course_name': course.course_name,
                'day_of_week': offering.day_of_week,
                'start_time': offering.start_time.strftime('%H:%M') if offering.start_time else None,
                'end_time': offering.end_time.strftime('%H:%M') if offering.end_time else None,
                'location': offering.location,
                'teacher_name': offering.teacher.name,
                'academic_year': offering.academic_year,
                'semester': offering.semester
            })
        
        return schedule
