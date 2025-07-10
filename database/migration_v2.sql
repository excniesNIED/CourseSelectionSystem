-- 选课系统数据库迁移脚本 v2
-- 新增课程时间、地点和状态管理功能
-- 执行日期：2025年7月11日

USE course_selection_system;

-- 开始事务
START TRANSACTION;

-- 1. 为 course_offerings 表添加新字段
ALTER TABLE course_offerings 
ADD COLUMN day_of_week INT NULL COMMENT '星期几 (1-7代表周一到周日)',
ADD COLUMN start_time TIME NULL COMMENT '开始时间',
ADD COLUMN end_time TIME NULL COMMENT '结束时间',
ADD COLUMN location VARCHAR(50) NULL COMMENT '上课地点',
ADD COLUMN status VARCHAR(20) NOT NULL DEFAULT '开放选课' COMMENT '课程状态 (开放选课/名额已满/已结束)';

-- 2. 为新字段添加索引以提高查询性能
CREATE INDEX idx_course_offerings_time ON course_offerings(day_of_week, start_time, end_time);
CREATE INDEX idx_course_offerings_status ON course_offerings(status);
CREATE INDEX idx_course_offerings_location ON course_offerings(location);

-- 3. 更新现有数据，为已有开课记录设置默认时间和地点（可选）
-- 这里设置一些示例数据，实际使用时可以根据需要调整
UPDATE course_offerings SET 
    day_of_week = CASE 
        WHEN course_id = 'CS101' THEN 1  -- 周一
        WHEN course_id = 'CS102' THEN 2  -- 周二
        WHEN course_id = 'MA101' THEN 3  -- 周三
        WHEN course_id = 'EN101' THEN 4  -- 周四
        WHEN course_id = 'PH101' THEN 5  -- 周五
        WHEN course_id = 'CS103' THEN 1  -- 周一
        WHEN course_id = 'CS104' THEN 2  -- 周二
        WHEN course_id = 'CS105' THEN 3  -- 周三
        WHEN course_id = 'MA102' THEN 4  -- 周四
        WHEN course_id = 'PE101' THEN 5  -- 周五
        ELSE 1
    END,
    start_time = CASE 
        WHEN offering_id LIKE '%CS101%' THEN '08:00:00'
        WHEN offering_id LIKE '%CS102%' THEN '10:00:00'
        WHEN offering_id LIKE '%MA101%' THEN '14:00:00'
        WHEN offering_id LIKE '%EN101%' THEN '16:00:00'
        WHEN offering_id LIKE '%PH101%' THEN '08:00:00'
        WHEN offering_id LIKE '%CS103%' THEN '10:00:00'
        WHEN offering_id LIKE '%CS104%' THEN '14:00:00'
        WHEN offering_id LIKE '%CS105%' THEN '16:00:00'
        WHEN offering_id LIKE '%MA102%' THEN '08:00:00'
        WHEN offering_id LIKE '%PE101%' THEN '10:00:00'
        ELSE '08:00:00'
    END,
    end_time = CASE 
        WHEN offering_id LIKE '%CS101%' THEN '09:50:00'
        WHEN offering_id LIKE '%CS102%' THEN '11:50:00'
        WHEN offering_id LIKE '%MA101%' THEN '15:50:00'
        WHEN offering_id LIKE '%EN101%' THEN '17:50:00'
        WHEN offering_id LIKE '%PH101%' THEN '09:50:00'
        WHEN offering_id LIKE '%CS103%' THEN '11:50:00'
        WHEN offering_id LIKE '%CS104%' THEN '15:50:00'
        WHEN offering_id LIKE '%CS105%' THEN '17:50:00'
        WHEN offering_id LIKE '%MA102%' THEN '09:50:00'
        WHEN offering_id LIKE '%PE101%' THEN '11:50:00'
        ELSE '09:50:00'
    END,
    location = CASE 
        WHEN course_id LIKE 'CS%' THEN '计算机楼101'
        WHEN course_id LIKE 'MA%' THEN '数学楼201'
        WHEN course_id = 'EN101' THEN '外语楼301'
        WHEN course_id = 'PH101' THEN '物理楼401'
        WHEN course_id = 'PE101' THEN '体育馆'
        ELSE '教学楼A101'
    END,
    status = CASE 
        WHEN current_students >= max_students THEN '名额已满'
        ELSE '开放选课'
    END
WHERE day_of_week IS NULL;

-- 4. 添加约束检查
-- 确保 day_of_week 在1-7范围内
ALTER TABLE course_offerings 
ADD CONSTRAINT chk_day_of_week CHECK (day_of_week IS NULL OR (day_of_week >= 1 AND day_of_week <= 7));

-- 确保开始时间小于结束时间
ALTER TABLE course_offerings 
ADD CONSTRAINT chk_time_order CHECK (start_time IS NULL OR end_time IS NULL OR start_time < end_time);

-- 确保状态值有效
ALTER TABLE course_offerings 
ADD CONSTRAINT chk_status CHECK (status IN ('开放选课', '名额已满', '已结束', '暂停选课'));

-- 提交事务
COMMIT;

-- 显示迁移完成信息
SELECT 'Database migration v2 completed successfully' AS status;

-- 验证新字段
SELECT 
    offering_id,
    course_id,
    day_of_week,
    start_time,
    end_time,
    location,
    status,
    current_students,
    max_students
FROM course_offerings 
LIMIT 5;
