import requests
import json

# 测试后端 API
BASE_URL = "http://127.0.0.1:5000/api"

def init_data():
    """初始化数据"""
    try:
        response = requests.post(f"{BASE_URL}/admin/init-data")
        print(f"初始化数据 - 状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"初始化数据失败: {e}")
        return False

def test_login():
    """测试登录功能"""
    login_data = {
        "username": "admin",
        "password": "123456",
        "user_type": "admin"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        print(f"登录测试 - 状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        
        if response.status_code == 200:
            return response.json().get('access_token')
        else:
            print("登录失败")
            return None
    except Exception as e:
        print(f"请求失败: {e}")
        return None

def test_teachers_api(token):
    """测试教师管理 API"""
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        # 获取教师列表
        response = requests.get(f"{BASE_URL}/admin/teachers", headers=headers)
        print(f"获取教师列表 - 状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"教师数量: {len(data.get('teachers', []))}")
        
        # 创建新教师
        new_teacher = {
            "teacher_id": "T005",
            "name": "新教师",
            "gender": "男",
            "age": 30,
            "title": "讲师",
            "phone": "13800138005",
            "password": "123456"
        }
        
        response = requests.post(f"{BASE_URL}/admin/teachers", json=new_teacher, headers=headers)
        print(f"创建教师 - 状态码: {response.status_code}")
        if response.status_code == 201:
            print("✅ 教师创建成功")
        
    except Exception as e:
        print(f"教师 API 测试失败: {e}")

if __name__ == "__main__":
    print("🚀 开始 API 测试...")
    
    # 初始化数据
    if init_data():
        print("✅ 数据初始化成功")
    
    # 测试登录
    token = test_login()
    
    if not token:
        print("❌ 登录失败")
    else:
        print("✅ 登录成功！")
        
        # 测试教师管理 API
        test_teachers_api(token)
