from app import create_app, db

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        # 创建数据库表（如果不存在）
        db.create_all()
    
    app.run(debug=True, host='0.0.0.0', port=5000)
