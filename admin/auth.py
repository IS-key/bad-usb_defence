# -*- coding: utf-8 -*-
import getpass

from flask import Flask, request, redirect, url_for, session, render_template_string
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Настройка PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://test:test@172.20.10.2:5432/usb_control'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Модель User
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


def init_db():
    with app.app_context():
        # Создаем таблицы
        db.create_all()

        # Запрашиваем пароль для admin
        admin_password = getpass.getpass("Введите пароль для пользователя admin: ")

        # Проверяем, что пароль не пустой
        while not admin_password.strip():
            print("Пароль не может быть пустым!")
            admin_password = getpass.getpass("Введите пароль для пользователя admin: ")

        # Создаем/обновляем пользователя admin
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(username='admin')
            print("Создаем нового пользователя admin")
        else:
            print("Обновляем пароль для существующего пользователя admin")

        admin.set_password(admin_password)
        db.session.add(admin)
        db.session.commit()
        print("Пароль для admin успешно установлен!")

# Создаем таблицы и пользователя admin при первом запуске
# @app.before_first_request
# def create_tables():
#     db.create_all()
#     if not User.query.filter_by(username='admin').first():
#         admin = User(username='admin')
#         admin.set_password('admin')
#         db.session.add(admin)
#         db.session.commit()

# CSS стили
CSS = """
<style>
    body {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        margin: 0;
        padding: 0;
        height: 100vh;
        display: flex;
        justify-content: center;
        align-items: center;
        color: #333;
    }
    .login-container {
        background: white;
        padding: 2rem 3rem;
        border-radius: 10px;
        box-shadow: 0 15px 30px rgba(0, 0, 0, 0.1);
        width: 100%;
        max-width: 400px;
        text-align: center;
    }
    h1 {
        color: #2c3e50;
        margin-bottom: 1.5rem;
    }
    .form-group {
        margin-bottom: 1.5rem;
        text-align: left;
    }
    label {
        display: block;
        margin-bottom: 0.5rem;
        font-weight: 600;
        color: #2c3e50;
    }
    input {
        width: 100%;
        padding: 0.8rem;
        border: 1px solid #ddd;
        border-radius: 5px;
        font-size: 1rem;
        box-sizing: border-box;
    }
    input:focus {
        outline: none;
        border-color: #667eea;
        box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2);
    }
    button {
        background: #667eea;
        color: white;
        border: none;
        padding: 1rem 2rem;
        border-radius: 5px;
        font-size: 1rem;
        cursor: pointer;
        width: 100%;
        font-weight: 600;
        transition: background 0.3s;
    }
    button:hover {
        background: #5a6fd1;
    }
    .error-message {
        color: #e74c3c;
        margin: 1rem 0;
    }
    .login-footer {
        margin-top: 1.5rem;
        font-size: 0.9rem;
        color: #7f8c8d;
    }
    .back-link {
        color: #667eea;
        text-decoration: none;
        font-weight: 600;
    }
    .back-link:hover {
        text-decoration: underline;
    }
</style>
"""

# HTML шаблон для формы входа
LOGIN_FORM = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Вход в систему</title>
    {css}
</head>
<body>
    <div class="login-container">
        <h1>Вход в систему</h1>
        <form method="POST">
            <div class="form-group">
                <label for="username">Имя пользователя</label>
                <input type="text" id="username" name="username" required placeholder="Введите ваш логин">
            </div>
            <div class="form-group">
                <label for="password">Пароль</label>
                <input type="password" id="password" name="password" required placeholder="Введите ваш пароль">
            </div>
            <button type="submit">Войти</button>
        </form>
        <div class="login-footer">
        </div>
    </div>
</body>
</html>
""".format(css=CSS)

ERROR_FORM = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ошибка входа</title>
    {css}
</head>
<body>
    <div class="login-container">
        <h1>Ошибка входа</h1>
        <div class="error-message">
            <p>Неверное имя пользователя или пароль</p>
        </div>
        <a href="/" class="back-link">Попробовать снова</a>
    </div>
</body>
</html>
""".format(css=CSS)

# Главная страница с формой входа
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            session['logged_in'] = True
            session['username'] = username
            return redirect('http://localhost:3000')
        else:
            return render_template_string(ERROR_FORM)

    return render_template_string(LOGIN_FORM)

# Выход из системы
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    return redirect('/')

init_db()

if __name__ == '__main__':
    app.run(debug=True, port=3800)
