#!/usr/bin/env python3
"""
更新课程开课的current_students字段
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.models import db, CourseOffering, Enrollment
from sqlalchemy import func

def update_current_students():
    """更新所有开课的current_students字段"""
    app = create_app()
    
    with app.app_context():
        try:
            # 获取所有开课
            offerings = CourseOffering.query.all()
            
            print(f"找到 {len(offerings)} 个开课记录")
            
            updated_count = 0
            
            for offering in offerings:
                # 计算该课程的实际选课人数
                actual_count = Enrollment.query.filter_by(offering_id=offering.offering_id).count()
                
                # 更新字段
                if offering.current_students != actual_count:
                    print(f"更新 {offering.offering_id}: {offering.current_students} -> {actual_count}")
                    offering.current_students = actual_count
                    updated_count += 1
                else:
                    print(f"  {offering.offering_id}: {actual_count} (无需更新)")
            
            # 提交更改
            db.session.commit()
            
            print(f"\n成功更新 {updated_count} 个开课记录的选课人数")
            
            # 显示更新后的统计
            print("\n更新后的选课统计:")
            for offering in offerings:
                print(f"  {offering.course.course_name} ({offering.teacher.name}): {offering.current_students}/{offering.max_students} 人")
                    
        except Exception as e:
            print(f"更新失败: {e}")
            db.session.rollback()

if __name__ == "__main__":
    update_current_students()
