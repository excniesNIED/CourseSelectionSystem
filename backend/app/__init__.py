from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from dotenv import load_dotenv
import os

# 加载环境变量
load_dotenv()

# 初始化扩展
db = SQLAlchemy()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    
    # 配置
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-string-change-in-production')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False  # Token不过期，实际生产环境建议设置过期时间    # 数据库配置 - 临时使用 SQLite
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///course_selection.db'
    # MySQL 配置（备用）
    # app.config['SQLALCHEMY_DATABASE_URI'] = (
    #     f"mysql+pymysql://{os.getenv('DB_USER', 'root')}:"
    #     f"{os.getenv('DB_PASSWORD', 'password')}@"
    #     f"{os.getenv('DB_HOST', 'localhost')}:"
    #     f"{os.getenv('DB_PORT', '3306')}/"
    #     f"{os.getenv('DB_NAME', 'course_selection_system')}"
    #     f"?charset=utf8mb4&auth_plugin=mysql_native_password&connect_timeout=10"
    # )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # 初始化扩展
    db.init_app(app)
    jwt.init_app(app)
    CORS(app)
    
    # 注册蓝图
    from .routes.auth import auth_bp
    from .routes.admin import admin_bp
    from .routes.teacher import teacher_bp
    from .routes.student import student_bp
    from .routes.common import common_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(teacher_bp, url_prefix='/api/teacher')
    app.register_blueprint(student_bp, url_prefix='/api/student')
    app.register_blueprint(common_bp, url_prefix='/api/common')
    
    return app
