"""
ระบบ Logging สำหรับแอพพลิเคชัน Backup
- สร้างไฟล์ log แยกรายวัน (backup_YYYY-MM-DD.log)
- รองรับทั้ง console และ file output
"""

import logging
import os
from datetime import datetime
from pathlib import Path


class BackupLogger:
    """จัดการ logging สำหรับระบบ backup"""

    def __init__(self, log_dir="logs"):
        """
        สร้าง logger instance

        Args:
            log_dir: โฟลเดอร์สำหรับเก็บไฟล์ log
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # สร้างชื่อไฟล์ log ตามวันที่ปัจจุบัน
        today = datetime.now().strftime("%Y-%m-%d")
        self.log_file = self.log_dir / f"backup_{today}.log"

        # สร้าง logger
        self.logger = logging.getLogger("BackupApp")
        self.logger.setLevel(logging.DEBUG)

        # ลบ handlers เก่าถ้ามี (ป้องกันการซ้ำซ้อน)
        if self.logger.handlers:
            self.logger.handlers.clear()

        # สร้าง formatter
        formatter = logging.Formatter(
            '[%(asctime)s] %(levelname)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # File handler - เขียน log ลงไฟล์
        file_handler = logging.FileHandler(
            self.log_file,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

        # Console handler - แสดง log บน console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

    def info(self, message):
        """บันทึก info message"""
        self.logger.info(message)

    def warning(self, message):
        """บันทึก warning message"""
        self.logger.warning(message)

    def error(self, message):
        """บันทึก error message"""
        self.logger.error(message)

    def debug(self, message):
        """บันทึก debug message"""
        self.logger.debug(message)

    def success(self, message):
        """บันทึก success message (info level)"""
        self.logger.info(f"✓ {message}")

    def get_log_file_path(self):
        """ส่งคืน path ของไฟล์ log ปัจจุบัน"""
        return str(self.log_file)


# สร้าง singleton instance
_logger_instance = None

def get_logger(log_dir="logs"):
    """
    ดึง logger instance (singleton pattern)

    Args:
        log_dir: โฟลเดอร์สำหรับเก็บไฟล์ log

    Returns:
        BackupLogger instance
    """
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = BackupLogger(log_dir)
    return _logger_instance
