"""
CLI Application for Backup
- Run backup using saved configuration
"""

import argparse
import sys
from pathlib import Path

# Add path for importing modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.utils.logger import get_logger
from src.utils.log_manager import LogManager
from src.core.config_manager import ConfigManager
from src.core.backup_engine import BackupEngine


class BackupCLI:
    """CLI Application for Backup"""

    def __init__(self):
        """Create CLI instance"""
        self.logger = get_logger()
        self.log_manager = LogManager()
        self.config_manager = ConfigManager()
        self.backup_engine = BackupEngine(self.logger)

    def backup_from_config(self):
        """Run backup using config settings"""
        input_path = self.config_manager.get('backup.input_path')
        output_path = self.config_manager.get('backup.output_path')

        if not input_path or not output_path:
            self.logger.error("Source and destination folders not configured")
            self.logger.error("Please use GUI to configure folders first")
            return False

        self.logger.info("Starting backup (CLI mode)")
        self.logger.info(f"Source folder: {input_path}")
        self.logger.info(f"Destination folder: {output_path}")

        # Run backup
        result = self.backup_engine.backup(input_path, output_path)

        if result['success']:
            self.logger.success("Backup completed successfully")
            self.config_manager.update_last_backup()
            self.config_manager.save_config()
            return True
        else:
            self.logger.error(f"Error occurred: {result.get('error', 'Unknown error')}")
            return False

    def show_status(self):
        """Display system status"""
        print("=" * 60)
        print("Backup System Status")
        print("=" * 60)

        # Folders
        input_path = self.config_manager.get('backup.input_path', '-')
        output_path = self.config_manager.get('backup.output_path', '-')
        print(f"Source folder: {input_path}")
        print(f"Destination folder: {output_path}")

        # Last backup
        last_backup = self.config_manager.get('backup.last_backup')
        if last_backup:
            print(f"\nLast backup: {last_backup}")
        else:
            print("\nNo backup performed yet")

        # Log files
        log_info = self.log_manager.get_log_files_info()
        total_bytes, total_mb = self.log_manager.get_total_log_size()

        print(f"\nLog files: {len(log_info)} files")
        print(f"Total size: {total_mb} MB")

        print("=" * 60)

    def cleanup_logs(self):
        """Clean up old log files"""
        self.logger.info("Starting log cleanup...")

        retention_days = self.config_manager.get('logs.retention_days', 30)
        self.log_manager.retention_days = retention_days

        result = self.log_manager.run_maintenance(compress_logs=False)

        self.logger.info(f"Deleted log files: {result['deleted_logs']} files")
        self.logger.info(f"Deleted zip files: {result['deleted_zips']} files")
        self.logger.info("Cleanup completed")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='CLI Application for Automatic Backup',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Usage examples:

  # Run backup using saved configuration
  python run_cli.py --backup

  # Display system status
  python run_cli.py --status

  # Clean up old log files
  python run_cli.py --cleanup-logs

Note: Configure source and destination folders using the GUI first.
Use Windows Task Scheduler to schedule automatic backups.
        """
    )

    parser.add_argument(
        '--backup',
        action='store_true',
        help='Run backup using saved configuration'
    )

    parser.add_argument(
        '--status',
        action='store_true',
        help='Display system status'
    )

    parser.add_argument(
        '--cleanup-logs',
        action='store_true',
        help='Clean up old log files'
    )

    args = parser.parse_args()

    # Create CLI instance
    cli = BackupCLI()

    # Display status
    if args.status:
        cli.show_status()
        return

    # Clean up logs
    if args.cleanup_logs:
        cli.cleanup_logs()
        return

    # Run backup
    if args.backup:
        success = cli.backup_from_config()
        sys.exit(0 if success else 1)

    # No arguments - show help
    parser.print_help()


if __name__ == "__main__":
    main()
