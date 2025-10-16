"""
ระบบจัดการไฟล์ Log อัตโนมัติ
- ลบไฟล์ log เก่าที่เกินกำหนด
- จำกัดขนาดไฟล์ log
- Compress log files (optional)
"""

import os
import shutil
from datetime import datetime, timedelta
from pathlib import Path
import zipfile


class LogManager:
    """จัดการไฟล์ log อัตโนมัติ"""

    def __init__(self, log_dir="logs", retention_days=30, max_file_size_mb=10):
        """
        สร้าง LogManager instance

        Args:
            log_dir: โฟลเดอร์ที่เก็บไฟล์ log
            retention_days: จำนวนวันที่เก็บไฟล์ log (default: 30 วัน)
            max_file_size_mb: ขนาดไฟล์ log สูงสุด (MB) (default: 10 MB)
        """
        self.log_dir = Path(log_dir)
        self.retention_days = retention_days
        self.max_file_size_bytes = max_file_size_mb * 1024 * 1024

        # สร้างโฟลเดอร์ถ้ายังไม่มี
        self.log_dir.mkdir(parents=True, exist_ok=True)

    def cleanup_old_logs(self):
        """
        ลบไฟล์ log เก่าที่เกินกำหนด

        Returns:
            tuple: (จำนวนไฟล์ที่ลบ, จำนวน bytes ที่ลบ)
        """
        if not self.log_dir.exists():
            return 0, 0

        cutoff_date = datetime.now() - timedelta(days=self.retention_days)
        deleted_count = 0
        deleted_bytes = 0

        # วนลูปไฟล์ทั้งหมดในโฟลเดอร์ log
        for log_file in self.log_dir.glob("backup_*.log"):
            try:
                # ตรวจสอบวันที่แก้ไขล่าสุด
                file_mtime = datetime.fromtimestamp(log_file.stat().st_mtime)

                if file_mtime < cutoff_date:
                    file_size = log_file.stat().st_size
                    log_file.unlink()  # ลบไฟล์
                    deleted_count += 1
                    deleted_bytes += file_size

            except Exception as e:
                print(f"Error deleting {log_file}: {e}")

        return deleted_count, deleted_bytes

    def cleanup_zip_files(self):
        """ลบไฟล์ zip เก่า"""
        if not self.log_dir.exists():
            return 0

        cutoff_date = datetime.now() - timedelta(days=self.retention_days)
        deleted_count = 0

        for zip_file in self.log_dir.glob("backup_*.zip"):
            try:
                file_mtime = datetime.fromtimestamp(zip_file.stat().st_mtime)

                if file_mtime < cutoff_date:
                    zip_file.unlink()
                    deleted_count += 1

            except Exception as e:
                print(f"Error deleting {zip_file}: {e}")

        return deleted_count

    def check_file_size(self, file_path):
        """
        ตรวจสอบขนาดไฟล์ log

        Args:
            file_path: path ของไฟล์ที่ต้องการตรวจสอบ

        Returns:
            bool: True ถ้าไฟล์มีขนาดเกินกำหนด
        """
        file_path = Path(file_path)

        if not file_path.exists():
            return False

        file_size = file_path.stat().st_size
        return file_size > self.max_file_size_bytes

    def compress_old_logs(self, days_threshold=7):
        """
        Compress ไฟล์ log ที่เก่ากว่าที่กำหนด

        Args:
            days_threshold: จำนวนวันที่จะ compress (default: 7 วัน)

        Returns:
            int: จำนวนไฟล์ที่ compress
        """
        if not self.log_dir.exists():
            return 0

        cutoff_date = datetime.now() - timedelta(days=days_threshold)
        compressed_count = 0

        for log_file in self.log_dir.glob("backup_*.log"):
            try:
                file_mtime = datetime.fromtimestamp(log_file.stat().st_mtime)

                # Compress ไฟล์ที่เก่ากว่าที่กำหนด
                if file_mtime < cutoff_date:
                    zip_path = log_file.with_suffix('.log.zip')

                    # สร้างไฟล์ zip
                    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                        zipf.write(log_file, log_file.name)

                    # ลบไฟล์ต้นฉบับ
                    log_file.unlink()
                    compressed_count += 1

            except Exception as e:
                print(f"Error compressing {log_file}: {e}")

        return compressed_count

    def get_log_files_info(self):
        """
        ดึงข้อมูลไฟล์ log ทั้งหมด

        Returns:
            list: รายการ dict ที่มีข้อมูลไฟล์ log
        """
        if not self.log_dir.exists():
            return []

        log_files = []

        for log_file in sorted(self.log_dir.glob("backup_*.log*"), reverse=True):
            try:
                stat = log_file.stat()
                log_files.append({
                    'name': log_file.name,
                    'path': str(log_file),
                    'size': stat.st_size,
                    'size_mb': round(stat.st_size / (1024 * 1024), 2),
                    'modified': datetime.fromtimestamp(stat.st_mtime),
                    'is_compressed': log_file.suffix == '.zip'
                })
            except Exception as e:
                print(f"Error reading {log_file}: {e}")

        return log_files

    def run_maintenance(self, compress_logs=False):
        """
        รันการบำรุงรักษา log files

        Args:
            compress_logs: True ถ้าต้องการ compress logs เก่า

        Returns:
            dict: สรุปผลการทำงาน
        """
        result = {
            'deleted_logs': 0,
            'deleted_bytes': 0,
            'deleted_zips': 0,
            'compressed_logs': 0
        }

        # ลบไฟล์ log เก่า
        deleted_count, deleted_bytes = self.cleanup_old_logs()
        result['deleted_logs'] = deleted_count
        result['deleted_bytes'] = deleted_bytes

        # ลบไฟล์ zip เก่า
        result['deleted_zips'] = self.cleanup_zip_files()

        # Compress logs เก่า (ถ้าเปิดใช้งาน)
        if compress_logs:
            result['compressed_logs'] = self.compress_old_logs()

        return result

    def get_total_log_size(self):
        """
        คำนวณขนาดรวมของไฟล์ log ทั้งหมด

        Returns:
            tuple: (ขนาดรวม bytes, ขนาดรวม MB)
        """
        if not self.log_dir.exists():
            return 0, 0

        total_bytes = 0

        for log_file in self.log_dir.glob("backup_*.*"):
            try:
                total_bytes += log_file.stat().st_size
            except Exception:
                pass

        total_mb = round(total_bytes / (1024 * 1024), 2)
        return total_bytes, total_mb


def format_bytes(bytes_size):
    """
    แปลงขนาด bytes เป็นรูปแบบที่อ่านง่าย

    Args:
        bytes_size: ขนาดเป็น bytes

    Returns:
        str: ขนาดในรูปแบบที่อ่านง่าย (KB, MB, GB)
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.2f} PB"
