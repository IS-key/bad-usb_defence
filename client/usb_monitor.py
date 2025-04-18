# import sys
# import os
# import socket
# import json
# from pathlib import Path
# from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
#                              QLabel, QTextEdit, QPushButton, QHBoxLayout,
#                              QSystemTrayIcon, QMenu, QMessageBox)
# from PyQt5.QtCore import QTimer, Qt
# from PyQt5.QtGui import QFont, QIcon
# import usb.core
# import usb.util
# from datetime import datetime
# import requests
# import time
#
# # Константы
# API_URL = "http://localhost:5000/api"
# COMPANY_NAME = "Your Company"
# ALLOW_EXIT = False
# CONFIG_DIR = Path.home() / ".usb_monitor"
# CONFIG_FILE = CONFIG_DIR / "known_devices.json"
#
#
# def get_usb_string(dev, index):
#     """Получает строковый дескриптор USB устройства"""
#     if index == 0:
#         return 0
#     try:
#         langids = dev.langids
#         if langids:
#             try:
#                 return usb.util.get_string(dev, index, langids[0])
#             except usb.core.USBError:
#                 return 0
#     except:
#         return 0
#
#
# def load_known_devices():
#     """Загружает список известных устройств из файла"""
#     try:
#         if CONFIG_FILE.exists():
#             with open(CONFIG_FILE, 'r') as f:
#                 return json.load(f)
#     except Exception as e:
#         print(f"Ошибка загрузки известных устройств: {e}")
#     return []
#
#
# def save_known_devices(devices):
#     """Сохраняет список известных устройств в файл"""
#     try:
#         CONFIG_DIR.mkdir(exist_ok=True)
#         with open(CONFIG_FILE, 'w') as f:
#             json.dump(devices, f)
#     except Exception as e:
#         print(f"Ошибка сохранения известных устройств: {e}")
#
#
# def get_current_devices():
#     try:
#         devices = []
#         for dev in usb.core.find(find_all=True):
#             if dev is not None:
#                 manufacturer = get_usb_string(dev, dev.iManufacturer)
#                 product = get_usb_string(dev, dev.iProduct)
#                 serial = get_usb_string(dev, dev.iSerialNumber)
#                 devices.append((dev.idVendor, dev.idProduct, manufacturer, product, serial))
#         return devices
#     except Exception as e:
#         print(f"Ошибка получения текущих устройств: {e}")
#         return []
#
#
# def check_device(idVendor, idProduct, iManufacturer, iProduct, iSerialNumber):
#     url = f'{API_URL}/check_device?idVendor={hex(idVendor)}&idProduct={hex(idProduct)}&username={os.getlogin()}&hostname={socket.gethostname()}&ipaddress={get_local_ip()}&iManufacturer={iManufacturer}&iProduct={iProduct}&iSerialNumber={iSerialNumber}'
#     print('Запрос отправлен')
#     try:
#         response = requests.get(url=url, timeout=5)
#         if response.status_code == 200 and response.json().get('legit', False):
#             print('Устройство проверено')
#             return True
#     except Exception as e:
#         print(f'Ошибка проверки устройства: {e}')
#     return False
#
#
# def get_local_ip():
#     try:
#         s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#         s.connect(("8.8.8.8", 80))
#         local_ip = s.getsockname()[0]
#         s.close()
#         return local_ip
#     except Exception:
#         return "127.0.0.1"
#
#
# def send_warning_to_admin(idProduct, idVendor, iManufacturer, iProduct, iSerialNumber):
#     username = os.getlogin()
#     hostname = socket.gethostname()
#     time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#     ip_address = get_local_ip()
#     url = f'{API_URL}/warning'
#
#     data = {
#         "username": username,
#         "hostname": hostname,
#         "time": time_str,
#         "local_ip": ip_address,
#         "idProduct": hex(idProduct),
#         "idVendor": hex(idVendor),
#         "iManufacturer": iManufacturer,
#         "iProduct": iProduct,
#         "iSerialNumber": iSerialNumber
#     }
#
#     try:
#         requests.post(url, data=data, timeout=5)
#     except Exception as e:
#         print(f'Ошибка отправки предупреждения: {e}')
#
#
# class USBMonitorGUI(QMainWindow):
#     def __init__(self):
#         super().__init__()
#         self.setWindowTitle(f"USB Device Monitor - {COMPANY_NAME}")
#         self.setGeometry(100, 100, 600, 400)
#         self.setWindowIcon(QIcon("icon.png"))
#
#         self.init_ui()
#
#         self.initial_devices = self.get_current_usb_devices()
#         self.verified_devices = set((dev[0], dev[1]) for dev in self.initial_devices)
#         self.suspicious_devices = set()
#
#         self.tray_icon = QSystemTrayIcon(self)
#         self.tray_icon.setIcon(QIcon("icon.png"))
#
#         tray_menu = QMenu()
#         show_action = tray_menu.addAction("Показать")
#         show_action.triggered.connect(self.show_normal)
#         exit_action = tray_menu.addAction("Выход")
#         exit_action.triggered.connect(self.close)
#
#         self.tray_icon.setContextMenu(tray_menu)
#         self.tray_icon.show()
#
#         self.known_devices = load_known_devices()
#         self.first_run = len(self.known_devices) == 0
#
#         if self.first_run:
#             current_devices = get_current_devices()
#             save_known_devices(current_devices)
#             self.known_devices = current_devices
#             self.log("Первоначальная инициализация: сохранены подключенные устройства")
#
#         self.devices = list(self.known_devices)
#         self.seen_devices = []
#
#         self.timer = QTimer()
#         self.timer.timeout.connect(self.check_usb_devices)
#         self.timer.start(1000)
#
#     def init_ui(self):
#         self.central_widget = QWidget()
#         self.setCentralWidget(self.central_widget)
#
#         self.layout = QVBoxLayout()
#         self.central_widget.setLayout(self.layout)
#
#         self.log_area = QTextEdit()
#         self.log_area.setReadOnly(True)
#         self.log_area.setFont(QFont("Courier", 10))
#         self.layout.addWidget(self.log_area)
#
#         buttons_layout = QHBoxLayout()
#
#         self.clear_button = QPushButton("Очистить лог")
#         self.clear_button.clicked.connect(self.clear_log)
#         buttons_layout.addWidget(self.clear_button)
#
#         self.exit_button = QPushButton("Выход")
#         self.exit_button.clicked.connect(self.close)
#         buttons_layout.addWidget(self.exit_button)
#
#         self.layout.addLayout(buttons_layout)
#
#     def log(self, message):
#         self.log_area.append(message)
#         print(message)
#
#     def clear_log(self):
#         self.log_area.clear()
#
#     def show_normal(self):
#         self.showNormal()
#         self.activateWindow()
#
#     def get_current_usb_devices(self):
#         try:
#             devices = []
#             for dev in usb.core.find(find_all=True):
#                 if dev is not None:
#                     manufacturer = get_usb_string(dev, dev.iManufacturer)
#                     product = get_usb_string(dev, dev.iProduct)
#                     serial = get_usb_string(dev, dev.iSerialNumber)
#                     devices.append((dev.idVendor, dev.idProduct, manufacturer, product, serial))
#             return devices
#         except:
#             return []
#
#     def verify_device(self, vid, pid, manufacturer, product, serial):
#         try:
#             return check_device(vid, pid, manufacturer, product, serial)
#         except Exception as e:
#             self.log(f"Ошибка проверки устройства: {e}")
#             return False
#
#     def check_usb_devices(self):
#         current_devices = self.get_current_usb_devices()
#         current_ids = set((dev[0], dev[1]) for dev in current_devices)
#
#         new_devices = [dev for dev in current_devices
#                        if (dev[0], dev[1]) not in self.verified_devices
#                        and (dev[0], dev[1]) not in self.suspicious_devices]
#
#         for vid, pid, manufacturer, product, serial in new_devices:
#             log_msg = f"Проверяем устройство: VID={hex(vid)}, PID={hex(pid)}"
#             if manufacturer != 0:
#                 log_msg += f", Производитель: {manufacturer}"
#             if product != 0:
#                 log_msg += f", Устройство: {product}"
#             if serial != 0:
#                 log_msg += f", Серийный: {serial}"
#             self.log(log_msg)
#
#             if self.verify_device(vid, pid, manufacturer, product, serial):
#                 self.verified_devices.add((vid, pid))
#                 self.log(f"Устройство подтверждено: {product if product != 0 else 'Unknown'}")
#             else:
#                 self.suspicious_devices.add((vid, pid))
#                 self.log(f"ВНИМАНИЕ: Неавторизованное устройство!")
#                 send_warning_to_admin(pid, vid, manufacturer, product, serial)
#
#     def closeEvent(self, event):
#         if not ALLOW_EXIT:
#             self.hide()
#             event.ignore()
#         else:
#             self.tray_icon.hide()
#             event.accept()
#
#
# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     app.setQuitOnLastWindowClosed(False)
#
#     try:
#         list(usb.core.find(find_all=True))
#         window = USBMonitorGUI()
#         window.show()
#         sys.exit(app.exec_())
#     except usb.core.NoBackendError:
#         error_msg = QLabel(
#             "Ошибка: Не найдена библиотека для работы с USB.\nУстановите libusb (Linux: sudo apt install libusb-1.0-0-dev)")
#         error_msg.show()
#         app.exec_()
#     except Exception as e:
#         error_msg = QLabel(f"Ошибка запуска: {str(e)}")
#         error_msg.show()
#         app.exec_()

