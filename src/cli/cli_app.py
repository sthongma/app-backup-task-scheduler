"""
CLI Application สำหรับ Backup อัตโนมัติ
- รันในพื้นหลังตาม schedule ที่ตั้งไว้
- รองรับ command line arguments
"""

import argparse
import sys
import time
from pathlib import Path

# เพิ่ม path สำหรับ import modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.utils.logger import get_logger
from src.utils.log_manager import LogManager
from src.core.config_manager import ConfigManager
from src.core.backup_engine import BackupEngine
from src.core.scheduler import BackupScheduler


class BackupCLI:
    """CLI Application สำหรับ Backup"""

    def __init__(self):
        """สร้าง CLI instance"""
        self.logger = get_logger()
        self.log_manager = LogManager()
        self.config_manager = ConfigManager()
        self.backup_engine = BackupEngine(self.logger)
        self.scheduler = BackupScheduler(self.logger)

    def run_backup_once(self, input_path, output_path):
        """
        รัน backup ครั้งเดียวแล้วออก

        Args:
            input_path: path ของโฟลเดอร์ต้นทาง
            output_path: path ของโฟลเดอร์ปลายทาง

        Returns:
            bool: True ถ้าสำเร็จ
        """
        self.logger.info("เริ่มการสำรองข้อมูล (CLI mode - once)")

        # รัน backup
        result = self.backup_engine.backup(input_path, output_path)

        if result['success']:
            self.logger.success("การสำรองข้อมูลเสร็จสมบูรณ์")
            return True
        else:
            self.logger.error(f"เกิดข้อผิดพลาด: {result.get('error', 'Unknown error')}")
            return False

    def run_scheduled_backup(self, mode="hourly", custom_interval_minutes=60):
        """
        รัน backup อัตโนมัติตาม schedule

        Args:
            mode: โหมด (hourly, daily, custom)
            custom_interval_minutes: ช่วงเวลาสำหรับโหมด custom
        """
        # โหลดการตั้งค่า
        input_path = self.config_manager.get('backup.input_path')
        output_path = self.config_manager.get('backup.output_path')

        if not input_path or not output_path:
            self.logger.error("ยังไม่ได้ตั้งค่าโฟลเดอร์ต้นทางและปลายทาง")
            self.logger.error("กรุณาใช้ GUI เพื่อตั้งค่าโฟลเดอร์ หรือระบุผ่าน command line arguments")
            return

        self.logger.info("เริ่มระบบสำรองข้อมูลอัตโนมัติ (CLI mode)")
        self.logger.info(f"โฟลเดอร์ต้นทาง: {input_path}")
        self.logger.info(f"โฟลเดอร์ปลายทาง: {output_path}")

        # สร้างฟังก์ชัน backup
        def backup_function():
            try:
                result = self.backup_engine.backup(input_path, output_path)

                if result['success']:
                    self.config_manager.update_last_backup()
                    self.config_manager.save_config()

            except Exception as e:
                self.logger.error(f"เกิดข้อผิดพลาด: {e}")

        # ตั้งค่า scheduler
        self.scheduler.set_backup_function(backup_function)

        # เริ่ม scheduler
        success = self.scheduler.start(mode=mode, custom_interval_minutes=custom_interval_minutes)

        if not success:
            self.logger.error("ไม่สามารถเริ่ม scheduler ได้")
            return

        # แสดงสถานะ
        status = self.scheduler.get_status()
        self.logger.info(f"โหมด: {self.scheduler.get_mode_description(status['mode'])}")

        if status['next_run_time']:
            self.logger.info(f"จะสำรองครั้งถัดไปเมื่อ: {status['next_run_time']}")

        self.logger.info("กด Ctrl+C เพื่อหยุด")
        self.logger.info("-" * 60)

        # รันจนกว่าจะถูก interrupt
        try:
            while True:
                time.sleep(1)

        except KeyboardInterrupt:
            self.logger.info("\nกำลังหยุดระบบ...")
            self.scheduler.shutdown()
            self.logger.info("หยุดระบบเรียบร้อย")

    def backup_from_config(self):
        """รัน backup ตามการตั้งค่าใน config"""
        input_path = self.config_manager.get('backup.input_path')
        output_path = self.config_manager.get('backup.output_path')

        if not input_path or not output_path:
            self.logger.error("ยังไม่ได้ตั้งค่าโฟลเดอร์ต้นทางและปลายทาง")
            return False

        return self.run_backup_once(input_path, output_path)

    def show_status(self):
        """แสดงสถานะของระบบ"""
        print("=" * 60)
        print("สถานะระบบสำรองข้อมูล")
        print("=" * 60)

        # โฟลเดอร์
        input_path = self.config_manager.get('backup.input_path', '-')
        output_path = self.config_manager.get('backup.output_path', '-')
        print(f"โฟลเดอร์ต้นทาง: {input_path}")
        print(f"โฟลเดอร์ปลายทาง: {output_path}")

        # Schedule
        schedule_settings = self.config_manager.get_schedule_settings()
        enabled = schedule_settings.get('enabled', False)
        mode = schedule_settings.get('mode', 'off')

        print(f"\nการสำรองอัตโนมัติ: {'เปิด' if enabled else 'ปิด'}")

        if enabled:
            print(f"โหมด: {self.scheduler.get_mode_description(mode)}")

            if mode == 'custom':
                interval = schedule_settings.get('custom_interval_minutes', 60)
                print(f"ช่วงเวลา: {interval} นาที")

        # Backup ล่าสุด
        last_backup = self.config_manager.get('backup.last_backup')
        if last_backup:
            print(f"\nสำรองล่าสุด: {last_backup}")
        else:
            print("\nยังไม่เคยสำรองข้อมูล")

        # Log files
        log_info = self.log_manager.get_log_files_info()
        total_bytes, total_mb = self.log_manager.get_total_log_size()

        print(f"\nไฟล์ Log: {len(log_info)} ไฟล์")
        print(f"ขนาดรวม: {total_mb} MB")

        print("=" * 60)

    def cleanup_logs(self):
        """ทำความสะอาด log files"""
        self.logger.info("เริ่มทำความสะอาด log files...")

        retention_days = self.config_manager.get('logs.retention_days', 30)
        self.log_manager.retention_days = retention_days

        result = self.log_manager.run_maintenance(compress_logs=False)

        self.logger.info(f"ลบไฟล์ log: {result['deleted_logs']} ไฟล์")
        self.logger.info(f"ลบไฟล์ zip: {result['deleted_zips']} ไฟล์")
        self.logger.info("ทำความสะอาดเสร็จสิ้น")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='CLI Application สำหรับสำรองข้อมูลอัตโนมัติ',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
