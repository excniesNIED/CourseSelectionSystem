# 教务系统选课系统

一个基于Vue 3 + Python Flask的前后端分离教务系统选课管理平台。

## 技术栈

### 前端
- Vue 3
- Vite
- JavaScript
- Material Design 3 (Vuetify 3)
- Vue Router
- Pinia (状态管理)

### 后端
- Python Flask
- SQLAlchemy
- Flask-JWT-Extended (JWT认证)
- Flask-CORS (跨域处理)
- PyMySQL (数据库连接)

### 数据库
- MariaDB

## 项目结构

```
CourseSelectionSystem/
├── frontend/                 # Vue前端项目
│   ├── src/
│   │   ├── components/      # 组件
│   │   ├── views/           # 页面视图
│   │   ├── router/          # 路由配置
│   │   ├── stores/          # 状态管理
│   │   └── utils/           # 工具函数
│   ├── package.json
│   └── vite.config.js
├── backend/                  # Python后端项目
│   ├── app/
│   │   ├── models/          # 数据模型
│   │   ├── routes/          # 路由控制器
│   │   ├── utils/           # 工具函数
│   │   └── __init__.py
│   ├── requirements.txt
│   └── run.py
├── database/                 # 数据库脚本
│   └── init.sql             # 数据库初始化脚本
└── README.md
```

## 功能特性

### 管理员功能
- 教师信息管理（增删改查）
- 学生信息管理（增删改查）
- 课程信息管理（增删改查）
- 密码修改

### 教师功能
- 查看个人信息
- 查看任课信息
- 开设/取消课程
- 学生成绩管理
- 班级学生排名查看
- 课程成绩统计
- 密码修改

### 学生功能
- 查看个人信息
- 查看已选课程
- 选课/退选
- 成绩查询
- 密码修改

## 快速开始

### 1. 数据库设置
- 安装MariaDB
- 创建数据库
- 执行 `database/init.sql` 初始化表结构

### 2. 后端设置
```bash
cd backend
pip install -r requirements.txt
python run.py
```

### 3. 前端设置
```bash
cd frontend
npm install
npm run dev
```

## 数据库设计

系统包含以下主要实体：
- 班级 (Class)
- 学生 (Student)
- 课程 (Course)
- 教师 (Teacher)
- 开课情况 (CourseOffering)
- 选课情况 (Enrollment)

详细的数据库设计请参考 `需求.md` 文件。
