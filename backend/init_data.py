# -*- coding: utf-8 -*-
from app import create_app, db
from app.models import Admin, Class, Student, Course, Teacher, CourseOffering, Enrollment

app = create_app()

def init_data():
    """初始化测试数据"""
    try:
        with app.app_context():
            # 清空现有数据
            db.drop_all()
            db.create_all()
              # 1. 创建管理员
            admin = Admin(
                admin_id='admin001',
                username='admin',
                name='系统管理员'
            )
            admin.set_password('admin123')
            db.session.add(admin)
            
            # 2. 创建班级
            classes = [
                Class(class_id='CS01', class_name='计算机科学与技术1班'),
                Class(class_id='CS02', class_name='计算机科学与技术2班'),
                Class(class_id='SE01', class_name='软件工程1班'),
            ]
            db.session.add_all(classes)
            
            # 3. 创建课程
            courses = [
                Course(course_id='CS101', course_name='数据结构', hours=64, exam_type=True, credits=4.0),
                Course(course_id='CS102', course_name='算法设计与分析', hours=48, exam_type=True, credits=3.0),
                Course(course_id='CS103', course_name='数据库原理', hours=64, exam_type=True, credits=4.0),
                Course(course_id='CS104', course_name='计算机网络', hours=48, exam_type=True, credits=3.0),
                Course(course_id='CS105', course_name='软件工程', hours=48, exam_type=False, credits=3.0),
            ]
            db.session.add_all(courses)
              # 4. 创建教师
            teachers = [
                Teacher(teacher_id='T001', name='张教授', gender='男', age=45, title='教授', phone='13800138001'),
                Teacher(teacher_id='T002', name='李副教授', gender='女', age=38, title='副教授', phone='13800138002'),
                Teacher(teacher_id='T003', name='王讲师', gender='男', age=32, title='讲师', phone='13800138003'),
                Teacher(teacher_id='T004', name='赵博士', gender='女', age=35, title='讲师', phone='13800138004'),
            ]
            for teacher in teachers:
                teacher.set_password('teacher123')
            db.session.add_all(teachers)            # 5. 创建学生
            students = [
                Student(student_id='202301001001', name='张三', gender='男', age=20, hometown='北京', class_id='CS01'),
                Student(student_id='202301001002', name='李四', gender='女', age=19, hometown='上海', class_id='CS01'),
                Student(student_id='202301001003', name='王五', gender='男', age=20, hometown='广州', class_id='CS02'),
                Student(student_id='202301001004', name='赵六', gender='女', age=19, hometown='深圳', class_id='CS02'),
                Student(student_id='202301001005', name='钱七', gender='男', age=20, hometown='杭州', class_id='SE01'),
            ]
            for student in students:
                student.set_password('student123')
            db.session.add_all(students)
            
            # 提交基础数据
            db.session.commit()
            
            print("✅ 测试数据初始化完成！")
            print("👤 管理员: admin / admin123")
            print("👨‍🏫 教师: T001-T004 / teacher123")
            print("👨‍🎓 学生: 202301001001-202301001005 / student123")
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    init_data()