ตัวอย่างการใช้งาน:

  # สำรองครั้งเดียว
  python run_cli.py --input "C:/source" --output "D:/backup" --once

  # สำรองอัตโนมัติ (ทุกชั่วโมง)
  python run_cli.py --schedule hourly

  # สำรองอัตโนมัติ (ทุกวัน)
  python run_cli.py --schedule daily

  # สำรองอัตโนมัติ (กำหนดเอง - ทุก 30 นาที)
  python run_cli.py --schedule custom --interval 30

  # สำรองตามการตั้งค่าใน config
  python run_cli.py --backup

  # แสดงสถานะ
  python run_cli.py --status

  # ทำความสะอาด log
  python run_cli.py --cleanup-logs
        """
    )

    parser.add_argument(
        '--input',
        type=str,
        help='โฟลเดอร์ต้นทาง (source folder)'
    )

    parser.add_argument(
        '--output',
        type=str,
        help='โฟลเดอร์ปลายทาง (destination folder)'
    )

    parser.add_argument(
        '--once',
        action='store_true',
        help='สำรองครั้งเดียวแล้วออก'
    )

    parser.add_argument(
        '--schedule',
        type=str,
        choices=['hourly', 'daily', 'custom'],
        help='เริ่มการสำรองอัตโนมัติ (hourly, daily, custom)'
    )

    parser.add_argument(
        '--interval',
        type=int,
        default=60,
        help='ช่วงเวลาสำหรับโหมด custom (นาที, default: 60)'
    )

    parser.add_argument(
        '--backup',
        action='store_true',
        help='สำรองตามการตั้งค่าใน config'
    )

    parser.add_argument(
        '--status',
        action='store_true',
        help='แสดงสถานะของระบบ'
    )

    parser.add_argument(
        '--cleanup-logs',
        action='store_true',
        help='ทำความสะอาด log files เก่า'
    )

    args = parser.parse_args()

    # สร้าง CLI instance
    cli = BackupCLI()

    # แสดงสถานะ
    if args.status:
        cli.show_status()
        return

    # ทำความสะอาด logs
    if args.cleanup_logs:
        cli.cleanup_logs()
        return

    # สำรองตาม config
    if args.backup:
        success = cli.backup_from_config()
        sys.exit(0 if success else 1)

    # สำรองครั้งเดียว
    if args.once:
        if not args.input or not args.output:
            print("Error: ต้องระบุ --input และ --output สำหรับโหมด --once")
            parser.print_help()
            sys.exit(1)

        success = cli.run_backup_once(args.input, args.output)
        sys.exit(0 if success else 1)

    # สำรองอัตโนมัติ
    if args.schedule:
        # อัพเดท config ถ้ามี input/output
        if args.input and args.output:
            cli.config_manager.set_backup_settings(args.input, args.output)
            cli.config_manager.save_config()

        cli.run_scheduled_backup(
            mode=args.schedule,
            custom_interval_minutes=args.interval
        )
        return

    # ไม่มี arguments - แสดง help
    parser.print_help()


if __name__ == "__main__":
    main()