import sys
import os
import socket
import json
from pathlib import Path
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QLabel, QTextEdit, QPushButton, QHBoxLayout,
                             QSystemTrayIcon, QMenu, QMessageBox)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QFont, QIcon
import usb.core
import usb.util
from datetime import datetime
import requests
import time

# Константы
API_URL = "http://localhost:5000/api"  # Базовый URL API
COMPANY_NAME = "Your Company"
ALLOW_EXIT = False
CONFIG_DIR = Path.home() / ".usb_monitor"
CONFIG_FILE = CONFIG_DIR / "known_devices.json"


def get_usb_string(dev, index):
    """Получает строковый дескриптор USB устройства"""
    if index == 0:
        return 0
    try:
        langids = dev.langids
        if langids:
            try:
                return usb.util.get_string(dev, index, langids[0])
            except usb.core.USBError:
                return 0
    except:
        return 0


def load_known_devices():
    """Загружает список известных устройств из файла"""
    try:
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"Ошибка загрузки известных устройств: {e}")
    return []


def save_known_devices(devices):
    """Сохраняет список известных устройств в файл"""
    try:
        CONFIG_DIR.mkdir(exist_ok=True)
        with open(CONFIG_FILE, 'w') as f:
            json.dump(devices, f)
    except Exception as e:
        print(f"Ошибка сохранения известных устройств: {e}")


