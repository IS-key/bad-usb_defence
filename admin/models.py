from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class LegitDevice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pid = db.Column(db.String(255), nullable=False)
    vid = db.Column(db.String(255), nullable=False)
    iManufacturer = db.Column(db.String(255), nullable=False)
    iProduct = db.Column(db.String(255), nullable=False)
    iSerialNumber = db.Column(db.String(255), nullable=False)
    employer_login = db.Column(db.String(255), nullable=False)
    ipaddress = db.Column(db.String(255), nullable=False)
    employer_hostname = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f"<LegitDevice {self.pid}-{self.vid}>"


from datetime import datetime

class LogEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_type = db.Column(db.String(50), nullable=False)  # 'warning' или 'check'
    username = db.Column(db.String(255))
    hostname = db.Column(db.String(255))
    ip_address = db.Column(db.String(255))
    device_vid = db.Column(db.String(255), nullable=True)
    device_pid = db.Column(db.String(255), nullable=True)
    iManufacturer = db.Column(db.String(255), nullable=False)
    iProduct = db.Column(db.String(255), nullable=False)
    iSerialNumber = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<LogEntry {self.event_type} at {self.timestamp}>"

