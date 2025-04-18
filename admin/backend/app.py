from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
from werkzeug.middleware.proxy_fix import ProxyFix

app = Flask(__name__)
CORS(app)
app.wsgi_app = ProxyFix(app.wsgi_app)

# Конфигурация базы данных
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://test:test@172.20.10.2:5432/usb_control'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Модели данных
class Device(db.Model):
    __tablename__ = 'devices'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    vid = db.Column(db.String(10), nullable=False)
    pid = db.Column(db.String(10), nullable=False)
    serial_number = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255))
    added_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'vid': self.vid,
            'pid': self.pid,
            'serial_number': self.serial_number,
            'description': self.description,
            'added_date': self.added_date.isoformat()
        }

class Log(db.Model):
    __tablename__ = 'logs'
    
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    device_name = db.Column(db.String(100))
    vid = db.Column(db.String(10))
    pid = db.Column(db.String(10))
    serial_number = db.Column(db.String(100))
    status = db.Column(db.String(20))  # allowed or blocked
    computer_name = db.Column(db.String(100))
    ip_address = db.Column(db.String(50))
    user_name = db.Column(db.String(100))
    
    def to_dict(self):
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat(),
            'device_name': self.device_name,
            'vid': self.vid,
            'pid': self.pid,
            'serial_number': self.serial_number,
            'status': self.status,
            'computer_name': self.computer_name,
            'ip_address': self.ip_address,
            'user': self.user_name
        }

class Client(db.Model):
    __tablename__ = 'clients'
    
    id = db.Column(db.Integer, primary_key=True)
    computer_name = db.Column(db.String(100), nullable=False)
    ip_address = db.Column(db.String(50), nullable=False)
    user_name = db.Column(db.String(100))
    os = db.Column(db.String(50))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='online')  # online or offline
    version = db.Column(db.String(20))
    
    def to_dict(self):
        return {
            'id': self.id,
            'computer_name': self.computer_name,
            'ip_address': self.ip_address,
            'user': self.user_name,
            'os': self.os,
            'last_seen': self.last_seen.isoformat(),
            'status': self.status,
            'version': self.version
        }

# API маршруты для устройств
@app.route('/api/devices', methods=['GET'])
def get_devices():
    devices = Device.query.all()
    return jsonify([device.to_dict() for device in devices])

@app.route('/api/devices', methods=['POST'])
def add_device():
    data = request.json
    
    # Проверка обязательных полей
    required_fields = ['name', 'vid', 'pid', 'serial_number']
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({'message': f'Поле {field} обязательно'}), 400
    
    # Проверка на дубликаты
    existing_device = Device.query.filter_by(
        vid=data['vid'], 
        pid=data['pid'], 
        serial_number=data['serial_number']
    ).first()
    
    if existing_device:
        return jsonify({'message': 'Устройство с такими параметрами уже существует'}), 400
    
    # Создание нового устройства
    new_device = Device(
        name=data['name'],
        vid=data['vid'],
        pid=data['pid'],
        serial_number=data['serial_number'],
        description=data.get('description', '')
    )
    
    db.session.add(new_device)
    db.session.commit()
    
    return jsonify(new_device.to_dict()), 201

@app.route('/api/devices/<int:device_id>', methods=['PUT'])
def update_device(device_id):
    device = Device.query.get_or_404(device_id)
    data = request.json
    
    # Обновление полей
    device.name = data.get('name', device.name)
    device.vid = data.get('vid', device.vid)
    device.pid = data.get('pid', device.pid)
    device.serial_number = data.get('serial_number', device.serial_number)
    device.description = data.get('description', device.description)
    
    db.session.commit()
    
    return jsonify(device.to_dict())

@app.route('/api/devices/<int:device_id>', methods=['DELETE'])
def delete_device(device_id):
    device = Device.query.get_or_404(device_id)
    
    db.session.delete(device)
    db.session.commit()
    
    return jsonify({'message': 'Устройство удалено'})

# API маршруты для логов
@app.route('/api/logs', methods=['GET'])
def get_logs():
    logs = Log.query.order_by(Log.timestamp.desc()).all()
    return jsonify([log.to_dict() for log in logs])

@app.route('/api/logs', methods=['POST'])
def add_log():
    data = request.json
    
    new_log = Log(
        device_name=data.get('device_name', ''),
        vid=data.get('vid', ''),
        pid=data.get('pid', ''),
        serial_number=data.get('serial_number', ''),
        status=data.get('status', 'blocked'),
        computer_name=data.get('computer_name', ''),
        ip_address=data.get('ip_address', ''),
        user=data.get('user', '')
    )
    
    db.session.add(new_log)
    db.session.commit()
    
    return jsonify(new_log.to_dict()), 201

# API маршруты для клиентов
@app.route('/api/clients', methods=['GET'])
def get_clients():
    clients = Client.query.all()
    return jsonify([client.to_dict() for client in clients])

@app.route('/api/clients', methods=['POST'])
def register_client():
    data = request.json
    
    # Проверка существования клиента
    existing_client = Client.query.filter_by(
        computer_name=data.get('computer_name'),
        ip_address=data.get('ip_address')
    ).first()
    
    if existing_client:
        # Обновление существующего клиента
        existing_client.user_name = data.get('user', existing_client.user_name)
        existing_client.os = data.get('os', existing_client.os)
        existing_client.last_seen = datetime.utcnow()
        existing_client.status = 'online'
        existing_client.version = data.get('version', existing_client.version)
        
        db.session.commit()
        return jsonify(existing_client.to_dict())
    
    # Создание нового клиента
    new_client = Client(
        computer_name=data.get('computer_name'),
        ip_address=data.get('ip_address'),
        user_name=data.get('user', ''),
        os=data.get('os', ''),
        version=data.get('version', '1.0.0')
    )
    
    db.session.add(new_client)
    db.session.commit()
    
    return jsonify(new_client.to_dict()), 201

@app.route('/api/clients/<int:client_id>', methods=['PUT'])
def update_client_status(client_id):
    client = Client.query.get_or_404(client_id)
    data = request.json
    
    client.status = data.get('status', client.status)
    client.last_seen = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify(client.to_dict())

# API маршрут для проверки устройства
@app.route('/api/check_device', methods=['POST'])
def check_device():
    data = request.json
    
    # Проверка наличия устройства в белом списке
    device = Device.query.filter_by(
        vid=data.get('vid', ''),
        pid=data.get('pid', ''),
        serial_number=data.get('serial_number', '')
    ).first()
    
    # Логирование подключения
    new_log = Log(
        device_name=data.get('device_name', 'Неизвестное устройство'),
        vid=data.get('vid', ''),
        pid=data.get('pid', ''),
        serial_number=data.get('serial_number', ''),
        status='allowed' if device else 'blocked',
        computer_name=data.get('computer_name', ''),
        ip_address=data.get('ip_address', ''),
        user_name=data.get('user', '')
    )
    
    db.session.add(new_log)
    db.session.commit()
    
    if device:
        return jsonify({
            'allowed': True,
            'device': device.to_dict()
        })
    else:
        return jsonify({
            'allowed': False,
            'message': 'Устройство не найдено в белом списке'
        }), 400

# Инициализация базы данных
@app.before_first_request
def create_tables():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
