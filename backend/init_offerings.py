"""
初始化开课数据脚本
为系统添加示例开课数据，用于测试和演示
"""
import requests
import json

# 后端API地址
BASE_URL = "http://localhost:5000/api"

def get_teacher_token(teacher_id, password="123456"):
    """获取教师登录token"""
    login_data = {
        "username": teacher_id,
        "password": password,
        "user_type": "teacher"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"教师 {teacher_id} 登录失败: {response.text}")
        return None

def create_course_offering(token, offering_data):
    """创建开课"""
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.post(f"{BASE_URL}/teacher/courses", json=offering_data, headers=headers)
    if response.status_code == 201:
        result = response.json()
        print(f"✓ 开课成功: {result['offering_id']}")
        return True
    else:
        print(f"✗ 开课失败: {response.text}")
        return False

def init_course_offerings():
    """初始化开课数据"""
    print("=== 开始初始化开课数据 ===")
    
    # 开课数据定义
    offerings = [
        # 张教授 (T001) 的课程
        {
            "teacher_id": "T001",
            "courses": [
                {
                    "course_id": "CS103",
                    "academic_year": "2024",
                    "semester": 1,
                    "max_students": 45,
                    "day_of_week": 2,  # 周二
                    "start_time": "14:00",
                    "end_time": "15:50",
                    "location": "教学楼B201"
                }
            ]
        },
        # 李副教授 (T002) 的课程
        {
            "teacher_id": "T002", 
            "courses": [
                {
                    "course_id": "CS104",
                    "academic_year": "2024",
                    "semester": 1,
                    "max_students": 35,
                    "day_of_week": 4,  # 周四
                    "start_time": "08:00",
                    "end_time": "09:50",
                    "location": "计算机实验室1"
                },
                {
                    "course_id": "CS105",
                    "academic_year": "2024",
                    "semester": 1,
                    "max_students": 30,
                    "day_of_week": 5,  # 周五
                    "start_time": "10:00",
                    "end_time": "11:50",
                    "location": "教学楼B301"
                }
            ]
        },
        # 王讲师 (T003) 的课程
        {
            "teacher_id": "T003",
            "courses": [
                {
                    "course_id": "CS101",
                    "academic_year": "2024",
                    "semester": 1,
                    "max_students": 60,
                    "day_of_week": 1,  # 周一
                    "start_time": "14:00",
                    "end_time": "15:50",
                    "location": "大阶梯教室"
                }
            ]
        },
        # 赵助教 (T004) 的课程
        {
            "teacher_id": "T004",
            "courses": [
                {
                    "course_id": "CS102",
                    "academic_year": "2024",
                    "semester": 1,
                    "max_students": 40,
                    "day_of_week": 3,  # 周三
                    "start_time": "16:00",
                    "end_time": "17:50",
                    "location": "计算机实验室2"
                }
            ]
        }
    ]
    
    success_count = 0
    total_count = 0
    
    for teacher_data in offerings:
        teacher_id = teacher_data["teacher_id"]
        print(f"\n--- 为教师 {teacher_id} 创建开课 ---")
        
        # 获取教师token
        token = get_teacher_token(teacher_id)
        if not token:
            continue
            
        # 创建该教师的所有开课
        for course_data in teacher_data["courses"]:
            total_count += 1
            if create_course_offering(token, course_data):
                success_count += 1
    
    print(f"\n=== 开课数据初始化完成 ===")
    print(f"成功创建: {success_count}/{total_count} 个开课")

if __name__ == "__main__":
    try:
        init_course_offerings()
    except Exception as e:
        print(f"初始化失败: {str(e)}")
        import traceback
        traceback.print_exc()
