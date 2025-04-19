import sys
import os
import socket
import json
from pathlib import Path
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QLabel, QTextEdit, QPushButton, QHBoxLayout,
                             QSystemTrayIcon, QMenu, QMessageBox, QFrame,
                             QSplitter, QTreeWidget, QTreeWidgetItem, QHeaderView)
from PyQt5.QtCore import QTimer, Qt, QSize
from PyQt5.QtGui import QFont, QIcon, QColor, QPalette, QLinearGradient, QBrush
import usb.core
import usb.util
from datetime import datetime
import requests
import time
import config

API_URL = config.API_URL
COMPANY_NAME = config.COMPANY_NAME
ALLOW_EXIT = False
CONFIG_DIR = Path.home() / ".usb_monitor"
CONFIG_FILE = CONFIG_DIR / "known_devices.json"


def get_usb_string(dev, index):
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
    try:
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading known devices: {e}")
    return []


def save_known_devices(devices):
    try:
        CONFIG_DIR.mkdir(exist_ok=True)
        with open(CONFIG_FILE, 'w') as f:
            json.dump(devices, f)
    except Exception as e:
        print(f"Error saving known devices: {e}")


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
        print(f"Error getting current devices: {e}")
        return []


def check_device(vid, pid, manufacturer, product, serial_number):
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
        print(f'Error checking device: {e}')
    return False


def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return "127.0.0.1"


def register_client():
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
        print(f'Error registering client: {e}')
        return False


class StyledFrame(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)
        self.setStyleSheet("""
            StyledFrame {
                background-color: #f8f9fa;
                border-radius: 8px;
                border: 1px solid #e9ecef;
            }
        """)


class USBMonitorGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"USB Device Monitor - {COMPANY_NAME}")
        self.setGeometry(100, 100, 800, 600)
        self.setWindowIcon(QIcon("icon.jpg"))
        self.setStyleSheet("""
            QMainWindow {
                background-color: #ffffff;
            }
            QTextEdit {
                background-color: #f8f9fa;
                border-radius: 4px;
                border: 1px solid #e9ecef;
                padding: 8px;
                font-family: 'Courier New';
                font-size: 10pt;
            }
            QPushButton {
                background-color: #007bff;
                color: white;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover {
                background-color: #0069d9;
            }
            QPushButton:pressed {
                background-color: #0062cc;
            }
            QLabel {
                font-size: 12pt;
                font-weight: bold;
                color: #343a40;
            }
            QTreeWidget {
                background-color: #f8f9fa;
                border-radius: 4px;
                border: 1px solid #e9ecef;
                padding: 4px;
            }
            QTreeWidget::item {
                height: 30px;
            }
            QTreeWidget::item:selected {
                background-color: #007bff;
                color: white;
            }
        """)

        self.init_ui()

        self.initial_devices = self.get_current_usb_devices()
        self.verified_devices = set((dev[0], dev[1]) for dev in self.initial_devices)
        self.suspicious_devices = set()

        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon("icon.jpg"))

        tray_menu = QMenu()
        show_action = tray_menu.addAction("Show")
        show_action.triggered.connect(self.show_normal)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

        self.known_devices = load_known_devices()
        self.first_run = len(self.known_devices) == 0

        if self.first_run:
            current_devices = get_current_devices()
            save_known_devices(current_devices)
            self.known_devices = current_devices
            self.log("Initial setup: saved connected devices")

        if register_client():
            self.log("Client successfully registered")
        else:
            self.log("Error registering client")

        self.timer = QTimer()
        self.timer.timeout.connect(self.check_usb_devices)
        self.timer.start(1000)

        self.update_device_tree()

    def init_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        main_layout = QVBoxLayout()
        self.central_widget.setLayout(main_layout)

        header_frame = StyledFrame()
        header_layout = QHBoxLayout(header_frame)

        title_label = QLabel(f"USB Device Monitor - {COMPANY_NAME}")
        title_label.setStyleSheet("font-size: 18pt; color: #343a40;")
        header_layout.addWidget(title_label)

        status_label = QLabel("Status: Monitoring")
        status_label.setStyleSheet("color: #28a745; font-weight: bold;")
        header_layout.addWidget(status_label, alignment=Qt.AlignRight)

        main_layout.addWidget(header_frame)

        splitter = QSplitter(Qt.Horizontal)

        left_panel = StyledFrame()
        left_layout = QVBoxLayout(left_panel)

        devices_label = QLabel("Connected Devices")
        left_layout.addWidget(devices_label)

        self.device_tree = QTreeWidget()
        self.device_tree.setHeaderLabels(["Device", "Status"])
        self.device_tree.header().setSectionResizeMode(0, QHeaderView.Stretch)
        self.device_tree.header().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        left_layout.addWidget(self.device_tree)

        right_panel = StyledFrame()
        right_layout = QVBoxLayout(right_panel)

        log_label = QLabel("Activity Log")
        right_layout.addWidget(log_label)

        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setFont(QFont("Courier New", 10))
        right_layout.addWidget(self.log_area)

        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([300, 500])

        main_layout.addWidget(splitter)

        buttons_frame = StyledFrame()
        buttons_layout = QHBoxLayout(buttons_frame)

        self.clear_button = QPushButton("Clear Log")
        self.clear_button.clicked.connect(self.clear_log)
        buttons_layout.addWidget(self.clear_button)

        self.refresh_button = QPushButton("Refresh Devices")
        self.refresh_button.clicked.connect(self.update_device_tree)
        buttons_layout.addWidget(self.refresh_button)

        self.exit_button = QPushButton("Exit")
        self.exit_button.clicked.connect(self.close)
        buttons_layout.addWidget(self.exit_button)

        main_layout.addWidget(buttons_frame)

    def update_device_tree(self):
        self.device_tree.clear()
        current_devices = self.get_current_usb_devices()

        for vid, pid, manufacturer, product, serial in current_devices:
            device_name = str(product) if product != 0 else f"Unknown Device ({hex(vid)}:{hex(pid)})"
            manufacturer_name = str(manufacturer) if manufacturer != 0 else "Unknown Manufacturer"

            item = QTreeWidgetItem([f"{device_name} - {manufacturer_name}"])

            if (vid, pid) in self.verified_devices:
                item.setText(1, "Allowed")
                item.setForeground(1, QBrush(QColor("#28a745")))
            elif (vid, pid) in self.suspicious_devices:
                item.setText(1, "Blocked")
                item.setForeground(1, QBrush(QColor("#dc3545")))
            else:
                item.setText(1, "Unknown")
                item.setForeground(1, QBrush(QColor("#ffc107")))

            details = QTreeWidgetItem([f"VID: {hex(vid)}, PID: {hex(pid)}"])
            if serial != 0:
                serial_item = QTreeWidgetItem([f"Serial: {serial}"])
                details.addChild(serial_item)

            item.addChild(details)
            self.device_tree.addTopLevelItem(item)

        self.device_tree.expandAll()

    def log(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted_message = f"[{timestamp}] {message}"
        self.log_area.append(formatted_message)
        print(formatted_message)

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
                self.block_device(vid, pid)
                return False
            else:
                return False
        except Exception as e:
            print(f'Error checking device: {e}')
            return False

    def block_known(self, vid, pid):
        dev = usb.core.find(idVendor=vid, idProduct=pid)
        if dev is not None:
            try:
                if dev.is_kernel_driver_active(0):
                    dev.detach_kernel_driver(0)
                if dev.is_kernel_driver_active(1):
                    dev.detach_kernel_driver(1)
                usb.util.dispose_resources(dev)
            except:
                pass

    def block_device(self, vid, pid):
        try:
            dev = usb.core.find(idVendor=vid, idProduct=pid)
            if dev is not None:
                try:
                    if dev.is_kernel_driver_active(0):
                        dev.detach_kernel_driver(0)
                    if dev.is_kernel_driver_active(1):
                        dev.detach_kernel_driver(1)
                    usb.util.dispose_resources(dev)
                    self.log(f"Device VID={hex(vid)}, PID={hex(pid)} has been blocked")
                except usb.core.USBError:
                    self.log(f"Device disconnected for verification")
        except Exception as e:
            self.log(f"Error finding device to block: {str(e)}")

    def check_usb_devices(self):
        current_devices = self.get_current_usb_devices()
        current_ids = set((dev[0], dev[1]) for dev in current_devices)
        new_devices = []
        for dev in current_devices:
            if (dev[0], dev[1]) in self.suspicious_devices:
                self.block_known(dev[0], dev[1])
            if (dev[0], dev[1]) not in self.verified_devices and (dev[0], dev[1]) not in self.suspicious_devices:
                new_devices.append(dev)

        for vid, pid, manufacturer, product, serial in new_devices:
            log_msg = f"New device detected: VID={hex(vid)}, PID={hex(pid)}"
            if manufacturer != 0:
                log_msg += f", Manufacturer: {manufacturer}"
            if product != 0:
                log_msg += f", Device: {product}"
            if serial != 0:
                log_msg += f", Serial: {serial.replace(' ', '')}"
            self.log(log_msg)
            if serial == 0:
                serial = '0'
            if self.verify_device(vid, pid, manufacturer, product, serial):
                self.verified_devices.add((vid, pid))
                self.log(f"Device allowed: {product if product != 0 else 'Unknown'}")
            else:
                self.suspicious_devices.add((vid, pid))
                self.log(f"WARNING: Unauthorized device!")

                log_data = {
                    'device_name': str(product) if product != 0 else 'Unknown',
                    'vid': hex(vid),
                    'pid': hex(pid),
                    'serial_number': str(serial) if serial != 0 else '0',
                    'status': 'blocked',
                    'computer_name': socket.gethostname(),
                    'ip_address': get_local_ip(),
                    'user': os.getlogin()
                }

        self.update_device_tree()

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
            "Error: USB library not found.\nPlease install libusb (Linux: sudo apt install libusb-1.0-0-dev)")
        error_msg.show()
        app.exec_()
    except Exception as e:
        error_msg = QLabel(f"Startup error: {str(e)}")
        error_msg.show()
        app.exec_()