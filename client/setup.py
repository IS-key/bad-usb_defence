from setuptools import setup

APP = ['usb_monitor.py']
DATA_FILES = ['icon.png', 'config.py']
OPTIONS = {
    'argv_emulation': True,
    'plist': {
        'LSUIElement': True,  # Makes the app run as a background application
        'CFBundleName': 'USB Monitor',
        'CFBundleDisplayName': 'USB Monitor',
        'CFBundleIdentifier': 'com.company.usbmonitor',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'NSHumanReadableCopyright': 'Copyright © 2024 Your Company',
    },
    'packages': ['PyQt5', 'usb', 'requests'],
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
