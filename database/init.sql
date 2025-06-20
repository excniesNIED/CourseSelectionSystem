-- 教务系统选课系统数据库初始化脚本
-- 数据库：MariaDB

-- 创建数据库
CREATE DATABASE IF NOT EXISTS course_selection_system 
CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE course_selection_system;

-- 1. 班级表
CREATE TABLE IF NOT EXISTS classes (
    class_id VARCHAR(4) NOT NULL PRIMARY KEY COMMENT '班级编号',
    class_name VARCHAR(20) NOT NULL COMMENT '班级名称',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) COMMENT '班级信息表';

-- 2. 学生表
CREATE TABLE IF NOT EXISTS students (
    student_id VARCHAR(12) NOT NULL PRIMARY KEY COMMENT '学号',
    name VARCHAR(5) NOT NULL COMMENT '姓名',
    gender VARCHAR(1) NOT NULL COMMENT '性别',
    age INT NOT NULL COMMENT '年龄',
    hometown VARCHAR(20) NOT NULL COMMENT '生源所在地',
    total_credits FLOAT DEFAULT 0 COMMENT '已修学分总数',
    password VARCHAR(255) NOT NULL COMMENT '登录密码',
    class_id VARCHAR(4) NOT NULL COMMENT '班级编号',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (class_id) REFERENCES classes(class_id) ON DELETE RESTRICT ON UPDATE CASCADE
) COMMENT '学生信息表';

-- 3. 课程表
CREATE TABLE IF NOT EXISTS courses (
    course_id VARCHAR(5) NOT NULL PRIMARY KEY COMMENT '课程编号',
    course_name VARCHAR(20) NOT NULL COMMENT '课程名称',
    hours INT NOT NULL COMMENT '学时',
    exam_type BIT NOT NULL COMMENT '考试或考查(1:考试, 0:考查)',
    credits FLOAT NOT NULL COMMENT '学分',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) COMMENT '课程信息表';

-- 4. 教师表
CREATE TABLE IF NOT EXISTS teachers (
    teacher_id VARCHAR(5) NOT NULL PRIMARY KEY COMMENT '教师编号',
    name VARCHAR(20) NOT NULL COMMENT '姓名',
    gender VARCHAR(1) NOT NULL COMMENT '性别',
    age INT NOT NULL COMMENT '年龄',
    title VARCHAR(10) NOT NULL COMMENT '职称',
    phone VARCHAR(20) NOT NULL COMMENT '电话',
    password VARCHAR(255) NOT NULL COMMENT '登录密码',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) COMMENT '教师信息表';