def get_current_devices():
    try:
        devices = []
        for dev in usb.core.find(find_all=True):
            if dev is not None:
                manufacturer = get_usb_string(dev, dev.iManufacturer)
                product = get_usb_string(dev, dev.iProduct)
                serial = get_usb_string(dev, dev.iSerialNumber)
                devices.append((dev.idVendor, dev.idProduct, manufacturer, product, serial))
        return devices
    except Exception as e:
        print(f"Ошибка получения текущих устройств: {e}")
        return []


def check_device(vid, pid, manufacturer, product, serial_number):
    """Проверяет устройство через API"""
    data = {
        'vid': str(hex(vid)).replace("0x", ""),
        'pid': str(hex(pid)).replace('0x', ''),
        'serial_number': str(serial_number) if serial_number != 0 else '',
        'device_name': str(product) if product != 0 else 'Unknown',
        'computer_name': socket.gethostname(),
        'ip_address': get_local_ip(),
        'user': os.getlogin()
    }

    try:
        response = requests.post(f'{API_URL}/check_device', json=data, timeout=5)
        if response.status_code == 200:
            result = response.json()
            return result.get('allowed', False)
    except Exception as e:
        print(f'Ошибка проверки устройства: {e}')
    return False


def get_local_ip():
    """Получает локальный IP адрес"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return "127.0.0.1"


def register_client():
    """Регистрирует клиента в системе"""
    data = {
        'computer_name': socket.gethostname(),
        'ip_address': get_local_ip(),
        'user': os.getlogin(),
        'os': os.name,
        'version': '1.0.0'
    }

    try:
        response = requests.post(f'{API_URL}/clients', json=data, timeout=5)
        return response.status_code == 200 or response.status_code == 201
    except Exception as e:
        print(f'Ошибка регистрации клиента: {e}')
        return False


class USBMonitorGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"USB Device Monitor - {COMPANY_NAME}")
        self.setGeometry(100, 100, 600, 400)
        self.setWindowIcon(QIcon("icon.png"))

        self.init_ui()

        self.initial_devices = self.get_current_usb_devices()
        self.verified_devices = set((dev[0], dev[1]) for dev in self.initial_devices)
        self.suspicious_devices = set()

        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon("icon.png"))

        tray_menu = QMenu()
        show_action = tray_menu.addAction("Показать")
        show_action.triggered.connect(self.show_normal)
        exit_action = tray_menu.addAction("Выход")
        exit_action.triggered.connect(self.close)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

        self.known_devices = load_known_devices()
        self.first_run = len(self.known_devices) == 0

        if self.first_run:
            current_devices = get_current_devices()
            save_known_devices(current_devices)
            self.known_devices = current_devices
            self.log("Первоначальная инициализация: сохранены подключенные устройства")

        # Регистрация клиента при запуске
        if register_client():
            self.log("Клиент успешно зарегистрирован")
        else:
            self.log("Ошибка регистрации клиента")

        self.timer = QTimer()
        self.timer.timeout.connect(self.check_usb_devices)
        self.timer.start(1000)

    def init_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setFont(QFont("Courier", 10))
        self.layout.addWidget(self.log_area)

        buttons_layout = QHBoxLayout()

        self.clear_button = QPushButton("Очистить лог")
        self.clear_button.clicked.connect(self.clear_log)
        buttons_layout.addWidget(self.clear_button)

        self.exit_button = QPushButton("Выход")
        self.exit_button.clicked.connect(self.close)
        buttons_layout.addWidget(self.exit_button)

        self.layout.addLayout(buttons_layout)

    def log(self, message):
        self.log_area.append(message)
        print(message)

    def clear_log(self):
        self.log_area.clear()

    def show_normal(self):
        self.showNormal()
        self.activateWindow()

    def get_current_usb_devices(self):
        try:
            devices = []
            for dev in usb.core.find(find_all=True):
                if dev is not None:
                    manufacturer = get_usb_string(dev, dev.iManufacturer)
                    product = get_usb_string(dev, dev.iProduct)
                    serial = get_usb_string(dev, dev.iSerialNumber)
                    devices.append((dev.idVendor, dev.idProduct, manufacturer, product, serial))
            return devices
        except:
            return []

    def verify_device(self, vid, pid, manufacturer, product, serial):
        """Проверяет устройство через API и блокирует если получен статус 400"""
        try:
            data = {
                'vid': str(hex(vid)).replace("0x", ""),
                'pid': str(hex(pid)).replace('0x', ''),
                'serial_number': str(serial) if serial != 0 else '',
                'device_name': str(product) if product != 0 else 'Unknown',
                'computer_name': socket.gethostname(),
                'ip_address': get_local_ip(),
                'user': os.getlogin()
            }

            response = requests.post(f'{API_URL}/check_device', json=data, timeout=5)

            if response.status_code == 200:
                result = response.json()
                return result.get('allowed', False)
            elif response.status_code == 400:
                # Блокируем устройство
                self.block_device(vid, pid)
                return False
            else:
                return False
        except Exception as e:
            print(f'Ошибка проверки устройства: {e}')
            return False

    def block_device(self, vid, pid):
        """Блокирует USB устройство"""
        try:
            dev = usb.core.find(idVendor=vid, idProduct=pid)
            if dev is not None:
                try:
                    if dev.is_kernel_driver_active(0):
                        dev.detach_kernel_driver(0)
                    if dev.is_kernel_driver_active(1):
                        dev.detach_kernel_driver(1)
                    usb.util.dispose_resources(dev)
                    self.log(f"Устройство VID={hex(vid)}, PID={hex(pid)} было заблокировано")
                except usb.core.USBError as e:
                    self.log(f"Ошибка блокировки устройства: {str(e)}")
        except Exception as e:
            self.log(f"Ошибка поиска устройства для блокировки: {str(e)}")

    def check_usb_devices(self):
        current_devices = self.get_current_usb_devices()
        current_ids = set((dev[0], dev[1]) for dev in current_devices)

        new_devices = [dev for dev in current_devices
                       if (dev[0], dev[1]) not in self.verified_devices
                       and (dev[0], dev[1]) not in self.suspicious_devices]

        for vid, pid, manufacturer, product, serial in new_devices:
            log_msg = f"Обнаружено новое устройство: VID={hex(vid)}, PID={hex(pid)}"
            if manufacturer != 0:
                log_msg += f", Производитель: {manufacturer}"
            if product != 0:
                log_msg += f", Устройство: {product}"
            if serial != 0:
                log_msg += f", Серийный: {serial}"
            self.log(log_msg)

            if self.verify_device(vid, pid, manufacturer, product, serial):
                self.verified_devices.add((vid, pid))
                self.log(f"Устройство разрешено: {product if product != 0 else 'Unknown'}")
            else:
                self.suspicious_devices.add((vid, pid))
                self.log(f"ВНИМАНИЕ: Неавторизованное устройство!")

                # Логируем событие на сервере
                log_data = {
                    'device_name': str(product) if product != 0 else 'Unknown',
                    'vid': hex(vid),
                    'pid': hex(pid),
                    'serial_number': str(serial) if serial != 0 else '',
                    'status': 'blocked',
                    'computer_name': socket.gethostname(),
                    'ip_address': get_local_ip(),
                    'user': os.getlogin()
                }
                try:
                    requests.post(f'{API_URL}/logs', json=log_data, timeout=5)
                except Exception as e:
                    print(f'Ошибка отправки лога: {e}')
    def closeEvent(self, event):
        if not ALLOW_EXIT:
            self.hide()
            event.ignore()
        else:
            self.tray_icon.hide()
            event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    try:
        list(usb.core.find(find_all=True))
        window = USBMonitorGUI()
        window.show()
        sys.exit(app.exec_())
    except usb.core.NoBackendError:
        error_msg = QLabel(
            "Ошибка: Не найдена библиотека для работы с USB.\nУстановите libusb (Linux: sudo apt install libusb-1.0-0-dev)")
        error_msg.show()
        app.exec_()
    except Exception as e:
        error_msg = QLabel(f"Ошибка запуска: {str(e)}")
        error_msg.show()
        app.exec_()