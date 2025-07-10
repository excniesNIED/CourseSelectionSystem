#!/usr/bin/env python3
"""
创建示例学生选课数据
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.models import db, Student, CourseOffering, Enrollment
from sqlalchemy import text
import random

def create_sample_enrollments():
    """创建示例选课数据"""
    app = create_app()
    
    with app.app_context():
        try:
            # 获取所有学生和课程开课信息
            students = Student.query.all()
            offerings = CourseOffering.query.all()
            
            print(f"找到 {len(students)} 个学生和 {len(offerings)} 个课程开课")
            
            if not students or not offerings:
                print("没有找到学生或课程开课数据，请先运行初始化脚本")
                return
            
            # 清空现有选课记录
            db.session.execute(text("DELETE FROM enrollments"))
            db.session.commit()
            print("已清空现有选课记录")
            
            enrollment_count = 0
            
            # 为每个学生随机选择一些课程
            for student in students:
                # 每个学生选择 2-4 门课程
                num_courses = random.randint(2, min(4, len(offerings)))
                selected_offerings = random.sample(offerings, num_courses)
                
                for offering in selected_offerings:
                    # 检查是否已经选过这门课
                    existing = Enrollment.query.filter_by(
                        student_id=student.student_id,
                        offering_id=offering.offering_id
                    ).first()
                    
                    if not existing:
                        enrollment = Enrollment(
                            student_id=student.student_id,
                            offering_id=offering.offering_id
                        )
                        db.session.add(enrollment)
                        enrollment_count += 1
            
            db.session.commit()
            print(f"成功创建 {enrollment_count} 条选课记录")
            
            # 显示统计信息
            print("\n选课统计:")
            for offering in offerings:
                count = Enrollment.query.filter_by(offering_id=offering.offering_id).count()
                print(f"  {offering.course.course_name} ({offering.teacher.name}): {count} 人选课")
            
            print("\n学生选课统计:")
            for student in students[:5]:  # 只显示前5个学生
                count = Enrollment.query.filter_by(student_id=student.student_id).count()
                enrollments = Enrollment.query.filter_by(student_id=student.student_id).all()
                courses = [e.offering.course.course_name for e in enrollments]
                print(f"  {student.name} ({student.student_id}): {count} 门课程 - {', '.join(courses[:3])}")
                if len(courses) > 3:
                    print(f"    还有 {len(courses) - 3} 门课程...")
                    
        except Exception as e:
            print(f"创建选课数据时出错: {e}")
            db.session.rollback()

if __name__ == "__main__":
    create_sample_enrollments()
