#!/usr/bin/env python
# -*- coding: utf-8 -*-

from app import create_app, db
from app.models import Admin, Class, Student, Course, Teacher

def main():
    app = create_app()
    
    with app.app_context():
        try:
            # 创建表
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
            class1 = Class(class_id='CS01', class_name='计算机科学与技术1班')
            db.session.add(class1)
            
            # 创建课程
            course1 = Course(course_id='CS101', course_name='数据结构', hours=64, exam_type=True, credits=4.0)
            db.session.add(course1)
            
            # 创建教师
            teacher1 = Teacher(teacher_id='T001', name='张教授', gender='男', age=45, title='教授', phone='13800138001')
            teacher1.set_password('123456')
            db.session.add(teacher1)
            
            # 创建学生
            student1 = Student(student_id='2021001001', name='张三', gender='男', age=20, hometown='北京', class_id='CS01')
            student1.set_password('123456')
            db.session.add(student1)
            
            db.session.commit()
            
            print("Success: Test data created!")
            
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    main()
