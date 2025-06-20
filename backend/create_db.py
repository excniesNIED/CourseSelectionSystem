import pymysql

try:
    # 尝试连接 MariaDB 并创建数据库
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='123456',
        charset='utf8mb4',
        autocommit=True
    )
    
    cursor = conn.cursor()
    
    # 创建数据库
    cursor.execute("CREATE DATABASE IF NOT EXISTS course_selection_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
    print("数据库创建成功！")
    
    cursor.close()
    conn.close()
    
except pymysql.err.OperationalError as e:
    if "Authentication plugin" in str(e):
        print("认证插件错误，尝试其他方法...")
        try:
            # 尝试不指定认证插件
            conn = pymysql.connect(
                host='localhost',
                port=3306,
                user='root',
                password='123456',
                charset='utf8mb4',
                autocommit=True,
                ssl_disabled=True
            )
            
            cursor = conn.cursor()
            cursor.execute("CREATE DATABASE IF NOT EXISTS course_selection_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            print("数据库创建成功！")
            
            cursor.close()
            conn.close()
        except Exception as e2:
            print(f"数据库连接失败: {e2}")
    else:
        print(f"数据库错误: {e}")
except Exception as e:
    print(f"未知错误: {e}")
