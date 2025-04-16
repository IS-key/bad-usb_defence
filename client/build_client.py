#!/usr/bin/env python3
import os
import sys
import platform
import shutil
import subprocess
from pathlib import Path
import PyInstaller.__main__


def check_platform():
    """Проверяем, что сборка выполняется на целевой ОС"""
    target = platform.system().lower()
    if target not in ['windows', 'linux', 'darwin']:
        print("Неподдерживаемая ОС для сборки")
        sys.exit(1)
    return target


def create_config(api_url, company_name, allow_exit=False):
    """Создает конфигурационный файл"""
    config = f"""# Auto-generated config
API_URL = "{api_url}"
COMPANY_NAME = "{company_name}"
ALLOW_EXIT = {allow_exit}
REQUIRE_ADMIN = True  # Обязательный запуск от админа
"""
    return config


def patch_source_code(source_path, temp_path):
    """Модифицирует исходный код для включения проверки прав"""
    with open(source_path, 'r', encoding='utf-8') as f:
        code = f.read()

    # Добавляем проверку прав администратора
    admin_check = """
import sys
import os
import ctypes

def check_admin():
    try:
        if sys.platform == 'win32':
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        else:
            return os.getuid() == 0
    except:
        return False

if not check_admin():
    print("Ошибка: Требуются права администратора")
    if sys.platform == 'win32':
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    else:
        print("Запустите с sudo/от root")
    sys.exit(1)
"""

    code = admin_check + "\n" + code
    with open(temp_path, 'w', encoding='utf-8') as f:
        f.write(code)


def build_for_platform(target, api_url, company_name, output_dir):
    """Собирает клиент для конкретной платформы"""
    print(f"\nСборка для {target}...")

    temp_dir = Path("temp_build")
    temp_dir.mkdir(exist_ok=True)

    # 1. Создаем конфиг
    config = create_config(api_url, company_name)
    (temp_dir / "config.py").write_text(config, encoding='utf-8')

    # 2. Модифицируем исходный код
    source_file = "usb_monitor.py"
    temp_source = temp_dir / "usb_monitor_temp.py"
    patch_source_code(source_file, temp_source)

    # 3. Определяем параметры сборки
    base_name = f"USBMonitor_{company_name}_{api_url.split('//')[-1].split('/')[0]}"
    icon_ext = '.ico' if target == 'windows' else '.icns' if target == 'darwin' else '.png'
    icon_file = f"icon{icon_ext}"

    build_args = [
        str(temp_source),
        '--onefile',
        '--noconsole' if target != 'windows' else '--windowed',
        f'--name={base_name}',
        f'--add-data={temp_dir / "config.py"}:.' if target != 'windows' else f'--add-data={temp_dir / "config.py"};.',
    ]

    # 4. Добавляем иконку если есть
    if os.path.exists(icon_file):
        build_args.extend(['--icon', icon_file])
        build_args.append(f'--add-data={icon_file}:.' if target != 'windows' else f'--add-data={icon_file};.')

    # 5. Особые параметры для Windows (UAC)
    if target == 'windows':
        build_args.append('--uac-admin')

    # 6. Запускаем сборку
    PyInstaller.__main__.run(build_args)

    # 7. Организация выходных файлов
    platform_dir = Path(output_dir) / target
    platform_dir.mkdir(parents=True, exist_ok=True)

    if target == 'windows':
        exe_src = Path("dist") / f"{base_name}.exe"
        exe_dest = platform_dir / f"{base_name}.exe"
    elif target == 'darwin':
        exe_src = Path("dist") / f"{base_name}"
        exe_dest = platform_dir / f"{base_name}.app"
    else:  # linux
        exe_src = Path("dist") / f"{base_name}"
        exe_dest = platform_dir / f"{base_name}"

        # Создаем скрипт запуска для Linux
        launch_script = f"""#!/bin/sh
if [ "$(id -u)" != "0" ]; then
    echo "Требуются права root. Запустите с sudo."
    exit 1
fi
exec "{exe_dest.name}" "$@"
"""
        (platform_dir / f"launch_{base_name}.sh").write_text(launch_script)
        os.chmod(platform_dir / f"launch_{base_name}.sh", 0o755)

    if exe_src.exists():
        shutil.move(str(exe_src), str(exe_dest))
        print(f"Успешно: {exe_dest}")
    else:
        print("Ошибка сборки")

    # 8. Очистка
    shutil.rmtree("build")
    shutil.rmtree(temp_dir)
    spec_file = Path(f"{base_name}.spec")
    if spec_file.exists():
        spec_file.unlink()


def main():
    if len(sys.argv) < 3:
        print("Использование:")
        print("  python build_client.py <API_URL> <Company_Name> [output_dir]")
        print("Пример:")
        print("  python build_client.py https://api.yourcompany.com \"Your Company\" dist")
        sys.exit(1)

    api_url = sys.argv[1]
    company_name = sys.argv[2]
    output_dir = sys.argv[3] if len(sys.argv) > 3 else "dist"

    current_platform = check_platform()
    build_for_platform(current_platform, api_url, company_name, output_dir)

    print("\nДля сборки под другие ОС запустите на соответствующих системах:")
    print(f"  Windows: py -3 build_client.py {api_url} \"{company_name}\" {output_dir}")
    print(f"  macOS: python3 build_client.py {api_url} \"{company_name}\" {output_dir}")
    print(f"  Linux: python3 build_client.py {api_url} \"{company_name}\" {output_dir}")


if __name__ == "__main__":
    main()