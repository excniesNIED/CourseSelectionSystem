#!/usr/bin/env python3
"""
数据库升级脚本 - 为SQLite数据库添加新字段
运行此脚本以确保数据库模式与最新的模型一致
"""

import sqlite3
import os
from datetime import datetime

def upgrade_database():
    """升级SQLite数据库结构"""
    db_path = 'instance/course_selection.db'
    
    if not os.path.exists(db_path):
        print("数据库文件不存在，请先运行 create_db.py 创建数据库")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        print("开始升级数据库...")
        
        # 检查course_offerings表是否已有新字段
        cursor.execute("PRAGMA table_info(course_offerings)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # 添加新字段（如果不存在）
        new_columns = [
            ("day_of_week", "INTEGER"),
            ("start_time", "TIME"),
            ("end_time", "TIME"),
            ("location", "VARCHAR(50)"),
            ("status", "VARCHAR(20) DEFAULT '开放选课'")
        ]
        
        for column_name, column_type in new_columns:
            if column_name not in columns:
                print(f"添加字段: {column_name}")
                cursor.execute(f"ALTER TABLE course_offerings ADD COLUMN {column_name} {column_type}")
        
        # 创建先修关系表（如果不存在）
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS course_prerequisites (
                course_id VARCHAR(5) NOT NULL,
                prerequisite_id VARCHAR(5) NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (course_id, prerequisite_id),
                FOREIGN KEY (course_id) REFERENCES courses(course_id) ON DELETE CASCADE,
                FOREIGN KEY (prerequisite_id) REFERENCES courses(course_id) ON DELETE CASCADE
            )
        """)
        print("确保先修关系表存在")
        
        # 创建索引以提高查询性能
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_course_offerings_time ON course_offerings(day_of_week, start_time, end_time)",
            "CREATE INDEX IF NOT EXISTS idx_course_offerings_status ON course_offerings(status)",
            "CREATE INDEX IF NOT EXISTS idx_course_offerings_location ON course_offerings(location)"
        ]
        
        for index_sql in indexes:
            cursor.execute(index_sql)
        print("创建性能优化索引")
        
        # 更新现有记录的状态字段
        cursor.execute("""
            UPDATE course_offerings 
            SET status = CASE 
                WHEN current_students >= max_students THEN '名额已满'
                ELSE '开放选课'
            END
            WHERE status IS NULL OR status = ''
        """)
        
        conn.commit()
        print("数据库升级完成！")
        return True
        
    except Exception as e:
        conn.rollback()
        print(f"数据库升级失败: {e}")
        return False
    finally:
        conn.close()

if __name__ == '__main__':
    upgrade_database()