-- 5. 开课情况表
CREATE TABLE IF NOT EXISTS course_offerings (
    offering_id VARCHAR(15) NOT NULL PRIMARY KEY COMMENT '开课编号',
    course_id VARCHAR(5) NOT NULL COMMENT '课程编号',
    teacher_id VARCHAR(5) NOT NULL COMMENT '任课教师编号',
    academic_year VARCHAR(4) NOT NULL COMMENT '开课学年',
    semester BIT NOT NULL COMMENT '开课学期(1:第一学期, 0:第二学期)',
    max_students INT DEFAULT 50 COMMENT '最大选课人数',
    current_students INT DEFAULT 0 COMMENT '当前选课人数',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (course_id) REFERENCES courses(course_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY (teacher_id) REFERENCES teachers(teacher_id) ON DELETE RESTRICT ON UPDATE CASCADE
) COMMENT '开课情况表';

-- 6. 选课情况表
CREATE TABLE IF NOT EXISTS enrollments (
    offering_id VARCHAR(15) NOT NULL COMMENT '开课编号',
    student_id VARCHAR(12) NOT NULL COMMENT '学号',
    score INT DEFAULT NULL COMMENT '成绩',
    enrollment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '选课时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (offering_id, student_id),
    FOREIGN KEY (offering_id) REFERENCES course_offerings(offering_id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE ON UPDATE CASCADE
) COMMENT '选课情况表';

-- 7. 管理员表 (系统管理员)
CREATE TABLE IF NOT EXISTS admins (
    admin_id VARCHAR(10) NOT NULL PRIMARY KEY COMMENT '管理员编号',
    username VARCHAR(20) NOT NULL UNIQUE COMMENT '用户名',
    password VARCHAR(255) NOT NULL COMMENT '登录密码',
    name VARCHAR(20) NOT NULL COMMENT '姓名',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) COMMENT '管理员信息表';

-- 创建索引以提高查询性能
CREATE INDEX idx_students_class ON students(class_id);
CREATE INDEX idx_course_offerings_course ON course_offerings(course_id);
CREATE INDEX idx_course_offerings_teacher ON course_offerings(teacher_id);
CREATE INDEX idx_course_offerings_year_semester ON course_offerings(academic_year, semester);
CREATE INDEX idx_enrollments_student ON enrollments(student_id);
CREATE INDEX idx_enrollments_offering ON enrollments(offering_id);

-- 插入初始数据

-- 插入管理员
INSERT INTO admins (admin_id, username, password, name) VALUES 
('admin001', 'admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj3JU.Q/Z.CO', '系统管理员');
-- 密码为 'admin123'

-- 插入班级
INSERT INTO classes (class_id, class_name) VALUES 
('CS01', '计算机科学与技术1班'),
('CS02', '计算机科学与技术2班'),
('SE01', '软件工程1班'),
('SE02', '软件工程2班'),
('AI01', '人工智能1班');

-- 插入课程
INSERT INTO courses (course_id, course_name, hours, exam_type, credits) VALUES 
('CS101', '程序设计基础', 64, 1, 4.0),
('CS102', '数据结构', 48, 1, 3.0),
('CS103', '计算机组成原理', 48, 1, 3.0),
('CS104', '操作系统', 48, 1, 3.0),
('CS105', '数据库系统', 48, 1, 3.0),
('MA101', '高等数学', 80, 1, 5.0),
('MA102', '线性代数', 32, 1, 2.0),
('EN101', '大学英语', 48, 0, 3.0),
('PH101', '大学物理', 64, 1, 4.0),
('PE101', '体育', 32, 0, 2.0);

-- 插入教师
INSERT INTO teachers (teacher_id, name, gender, age, title, phone, password) VALUES 
('T001', '张教授', '男', 45, '教授', '13800138001', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj3JU.Q/Z.CO'),
('T002', '李副教授', '女', 38, '副教授', '13800138002', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj3JU.Q/Z.CO'),
('T003', '王讲师', '男', 32, '讲师', '13800138003', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj3JU.Q/Z.CO'),
('T004', '刘教授', '女', 50, '教授', '13800138004', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj3JU.Q/Z.CO'),
('T005', '陈讲师', '男', 35, '讲师', '13800138005', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj3JU.Q/Z.CO');
-- 所有教师密码为 'teacher123'

-- 插入学生
INSERT INTO students (student_id, name, gender, age, hometown, total_credits, password, class_id) VALUES 
('202301001001', '张三', '男', 20, '北京', 0, '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj3JU.Q/Z.CO', 'CS01'),
('202301001002', '李四', '女', 19, '上海', 0, '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj3JU.Q/Z.CO', 'CS01'),
('202301001003', '王五', '男', 20, '广州', 0, '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj3JU.Q/Z.CO', 'CS01'),
('202301002001', '赵六', '女', 19, '深圳', 0, '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj3JU.Q/Z.CO', 'CS02'),
('202301002002', '钱七', '男', 20, '杭州', 0, '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj3JU.Q/Z.CO', 'CS02'),
('202301003001', '孙八', '女', 19, '南京', 0, '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj3JU.Q/Z.CO', 'SE01'),
('202301003002', '周九', '男', 20, '武汉', 0, '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj3JU.Q/Z.CO', 'SE01'),
('202301004001', '吴十', '女', 19, '成都', 0, '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj3JU.Q/Z.CO', 'SE02'),
('202301005001', '郑一', '男', 20, '西安', 0, '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj3JU.Q/Z.CO', 'AI01'),
('202301005002', '王二', '女', 19, '重庆', 0, '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj3JU.Q/Z.CO', 'AI01');
-- 所有学生密码为 'student123'

-- 插入开课情况
INSERT INTO course_offerings (offering_id, course_id, teacher_id, academic_year, semester, max_students) VALUES 
('2024-1-CS101-T001', 'CS101', 'T001', '2024', 1, 50),
('2024-1-CS102-T002', 'CS102', 'T002', '2024', 1, 45),
('2024-1-MA101-T003', 'MA101', 'T003', '2024', 1, 60),
('2024-1-EN101-T004', 'EN101', 'T004', '2024', 1, 40),
('2024-1-PH101-T005', 'PH101', 'T005', '2024', 1, 50),
('2024-2-CS103-T001', 'CS103', 'T001', '2024', 0, 45),
('2024-2-CS104-T002', 'CS104', 'T002', '2024', 0, 45),
('2024-2-CS105-T003', 'CS105', 'T003', '2024', 0, 40),
('2024-2-MA102-T004', 'MA102', 'T004', '2024', 0, 50),
('2024-2-PE101-T005', 'PE101', 'T005', '2024', 0, 30);

-- 插入一些选课记录
INSERT INTO enrollments (offering_id, student_id, score) VALUES 
('2024-1-CS101-T001', '202301001001', 85),
('2024-1-CS101-T001', '202301001002', 92),
('2024-1-CS101-T001', '202301001003', 78),
('2024-1-CS102-T002', '202301001001', 88),
('2024-1-CS102-T002', '202301001002', 95),
('2024-1-MA101-T003', '202301001001', 76),
('2024-1-MA101-T003', '202301001002', 89),
('2024-1-MA101-T003', '202301001003', 82),
('2024-1-EN101-T004', '202301001001', 90),
('2024-1-EN101-T004', '202301002001', 87);

-- 更新开课情况的当前选课人数
UPDATE course_offerings SET current_students = (
    SELECT COUNT(*) FROM enrollments WHERE enrollments.offering_id = course_offerings.offering_id
);

-- 更新学生的总学分
UPDATE students SET total_credits = (
    SELECT COALESCE(SUM(c.credits), 0)
    FROM enrollments e 
    JOIN course_offerings co ON e.offering_id = co.offering_id
    JOIN courses c ON co.course_id = c.course_id
    WHERE e.student_id = students.student_id AND e.score >= 60
);

COMMIT;
