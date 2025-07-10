-- 选课系统先修课程关系表迁移脚本
-- 新增课程先修关系功能
-- 执行日期：2025年7月11日

USE course_selection_system;

-- 开始事务
START TRANSACTION;

-- 1. 创建课程先修关系表
CREATE TABLE IF NOT EXISTS course_prerequisites (
    course_id VARCHAR(5) NOT NULL COMMENT '课程编号',
    prerequisite_id VARCHAR(5) NOT NULL COMMENT '先修课程编号',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (course_id, prerequisite_id),
    FOREIGN KEY (course_id) REFERENCES courses(course_id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (prerequisite_id) REFERENCES courses(course_id) ON DELETE CASCADE ON UPDATE CASCADE,
    -- 防止课程自己作为自己的先修课程
    CONSTRAINT chk_no_self_prerequisite CHECK (course_id != prerequisite_id)
) COMMENT '课程先修关系表';

-- 2. 添加索引提高查询性能
CREATE INDEX idx_prerequisites_course ON course_prerequisites(course_id);
CREATE INDEX idx_prerequisites_prerequisite ON course_prerequisites(prerequisite_id);

-- 3. 插入一些示例先修关系数据
INSERT INTO course_prerequisites (course_id, prerequisite_id) VALUES 
-- 数据结构需要先学程序设计基础
('CS102', 'CS101'),
-- 计算机组成原理需要先学程序设计基础
('CS103', 'CS101'),
-- 操作系统需要先学数据结构和计算机组成原理
('CS104', 'CS102'),
('CS104', 'CS103'),
-- 数据库系统需要先学数据结构
('CS105', 'CS102'),
-- 线性代数需要先学高等数学
('MA102', 'MA101');

-- 4. 创建视图，方便查询课程及其先修课程
CREATE OR REPLACE VIEW course_with_prerequisites AS
SELECT 
    c.course_id,
    c.course_name,
    c.credits,
    GROUP_CONCAT(
        CONCAT(p.course_id, ':', p.course_name) 
        ORDER BY p.course_id 
        SEPARATOR '; '
    ) AS prerequisites
FROM courses c
LEFT JOIN course_prerequisites cp ON c.course_id = cp.course_id
LEFT JOIN courses p ON cp.prerequisite_id = p.course_id
GROUP BY c.course_id, c.course_name, c.credits
ORDER BY c.course_id;

-- 5. 创建视图，方便查询课程依赖关系
CREATE OR REPLACE VIEW course_dependency_tree AS
SELECT 
    p.course_id as prerequisite_course_id,
    p.course_name as prerequisite_course_name,
    c.course_id as dependent_course_id,
    c.course_name as dependent_course_name
FROM course_prerequisites cp
JOIN courses p ON cp.prerequisite_id = p.course_id
JOIN courses c ON cp.course_id = c.course_id
ORDER BY p.course_id, c.course_id;

-- 提交事务
COMMIT;

-- 显示迁移完成信息
SELECT 'Course prerequisites migration completed successfully' AS status;

-- 验证先修关系数据
SELECT * FROM course_with_prerequisites;

-- 验证依赖关系
SELECT * FROM course_dependency_tree;
