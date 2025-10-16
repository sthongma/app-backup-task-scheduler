"""
Automatic Log File Management System
- Delete old log files that exceed retention period
- Limit log file size
- Compress log files (optional)
"""

import os
import shutil
from datetime import datetime, timedelta
from pathlib import Path
import zipfile


class LogManager:
    """Manage log files automatically"""

    def __init__(self, log_dir="logs", retention_days=30, max_file_size_mb=10):
        """
        Create LogManager instance

        Args:
            log_dir: folder where log files are stored
            retention_days: number of days to keep log files (default: 30 days)
            max_file_size_mb: maximum log file size (MB) (default: 10 MB)
        """
        self.log_dir = Path(log_dir)
        self.retention_days = retention_days
        self.max_file_size_bytes = max_file_size_mb * 1024 * 1024

        # Create folder if it doesn't exist
        self.log_dir.mkdir(parents=True, exist_ok=True)

    def cleanup_old_logs(self):
        """
        Delete old log files that exceed retention period

        Returns:
            tuple: (number of deleted files, number of deleted bytes)
        """
        if not self.log_dir.exists():
            return 0, 0

        cutoff_date = datetime.now() - timedelta(days=self.retention_days)
        deleted_count = 0
        deleted_bytes = 0

        # Loop through all files in log folder
        for log_file in self.log_dir.glob("backup_*.log"):
            try:
                # Check last modified date
                file_mtime = datetime.fromtimestamp(log_file.stat().st_mtime)

                if file_mtime < cutoff_date:
                    file_size = log_file.stat().st_size
                    log_file.unlink()  # Delete file
                    deleted_count += 1
                    deleted_bytes += file_size

            except Exception as e:
                print(f"Error deleting {log_file}: {e}")

        return deleted_count, deleted_bytes

    def cleanup_zip_files(self):
        """Delete old zip files"""
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
        Check log file size

        Args:
            file_path: path of file to check

        Returns:
            bool: True if file size exceeds limit
        """
        file_path = Path(file_path)

        if not file_path.exists():
            return False

        file_size = file_path.stat().st_size
        return file_size > self.max_file_size_bytes

    def compress_old_logs(self, days_threshold=7):
        """
        Compress log files older than threshold

        Args:
            days_threshold: number of days for compression threshold (default: 7 days)

        Returns:
            int: number of compressed files
        """
        if not self.log_dir.exists():
            return 0

        cutoff_date = datetime.now() - timedelta(days=days_threshold)
        compressed_count = 0

        for log_file in self.log_dir.glob("backup_*.log"):
            try:
                file_mtime = datetime.fromtimestamp(log_file.stat().st_mtime)

                # Compress files older than threshold
                if file_mtime < cutoff_date:
                    zip_path = log_file.with_suffix('.log.zip')

                    # Create zip file
                    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                        zipf.write(log_file, log_file.name)

                    # Delete original file
                    log_file.unlink()
                    compressed_count += 1

            except Exception as e:
                print(f"Error compressing {log_file}: {e}")

        return compressed_count

    def get_log_files_info(self):
        """
        Get information of all log files

        Returns:
            list: list of dict containing log file information
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
        Run log files maintenance

        Args:
            compress_logs: True if old logs should be compressed

        Returns:
            dict: summary of maintenance results
        """
        result = {
            'deleted_logs': 0,
            'deleted_bytes': 0,
            'deleted_zips': 0,
            'compressed_logs': 0
        }

        # Delete old log files
        deleted_count, deleted_bytes = self.cleanup_old_logs()
        result['deleted_logs'] = deleted_count
        result['deleted_bytes'] = deleted_bytes

        # Delete old zip files
        result['deleted_zips'] = self.cleanup_zip_files()

        # Compress old logs (if enabled)
        if compress_logs:
            result['compressed_logs'] = self.compress_old_logs()

        return result

    def get_total_log_size(self):
        """
        Calculate total size of all log files

        Returns:
            tuple: (total size in bytes, total size in MB)
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
    Convert byte size to human-readable format

    Args:
        bytes_size: size in bytes

    Returns:
        str: size in human-readable format (KB, MB, GB)
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.2f} PB"
