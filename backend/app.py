from flask import Flask
from backend.config import init_db
from backend.routes.user_routes import user_bp
import os

app = Flask(__name__)
# 初始化数据库
db = init_db(app)

# 注册蓝图
app.register_blueprint(user_bp)

# 创建数据库表
@app.before_first_request
def create_tables():
    db.create_all()
    # 初始化管理员用户
    from backend.models import User
    if not User.query.filter_by(username='admin').first():
        from werkzeug.security import generate_password_hash
        admin = User(
            username='admin',
            password=generate_password_hash('admin123', method='sha256'),
            role_id=1,
            real_name='系统管理员'
        )
        db.session.add(admin)
        db.session.commit()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)