"""
ระบบจัดตารางเวลาอัตโนมัติสำหรับ Backup
- รองรับการตั้งเวลาหลายรูปแบบ
- ใช้ APScheduler
"""

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import threading


class BackupScheduler:
    """ระบบจัดการตารางเวลาสำหรับ Backup อัตโนมัติ"""

    def __init__(self, logger=None):
        """
        สร้าง BackupScheduler instance

        Args:
            logger: BackupLogger instance สำหรับบันทึก log
        """
        self.logger = logger
        self.scheduler = BackgroundScheduler()
        self.job_id = "backup_job"
        self.is_running = False
        self.backup_function = None
        self.current_mode = "off"

    def set_backup_function(self, backup_func):
        """
        ตั้งค่าฟังก์ชันที่จะรันเมื่อถึงเวลา

        Args:
            backup_func: function ที่จะเรียกเมื่อถึงเวลา backup
        """
        self.backup_function = backup_func

    def start(self, mode="hourly", custom_interval_minutes=60):
        """
        เริ่มการจัดตารางเวลา

        Args:
            mode: โหมดการตั้งเวลา (off, hourly, daily, custom)
            custom_interval_minutes: ระยะเวลาสำหรับโหมด custom (นาที)

        Returns:
            bool: True ถ้าเริ่มสำเร็จ
        """
        if self.backup_function is None:
            if self.logger:
                self.logger.error("ยังไม่ได้ตั้งค่าฟังก์ชัน backup")
            return False

        # ลบ job เก่า (ถ้ามี)
        self.stop()

        try:
            # เริ่ม scheduler
            if not self.scheduler.running:
                self.scheduler.start()

            # เพิ่ม job ตามโหมด
            if mode == "hourly":
                # ทุกชั่วโมง
                self.scheduler.add_job(
                    self._run_backup,
                    trigger=IntervalTrigger(hours=1),
                    id=self.job_id,
                    name="Hourly Backup",
                    replace_existing=True
                )
                if self.logger:
                    self.logger.info("เริ่มการสำรองข้อมูลอัตโนมัติ: ทุก 1 ชั่วโมง")

            elif mode == "daily":
                # ทุกวันเวลา 00:00
                self.scheduler.add_job(
                    self._run_backup,
                    trigger=CronTrigger(hour=0, minute=0),
                    id=self.job_id,
                    name="Daily Backup",
                    replace_existing=True
                )
                if self.logger:
                    self.logger.info("เริ่มการสำรองข้อมูลอัตโนมัติ: ทุกวันเวลา 00:00 น.")

            elif mode == "custom":
                # ตามช่วงเวลาที่กำหนด
                self.scheduler.add_job(
                    self._run_backup,
                    trigger=IntervalTrigger(minutes=custom_interval_minutes),
                    id=self.job_id,
                    name=f"Custom Backup ({custom_interval_minutes} min)",
                    replace_existing=True
                )
                if self.logger:
                    self.logger.info(f"เริ่มการสำรองข้อมูลอัตโนมัติ: ทุก {custom_interval_minutes} นาที")

            else:
                if self.logger:
                    self.logger.warning(f"โหมดไม่ถูกต้อง: {mode}")
                return False

            self.is_running = True
            self.current_mode = mode
            return True

        except Exception as e:
            if self.logger:
                self.logger.error(f"เกิดข้อผิดพลาดในการเริ่ม scheduler: {e}")
            return False

    def stop(self):
        """หยุดการจัดตารางเวลา"""
        try:
            if self.scheduler.running and self.scheduler.get_job(self.job_id):
                self.scheduler.remove_job(self.job_id)

            self.is_running = False
            self.current_mode = "off"

            if self.logger:
                self.logger.info("หยุดการสำรองข้อมูลอัตโนมัติ")

        except Exception as e:
            if self.logger:
                self.logger.error(f"เกิดข้อผิดพลาดในการหยุด scheduler: {e}")

    def shutdown(self):
        """ปิด scheduler"""
        try:
            if self.scheduler.running:
                self.scheduler.shutdown(wait=False)

            if self.logger:
                self.logger.info("ปิด scheduler")

        except Exception as e:
            if self.logger:
                self.logger.error(f"เกิดข้อผิดพลาดในการปิด scheduler: {e}")

    def _run_backup(self):
        """
        รันฟังก์ชัน backup (ถูกเรียกโดย scheduler)
        """
        if self.backup_function is None:
            return

        try:
            if self.logger:
                self.logger.info("=" * 60)
                self.logger.info(f"เริ่มการสำรองข้อมูลอัตโนมัติ ({self.current_mode})")
                self.logger.info(f"เวลา: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

            # เรียกฟังก์ชัน backup
            self.backup_function()

        except Exception as e:
            if self.logger:
                self.logger.error(f"เกิดข้อผิดพลาดในการสำรองข้อมูลอัตโนมัติ: {e}")

    def get_next_run_time(self):
        """
        ดึงเวลาที่จะรัน backup ครั้งถัดไป

        Returns:
            datetime or None: เวลาที่จะรันครั้งถัดไป
        """
        try:
            if not self.scheduler.running:
                return None

            job = self.scheduler.get_job(self.job_id)
            if job and job.next_run_time:
                return job.next_run_time

        except Exception:
            pass

        return None

    def get_status(self):
        """
        ดึงสถานะของ scheduler

        Returns:
            dict: สถานะของ scheduler
        """
        next_run = self.get_next_run_time()

        return {
            'is_running': self.is_running,
            'mode': self.current_mode,
            'next_run_time': next_run.strftime('%Y-%m-%d %H:%M:%S') if next_run else None,
            'scheduler_running': self.scheduler.running
        }

    def run_now(self):
        """
        รัน backup ทันทีแบบ asynchronous

        Returns:
            bool: True ถ้าเริ่มสำเร็จ
        """
        if self.backup_function is None:
            if self.logger:
                self.logger.error("ยังไม่ได้ตั้งค่าฟังก์ชัน backup")
            return False

        try:
            # รันใน thread แยก
            thread = threading.Thread(target=self._run_backup, daemon=True)
            thread.start()
            return True

        except Exception as e:
            if self.logger:
                self.logger.error(f"เกิดข้อผิดพลาดในการรัน backup ทันที: {e}")
            return False

    def is_job_running(self):
        """
        ตรวจสอบว่ามี job กำลังรันอยู่หรือไม่

        Returns:
            bool: True ถ้ามี job กำลังรัน
        """
        try:
            if not self.scheduler.running:
                return False

            job = self.scheduler.get_job(self.job_id)
            return job is not None

        except Exception:
            return False

    def get_mode_description(self, mode):
        """
        ดึงคำอธิบายของโหมด

        Args:
            mode: โหมด (off, hourly, daily, custom)

        Returns:
            str: คำอธิบาย
        """
        descriptions = {
            'off': 'Auto backup off',
            'hourly': 'Backup every hour',
            'daily': 'Backup daily at 00:00',
            'custom': 'Backup at custom interval'
        }
        return descriptions.get(mode, 'Unknown')
