"""
ระบบจัดการการตั้งค่าแอพพลิเคชัน
- บันทึกและโหลดการตั้งค่าจากไฟล์ JSON
- จัดการ input/output paths และ schedule settings
"""

import json
import os
from pathlib import Path
from datetime import datetime


class ConfigManager:
    """จัดการการตั้งค่าแอพพลิเคชัน"""

    def __init__(self, config_file="config/settings.json"):
        """
        สร้าง ConfigManager instance

        Args:
            config_file: path ของไฟล์ config
        """
        self.config_file = Path(config_file)
        self.config_file.parent.mkdir(parents=True, exist_ok=True)

        # โหลด config หรือสร้างใหม่
        self.config = self.load_config()

    def get_default_config(self):
        """
        สร้างการตั้งค่าเริ่มต้น

        Returns:
            dict: การตั้งค่าเริ่มต้น
        """
        return {
            "backup": {
                "input_path": "",
                "output_path": "",
                "last_backup": None
            },
            "schedule": {
                "enabled": False,
                "mode": "off",  # off, hourly, daily, custom
                "custom_interval_minutes": 60
            },
            "logs": {
                "retention_days": 30,
                "max_file_size_mb": 10,
                "compress_old_logs": False
            },
            "ui": {
                "theme": "dark",  # dark, light
                "last_window_size": "800x600"
            },
            "app_info": {
                "version": "1.0.0",
                "created_at": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat()
            }
        }

    def load_config(self):
        """
        โหลดการตั้งค่าจากไฟล์

        Returns:
            dict: การตั้งค่า
        """
        if not self.config_file.exists():
            # สร้างไฟล์ config ใหม่
            default_config = self.get_default_config()
            self.save_config(default_config)
            return default_config

        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)

            # อัพเดท last_updated
            config['app_info']['last_updated'] = datetime.now().isoformat()

            return config

        except json.JSONDecodeError as e:
            print(f"Error loading config: {e}")
            return self.get_default_config()

    def save_config(self, config=None):
        """
        บันทึกการตั้งค่าลงไฟล์

        Args:
            config: การตั้งค่าที่ต้องการบันทึก (ถ้าไม่ระบุจะใช้ self.config)

        Returns:
            bool: True ถ้าบันทึกสำเร็จ
        """
        if config is None:
            config = self.config

        try:
            # อัพเดท last_updated
            config['app_info']['last_updated'] = datetime.now().isoformat()

            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)

            return True

        except Exception as e:
            print(f"Error saving config: {e}")
            return False

    def get(self, key_path, default=None):
        """
        ดึงค่าจาก config โดยใช้ dot notation

        Args:
            key_path: path ของ key (เช่น "backup.input_path")
            default: ค่า default ถ้าไม่พบ

        Returns:
            ค่าที่ต้องการ
        """
        keys = key_path.split('.')
        value = self.config

        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default

        return value

    def set(self, key_path, value):
        """
        ตั้งค่าใน config โดยใช้ dot notation

        Args:
            key_path: path ของ key (เช่น "backup.input_path")
            value: ค่าที่ต้องการตั้ง
        """
        keys = key_path.split('.')
        target = self.config

        # วนลูปไปยัง key สุดท้าย
        for key in keys[:-1]:
            if key not in target:
                target[key] = {}
            target = target[key]

        # ตั้งค่า
        target[keys[-1]] = value

    def get_backup_settings(self):
        """ดึงการตั้งค่า backup"""
        return self.config.get('backup', {})

    def set_backup_settings(self, input_path, output_path):
        """
        ตั้งค่า backup paths

        Args:
            input_path: path ของโฟลเดอร์ต้นทาง
            output_path: path ของโฟลเดอร์ปลายทาง
        """
        self.set('backup.input_path', input_path)
        self.set('backup.output_path', output_path)

    def update_last_backup(self):
        """อัพเดทเวลา backup ล่าสุด"""
        self.set('backup.last_backup', datetime.now().isoformat())

    def get_schedule_settings(self):
        """ดึงการตั้งค่า schedule"""
        return self.config.get('schedule', {})

    def set_schedule_settings(self, enabled, mode, custom_interval_minutes=60):
        """
        ตั้งค่า schedule

        Args:
            enabled: เปิด/ปิดการ schedule
            mode: โหมด (off, hourly, daily, custom)
            custom_interval_minutes: ระยะเวลาสำหรับโหมด custom (นาที)
        """
        self.set('schedule.enabled', enabled)
        self.set('schedule.mode', mode)
        self.set('schedule.custom_interval_minutes', custom_interval_minutes)

    def get_log_settings(self):
        """ดึงการตั้งค่า logs"""
        return self.config.get('logs', {})

    def set_log_retention_days(self, days):
        """ตั้งค่าจำนวนวันเก็บ log"""
        self.set('logs.retention_days', days)

    def get_ui_settings(self):
        """ดึงการตั้งค่า UI"""
        return self.config.get('ui', {})

    def set_ui_theme(self, theme):
        """
        ตั้งค่า theme

        Args:
            theme: "dark" หรือ "light"
        """
        self.set('ui.theme', theme)

    def validate_paths(self):
        """
        ตรวจสอบว่า paths ที่ตั้งค่าไว้ถูกต้อง

        Returns:
            tuple: (input_valid, output_valid, error_message)
        """
        input_path = self.get('backup.input_path')
        output_path = self.get('backup.output_path')

        # ตรวจสอบ input path
        if not input_path:
            return False, False, "กรุณาเลือกโฟลเดอร์ต้นทาง"

        input_path_obj = Path(input_path)
        if not input_path_obj.exists():
            return False, False, f"ไม่พบโฟลเดอร์ต้นทาง: {input_path}"

        if not input_path_obj.is_dir():
            return False, False, f"ต้นทางไม่ใช่โฟลเดอร์: {input_path}"

        # ตรวจสอบ output path
        if not output_path:
            return True, False, "กรุณาเลือกโฟลเดอร์ปลายทาง"

        # output path สามารถสร้างใหม่ได้
        return True, True, None

    def export_config(self, export_path):
        """
        ส่งออกการตั้งค่าไปยังไฟล์อื่น

        Args:
            export_path: path ของไฟล์ที่จะส่งออก

        Returns:
            bool: True ถ้าสำเร็จ
        """
        try:
            export_path = Path(export_path)
            export_path.parent.mkdir(parents=True, exist_ok=True)

            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)

            return True

        except Exception as e:
            print(f"Error exporting config: {e}")
            return False

    def import_config(self, import_path):
        """
        นำเข้าการตั้งค่าจากไฟล์

        Args:
            import_path: path ของไฟล์ที่จะนำเข้า

        Returns:
            bool: True ถ้าสำเร็จ
        """
        try:
            import_path = Path(import_path)

            if not import_path.exists():
                return False

            with open(import_path, 'r', encoding='utf-8') as f:
                imported_config = json.load(f)

            # รวม config เข้ากับ default
            default_config = self.get_default_config()
            self.config = {**default_config, **imported_config}

            # บันทึก
            self.save_config()

            return True

        except Exception as e:
            print(f"Error importing config: {e}")
            return False
