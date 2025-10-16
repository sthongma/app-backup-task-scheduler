"""
Logging System for Backup Application
- Create daily log files (backup_YYYY-MM-DD.log)
- Support both console and file output
"""

import logging
import os
from datetime import datetime
from pathlib import Path


class BackupLogger:
    """Manage logging for backup system"""

    def __init__(self, log_dir="logs"):
        """
        Create logger instance

        Args:
            log_dir: folder for storing log files
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Create log file name based on current date
        today = datetime.now().strftime("%Y-%m-%d")
        self.log_file = self.log_dir / f"backup_{today}.log"

        # Create logger
        self.logger = logging.getLogger("BackupApp")
        self.logger.setLevel(logging.DEBUG)

        # Remove old handlers if exists (prevent duplication)
        if self.logger.handlers:
            self.logger.handlers.clear()

        # Create formatter
        formatter = logging.Formatter(
            '[%(asctime)s] %(levelname)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # File handler - write log to file
        file_handler = logging.FileHandler(
            self.log_file,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

        # Console handler - display log on console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

    def info(self, message):
        """Log info message"""
        self.logger.info(message)

    def warning(self, message):
        """Log warning message"""
        self.logger.warning(message)

    def error(self, message):
        """Log error message"""
        self.logger.error(message)

    def debug(self, message):
        """Log debug message"""
        self.logger.debug(message)

    def success(self, message):
        """Log success message (info level)"""
        self.logger.info(f"✓ {message}")

    def get_log_file_path(self):
        """Return path of current log file"""
        return str(self.log_file)


# Create singleton instance
_logger_instance = None

def get_logger(log_dir="logs"):
    """
    Get logger instance (singleton pattern)

    Args:
        log_dir: folder for storing log files

    Returns:
        BackupLogger instance
    """
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = BackupLogger(log_dir)
    return _logger_instance
