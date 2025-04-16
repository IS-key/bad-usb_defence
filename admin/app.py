# from flask import Flask, request, jsonify, redirect, url_for, render_template_string
# from flask_admin import Admin, AdminIndexView
# from flask_admin.contrib.sqla import ModelView
# from flask_sqlalchemy import SQLAlchemy
# from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
# from werkzeug.security import generate_password_hash, check_password_hash
# from datetime import datetime
#
# app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///devices.db'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.secret_key = '8-94123bafdsn,nmzc-dfa13-2489=adf@[iadf==0]'
#
# db = SQLAlchemy(app)
# login_manager = LoginManager(app)
# login_manager.login_view = 'login'
#
# # Модель пользователя для админки
# class AdminUser(UserMixin, db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(80), unique=True, nullable=False)
#     password_hash = db.Column(db.String(128))
#
#     def set_password(self, password):
#         self.password_hash = generate_password_hash(password)
#
#     def check_password(self, password):
#         return check_password_hash(self.password_hash, password)
#
# # Модель легального устройства
# class LegitDevice(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     pid = db.Column(db.String(50), nullable=False)
#     vid = db.Column(db.String(50), nullable=False)
#     iManufacturer = db.Column(db.String(255), nullable=False)
#     iProduct = db.Column(db.String(255), nullable=False)
#     iSerialNumber = db.Column(db.String(255), nullable=False)
#     employer_login = db.Column(db.String(100), nullable=False)
#     ipaddress = db.Column(db.String(100))
#     employer_hostname = db.Column(db.String(100))
#
# # Модель записи лога
# class LogEntry(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     event_type = db.Column(db.String(50), nullable=False)
#     username = db.Column(db.String(100), nullable=False)
#     hostname = db.Column(db.String(100), nullable=False)
#     ip_address = db.Column(db.String(100))
#     device_vid = db.Column(db.String(50))
#     device_pid = db.Column(db.String(50))
#     iManufacturer = db.Column(db.String(255), nullable=False)
#     iProduct = db.Column(db.String(255), nullable=False)
#     iSerialNumber = db.Column(db.String(255), nullable=False)
#     timestamp = db.Column(db.DateTime, default=datetime.utcnow)
#
# @login_manager.user_loader
# def load_user(user_id):
#     return AdminUser.query.get(int(user_id))
#
# class SecureModelView(ModelView):
#     def is_accessible(self):
#         return current_user.is_authenticated
#
#     def inaccessible_callback(self, name, **kwargs):
#         return redirect(url_for('login', next=request.url))
#
# class MyAdminIndexView(AdminIndexView):
#     def is_accessible(self):
#         return current_user.is_authenticated
#
#     def inaccessible_callback(self, name, **kwargs):
#         return redirect(url_for('login', next=request.url))
#
# admin = Admin(app, name='USB Device Admin', template_mode='bootstrap3', index_view=MyAdminIndexView())
#
# class LegitDeviceView(SecureModelView):
#     column_list = ('id', 'pid', 'vid', 'iManufacturer', 'iProduct', 'iSerialNumber', 'employer_login', 'ipaddress', 'employer_hostname')
#     form_columns = ('pid', 'vid', 'iManufacturer', 'iProduct', 'iSerialNumber', 'employer_login', 'ipaddress', 'employer_hostname')
#
# class LogEntryView(SecureModelView):
#     column_list = ('id', 'event_type', 'username', 'hostname', 'ip_address', 'device_vid', 'device_pid','iManufacturer', 'iProduct', 'iSerialNumber', 'timestamp')
#     can_create = False
#     can_edit = False
#     can_delete = True
#     column_filters = ('event_type', 'username', 'hostname')
#     column_searchable_list = ('username', 'hostname', 'device_vid', 'device_pid', 'iManufacturer', 'iProduct', 'iSerialNumber')
#
# admin.add_view(LegitDeviceView(LegitDevice, db.session))
# admin.add_view(LogEntryView(LogEntry, db.session))
#
# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         username = request.form.get('username')
#         password = request.form.get('password')
#         user = AdminUser.query.filter_by(username=username).first()
#         if user and user.check_password(password):
#             login_user(user)
#             next_page = request.args.get('next')
#             return redirect(next_page) if next_page else redirect(url_for('admin.index'))
#         return render_template_string('''
#             <h2>Login</h2>
#             <form method="POST">
#                 <div>
#                     <label for="username">Username:</label>
#                     <input type="text" id="username" name="username" required>
#                 </div>
#                 <div>
#                     <label for="password">Password:</label>
#                     <input type="password" id="password" name="password" required>
#                 </div>
#                 <button type="submit">Login</button>
#             </form>
#             <p style="color: red;">Invalid credentials</p>
#         ''')
#     return render_template_string('''
#         <h2>Login</h2>
#         <form method="POST">
#             <div>
#                 <label for="username">Username:</label>
#                 <input type="text" id="username" name="username" required>
#             </div>
#             <div>
#                 <label for="password">Password:</label>
#                 <input type="password" id="password" name="password" required>
#             </div>
#             <button type="submit">Login</button>
#         </form>
#     ''')
#
# @app.route('/logout')
# @login_required
# def logout():
#     logout_user()
#     return redirect(url_for('login'))
#
# @app.route('/')
# def index():
#     return "Welcome to the USB Device Admin Panel"
#
# @app.route('/api/devices', methods=['GET'])
# def api_devices():
#     devices = LegitDevice.query.all()
#     device_list = [{
#         'id': d.id,
#         'pid': d.pid,
#         'vid': d.vid,
#         'iManufacturer': d.iManufacturer,
#         'iProduct': d.iProduct,
#         'iSerialNumber': d.iSerialNumber,
#         'employer_login': d.employer_login,
#         'ipaddress': d.ipaddress,
#         'employer_hostname': d.employer_hostname
#     } for d in devices]
#
#     return jsonify(device_list), 200
#
# @app.route('/api/logs', methods=['GET'])
# def api_logs():
#     logs = LogEntry.query.order_by(LogEntry.timestamp.desc()).all()
#     log_list = [{
#         'id': l.id,
#         'event_type': l.event_type,
#         'username': l.username,
#         'hostname': l.hostname,
#         'ip_address': l.ip_address,
#         'device_vid': l.device_vid,
#         'device_pid': l.device_pid,
#         'iManufacturer': l.iManufacturer,
#         'iProduct': l.iProduct,
#         'iSerialNumber': l.iSerialNumber,
#         'timestamp': l.timestamp.strftime('%Y-%m-%d %H:%M:%S')
#     } for l in logs]
#
#     return jsonify(log_list), 200
#
# @app.route('/api/check_device', methods=["GET"])
# def check_device():
#     VID = request.args.get('idVendor')
#     PID = request.args.get('idProduct')
#     iManufacturer = request.args.get('iManufacturer')
#     iProduct = request.args.get('iProduct')
#     iSerialNumber = request.args.get('iSerialNumber')
#     if not iSerialNumber:
#         iSerialNumber = "0"
#     username = request.args.get('username')
#     hostname = request.args.get('hostname')
#     ip_address = request.args.get('ipaddress')
#
#     if not VID or not PID or not username or not hostname or not iManufacturer or not iProduct or not iSerialNumber:
#         return jsonify({'error': "Не хватает параметров"}), 400
#
#     log = LogEntry(
#         event_type="check",
#         username=username,
#         hostname=hostname,
#         ip_address=ip_address,
#         device_vid=VID,
#         device_pid=PID,
#         iManufacturer=iManufacturer,
#         iProduct=iProduct,
#         iSerialNumber=iSerialNumber
#     )
#     db.session.add(log)
#
#     device = LegitDevice.query.filter_by(
#         pid=PID,
#         vid=VID,
#         iManufacturer=iManufacturer,
#         iProduct=iProduct,
#         iSerialNumber=iSerialNumber,
#         employer_login=username,
#         employer_hostname=hostname,
#         ipaddress=ip_address,
#     ).first()
#
#     db.session.commit()
#     if device:
#         return jsonify({
#             "legit": True
#         }), 200
#     return jsonify({
#         "legit": False
#     }), 401
#
# @app.route('/api/warning', methods=['POST'])
# def warning():
#     username = request.form.get('username')
#     hostname = request.form.get('hostname')
#     ip_address = request.form.get('local_ip')
#     iManufacturer = request.args.get('iManufacturer')
#     iProduct = request.args.get('iProduct')
#     iSerialNumber = request.args.get('iSerialNumber')
#     idProduct = request.form.get('idProduct')
#     idVendor = request.form.get('idVendor')
#
#     if not username or not hostname:
#         return jsonify({'error': 'Отсутствуют обязательные параметры'}), 400
#
#     log = LogEntry(
#         event_type="warning",
#         username=username,
#         hostname=hostname,
#         ip_address=ip_address,
#         device_vid=idVendor,
#         device_pid=idProduct,
#         iManufacturer=iManufacturer,
#         iProduct=iProduct,
#         iSerialNumber=iSerialNumber
#     )
#     db.session.add(log)
#     db.session.commit()
#
#     return jsonify({"message": "Warning received and logged"}), 200
#
#
# @app.cli.command('init-admin')
# def init_admin():
#     import getpass
#
#     while True:
#         username = input("Логин администратора: ").strip()
#         if not username:
#             print("Логин не может быть пустым!")
#             continue
#
#         if AdminUser.query.filter_by(username=username).first():
#             print("Этот логин уже занят!")
#             continue
#
#         break
#
#     while True:
#         password = getpass.getpass("Пароль: ")
#         if len(password) < 8:
#             print("Пароль должен содержать минимум 8 символов!")
#             continue
#
#         password_confirm = getpass.getpass("Подтвердите пароль: ")
#         if password != password_confirm:
#             print("Пароли не совпадают!")
#             continue
#
#         break
#
#     admin = AdminUser(username=username)
#     admin.set_password(password)
#     db.session.add(admin)
#     db.session.commit()
#
#     print(f"\nАдминистратор {username} успешно создан!")
#     print("Сохраните эти данные в безопасном месте!")
#
#
# if __name__ == '__main__':
#     with app.app_context():
#         db.create_all()
#         if not AdminUser.query.filter_by(username='admin').first():
#             print('Установите администратора. Запустите flask init-admin')
#             exit(1)
#     app.run(debug=True)

