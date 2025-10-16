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
        input_paths = self.config_manager.get('backup.input_paths', [])
        output_path = self.config_manager.get('backup.output_path')

        if not input_paths or len(input_paths) == 0:
            self.logger.error("No source folders configured")
            self.logger.error("Please use GUI to add source folders first")
            return False

        if not output_path:
            self.logger.error("Destination folder not configured")
            self.logger.error("Please use GUI to configure destination folder first")
            return False

        self.logger.info("Starting backup (CLI mode)")
        self.logger.info(f"Source folders: {len(input_paths)} folder(s)")
        for idx, path in enumerate(input_paths, 1):
            self.logger.info(f"  [{idx}] {path}")
        self.logger.info(f"Destination folder: {output_path}")

        # Run multi-folder backup
        result = self.backup_engine.backup_multiple(input_paths, output_path)

        if result['success']:
            self.logger.success("All backups completed successfully")
            self.config_manager.update_last_backup()
            self.config_manager.save_config()
            return True
        else:
            self.logger.error(f"Some backups failed: {result['failed']}/{result['total_folders']} folders")
            return False

    def show_status(self):
        """Display system status"""
        print("=" * 60)
        print("Backup System Status")
        print("=" * 60)

        # Source Folders
        input_paths = self.config_manager.get('backup.input_paths', [])
        print(f"\nSource folders: {len(input_paths)} folder(s)")
        if len(input_paths) == 0:
            print("  (No folders configured)")
        else:
            for idx, path in enumerate(input_paths, 1):
                print(f"  [{idx}] {path}")

        # Destination Folder
        output_path = self.config_manager.get('backup.output_path', '-')
        print(f"\nDestination folder: {output_path}")

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
    """Main function - Auto-run all functions sequentially"""
    # Create CLI instance
    cli = BackupCLI()

    print("\n" + "=" * 60)
    print("AUTO-RUN MODE: Running all functions sequentially...")
    print("=" * 60 + "\n")

    # Step 1: Display system status
    print("\n[STEP 1/3] Displaying system status...")
    print("-" * 60)
    cli.show_status()

    # Step 2: Run backup
    print("\n[STEP 2/3] Running backup...")
    print("-" * 60)
    success = cli.backup_from_config()

    # Step 3: Clean up old logs
    print("\n[STEP 3/3] Cleaning up old logs...")
    print("-" * 60)
    cli.cleanup_logs()

    # Final summary
    print("\n" + "=" * 60)
    print("AUTO-RUN COMPLETED")
    print("=" * 60)
    print(f"Backup status: {'SUCCESS' if success else 'FAILED'}")
    print("=" * 60 + "\n")

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
