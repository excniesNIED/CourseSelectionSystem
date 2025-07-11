from app import db
from datetime import datetime, time
import bcrypt

# 定义课程先修关系的关联表
course_prerequisites = db.Table('course_prerequisites',
    db.Column('course_id', db.String(5), db.ForeignKey('courses.course_id'), primary_key=True),
    db.Column('prerequisite_id', db.String(5), db.ForeignKey('courses.course_id'), primary_key=True)
)

class Admin(db.Model):
    __tablename__ = 'admins'
    
    admin_id = db.Column(db.String(10), primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def set_password(self, password):
        """设置密码哈希"""
        self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def check_password(self, password):
        """检查密码"""
        return bcrypt.checkpw(password.encode('utf-8'), self.password.encode('utf-8'))

class Class(db.Model):
    __tablename__ = 'classes'
    
    class_id = db.Column(db.String(4), primary_key=True)
    class_name = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    students = db.relationship('Student', backref='class_info', lazy=True)

class Student(db.Model):
    __tablename__ = 'students'
    
    student_id = db.Column(db.String(12), primary_key=True)
    name = db.Column(db.String(5), nullable=False)
    gender = db.Column(db.String(1), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    hometown = db.Column(db.String(20), nullable=False)
    total_credits = db.Column(db.Float, default=0)
    password = db.Column(db.String(255), nullable=False)
    class_id = db.Column(db.String(4), db.ForeignKey('classes.class_id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    enrollments = db.relationship('Enrollment', backref='student', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """设置密码哈希"""
        self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def check_password(self, password):
        """检查密码"""
        return bcrypt.checkpw(password.encode('utf-8'), self.password.encode('utf-8'))

class Course(db.Model):
    __tablename__ = 'courses'
    
    course_id = db.Column(db.String(5), primary_key=True)
    course_name = db.Column(db.String(20), nullable=False)
    hours = db.Column(db.Integer, nullable=False)
    exam_type = db.Column(db.Boolean, nullable=False)  # True: 考试, False: 考查
    credits = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    offerings = db.relationship('CourseOffering', backref='course', lazy=True, cascade='all, delete-orphan')
    
    # 先修课程关系：此课程需要的先修课程
    prerequisites = db.relationship(
        'Course',
        secondary=course_prerequisites,
        primaryjoin=course_id == course_prerequisites.c.course_id,
        secondaryjoin=course_id == course_prerequisites.c.prerequisite_id,
        backref=db.backref('required_for', lazy='dynamic'),  # 反向关系：此课程是哪些课程的先修课
        lazy='dynamic'
    )

class Teacher(db.Model):
    __tablename__ = 'teachers'
    
    teacher_id = db.Column(db.String(5), primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    gender = db.Column(db.String(1), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(10), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    offerings = db.relationship('CourseOffering', backref='teacher', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """设置密码哈希"""
        self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def check_password(self, password):
        """检查密码"""
        return bcrypt.checkpw(password.encode('utf-8'), self.password.encode('utf-8'))

class CourseOffering(db.Model):
    __tablename__ = 'course_offerings'
    
    offering_id = db.Column(db.String(15), primary_key=True)
    course_id = db.Column(db.String(5), db.ForeignKey('courses.course_id'), nullable=False)
    teacher_id = db.Column(db.String(5), db.ForeignKey('teachers.teacher_id'), nullable=False)
    academic_year = db.Column(db.String(4), nullable=False)
    semester = db.Column(db.Boolean, nullable=False)  # True: 第一学期, False: 第二学期
    max_students = db.Column(db.Integer, default=50)
    current_students = db.Column(db.Integer, default=0)
    # 新增字段：课程时间和地点
    day_of_week = db.Column(db.Integer, nullable=True)  # 1-7 代表周一到周日
    start_time = db.Column(db.Time, nullable=True)  # 开始时间
    end_time = db.Column(db.Time, nullable=True)  # 结束时间
    location = db.Column(db.String(50), nullable=True)  # 上课地点
    status = db.Column(db.String(20), default='开放选课', nullable=False)  # 课程状态
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    enrollments = db.relationship('Enrollment', backref='offering', lazy=True, cascade='all, delete-orphan')

class Enrollment(db.Model):
    __tablename__ = 'enrollments'
    
    offering_id = db.Column(db.String(15), db.ForeignKey('course_offerings.offering_id'), primary_key=True)
    student_id = db.Column(db.String(12), db.ForeignKey('students.student_id'), primary_key=True)
    score = db.Column(db.Integer, nullable=True)
    enrollment_date = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