from flask import Flask, request, jsonify, redirect, url_for, render_template_string
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///devices.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your-secret-key-here'

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class AdminUser(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class LegitDevice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pid = db.Column(db.String(50), nullable=False)
    vid = db.Column(db.String(50), nullable=False)
    iManufacturer = db.Column(db.String(255), nullable=False)
    iProduct = db.Column(db.String(255), nullable=False)
    iSerialNumber = db.Column(db.String(255), nullable=False, default="0")
    employer_login = db.Column(db.String(100), nullable=False)
    ipaddress = db.Column(db.String(100))
    employer_hostname = db.Column(db.String(100))

    def __repr__(self):
        return f"<Device {self.iManufacturer} {self.iProduct} (VID:{self.vid}, PID:{self.pid})>"

class LogEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_type = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(100), nullable=False)
    hostname = db.Column(db.String(100), nullable=False)
    ip_address = db.Column(db.String(100))
    device_vid = db.Column(db.String(50))
    device_pid = db.Column(db.String(50))
    iManufacturer = db.Column(db.String(255), nullable=False)
    iProduct = db.Column(db.String(255), nullable=False)
    iSerialNumber = db.Column(db.String(255), nullable=False, default="0")
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return AdminUser.query.get(int(user_id))

class SecureModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login', next=request.url))

class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login', next=request.url))

admin = Admin(app, name='USB Device Admin', template_mode='bootstrap3', index_view=MyAdminIndexView())

class LegitDeviceView(SecureModelView):
    column_list = ('id', 'pid', 'vid', 'iManufacturer', 'iProduct', 'iSerialNumber', 'employer_login', 'ipaddress', 'employer_hostname')
    form_columns = ('pid', 'vid', 'iManufacturer', 'iProduct', 'iSerialNumber', 'employer_login', 'ipaddress', 'employer_hostname')
    column_searchable_list = ('iManufacturer', 'iProduct', 'iSerialNumber', 'employer_login')
    column_filters = ('pid', 'vid', 'iManufacturer')

class LogEntryView(SecureModelView):
    column_list = ('id', 'event_type', 'username', 'hostname', 'ip_address', 'device_vid', 'device_pid', 'iManufacturer', 'iProduct', 'iSerialNumber', 'timestamp')
    can_create = False
    can_edit = False
    can_delete = True
    column_filters = ('event_type', 'username', 'hostname', 'iManufacturer')
    column_searchable_list = ('username', 'hostname', 'device_vid', 'device_pid', 'iManufacturer', 'iProduct', 'iSerialNumber')

admin.add_view(LegitDeviceView(LegitDevice, db.session))
admin.add_view(LogEntryView(LogEntry, db.session))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = AdminUser.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('admin.index'))
        return render_template_string('''
            <h2>Login</h2>
            <form method="POST">
                <div>
                    <label for="username">Username:</label>
                    <input type="text" id="username" name="username" required>
                </div>
                <div>
                    <label for="password">Password:</label>
                    <input type="password" id="password" name="password" required>
                </div>
                <button type="submit">Login</button>
            </form>
            <p style="color: red;">Invalid credentials</p>
        ''')
    return render_template_string('''
        <h2>Login</h2>
        <form method="POST">
            <div>
                <label for="username">Username:</label>
                <input type="text" id="username" name="username" required>
            </div>
            <div>
                <label for="password">Password:</label>
                <input type="password" id="password" name="password" required>
            </div>
            <button type="submit">Login</button>
        </form>
    ''')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
def index():
    return "Welcome to the USB Device Admin Panel"

@app.route('/api/check_device', methods=["GET"])
def check_device():
    # Получаем параметры из запроса
    vid = request.args.get('idVendor', '').lower().replace('0x', '')
    pid = request.args.get('idProduct', '').lower().replace('0x', '')
    iManufacturer = request.args.get('iManufacturer', '0')
    iProduct = request.args.get('iProduct', '0')
    iSerialNumber = request.args.get('iSerialNumber', '0')
    username = request.args.get('username', '')
    hostname = request.args.get('hostname', '')
    ip_address = request.args.get('ipaddress', '')

    # Проверяем обязательные параметры
    if not vid or not pid or not username or not hostname:
        return jsonify({'error': "Missing required parameters"}), 400

    # Нормализуем серийный номер
    if not iSerialNumber or iSerialNumber == 'None':
        iSerialNumber = '0'

    # Создаем запись в логе
    log_entry = LogEntry(
        event_type="check",
        username=username,
        hostname=hostname,
        ip_address=ip_address,
        device_vid=vid,
        device_pid=pid,
        iManufacturer=iManufacturer,
        iProduct=iProduct,
        iSerialNumber=iSerialNumber
    )
    db.session.add(log_entry)

    # Ищем устройство в базе
    device = LegitDevice.query.filter_by(
        vid=vid,
        pid=pid,
        iManufacturer=iManufacturer,
        iProduct=iProduct,
        iSerialNumber=iSerialNumber,
        employer_login=username
    ).first()

    db.session.commit()

    if device:
        return jsonify({"legit": True}), 200
    return jsonify({"legit": False}), 401

@app.route('/api/warning', methods=['POST'])
def warning():
    # Получаем данные из формы
    username = request.form.get('username', '')
    hostname = request.form.get('hostname', '')
    ip_address = request.form.get('local_ip', '')
    iManufacturer = request.form.get('iManufacturer', '0')
    iProduct = request.form.get('iProduct', '0')
    iSerialNumber = request.form.get('iSerialNumber', '0')
    pid = request.form.get('idProduct', '').lower().replace('0x', '')
    vid = request.form.get('idVendor', '').lower().replace('0x', '')

    # Нормализуем серийный номер
    if not iSerialNumber or iSerialNumber == 'None':
        iSerialNumber = '0'

    # Проверяем обязательные параметры
    if not username or not hostname or not pid or not vid:
        return jsonify({'error': 'Missing required parameters'}), 400

    # Создаем запись в логе
    log_entry = LogEntry(
        event_type="warning",
        username=username,
        hostname=hostname,
        ip_address=ip_address,
        device_vid=vid,
        device_pid=pid,
        iManufacturer=iManufacturer,
        iProduct=iProduct,
        iSerialNumber=iSerialNumber
    )
    db.session.add(log_entry)
    db.session.commit()

    return jsonify({"message": "Warning logged successfully"}), 200

@app.cli.command('init-admin')
def init_admin():
    """Команда для создания администратора"""
    import getpass

    while True:
        username = input("Admin username: ").strip()
        if not username:
            print("Username cannot be empty!")
            continue

        if AdminUser.query.filter_by(username=username).first():
            print("Username already exists!")
            continue

        break

    while True:
        password = getpass.getpass("Password: ")
        if len(password) < 8:
            print("Password must be at least 8 characters!")
            continue

        password_confirm = getpass.getpass("Confirm password: ")
        if password != password_confirm:
            print("Passwords don't match!")
            continue

        break

    admin = AdminUser(username=username)
    admin.set_password(password)
    db.session.add(admin)
    db.session.commit()

    print(f"\nAdmin user {username} created successfully!")
    print("Please store these credentials securely!")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        if not AdminUser.query.filter_by(username='admin').first():
            print('Please create an admin user first. Run: flask init-admin')
            exit(1)
    app.run(host='0.0.0.0', port=5000, debug=True)