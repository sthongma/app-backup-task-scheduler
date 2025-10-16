"""
File/Folder Backup System
- Copy entire folders with all subfolders and files
- Display progress and status
- Log operations
"""

import shutil
import os
from pathlib import Path
from datetime import datetime
import time


class BackupEngine:
    """Automated file backup system"""

    def __init__(self, logger=None):
        """
        Create BackupEngine instance

        Args:
            logger: BackupLogger instance for logging operations
        """
        self.logger = logger
        self.total_files = 0
        self.copied_files = 0
        self.failed_files = 0
        self.total_size = 0
        self.copied_size = 0
        self.errors = []
        self.callback = None

    def set_progress_callback(self, callback):
        """
        Set callback function for progress reporting

        Args:
            callback: function that accepts parameters (current, total, message)
        """
        self.callback = callback

    def _count_files(self, source_path):
        """
        Count the number of files and total size in folder

        Args:
            source_path: path of source folder

        Returns:
            tuple: (file count, total size in bytes)
        """
        file_count = 0
        total_size = 0

        try:
            for root, dirs, files in os.walk(source_path):
                for file in files:
                    file_path = Path(root) / file
                    try:
                        if file_path.exists():
                            total_size += file_path.stat().st_size
                            file_count += 1
                    except Exception:
                        pass

        except Exception as e:
            if self.logger:
                self.logger.error(f"Error counting files: {e}")

        return file_count, total_size

    def _format_size(self, bytes_size):
        """
        Convert byte size to human-readable format

        Args:
            bytes_size: size in bytes

        Returns:
            str: size in human-readable format
        """
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_size < 1024.0:
                return f"{bytes_size:.2f} {unit}"
            bytes_size /= 1024.0
        return f"{bytes_size:.2f} PB"

    def _copy_file_with_progress(self, src, dst):
        """
        Copy file with progress update

        Args:
            src: path of source file
            dst: path of destination file

        Returns:
            bool: True if successful
        """
        try:
            # Create destination folder
            dst_path = Path(dst)
            dst_path.parent.mkdir(parents=True, exist_ok=True)

            # Copy file
            shutil.copy2(src, dst)

            # Update progress
            src_path = Path(src)
            file_size = src_path.stat().st_size
            self.copied_size += file_size
            self.copied_files += 1

            # Call callback
            if self.callback:
                progress_percent = (self.copied_files / self.total_files * 100) if self.total_files > 0 else 0
                self.callback(
                    self.copied_files,
                    self.total_files,
                    f"Copying: {src_path.name} ({progress_percent:.1f}%)"
                )

            return True

        except Exception as e:
            self.failed_files += 1
            error_msg = f"Error copying {src}: {e}"
            self.errors.append(error_msg)

            if self.logger:
                self.logger.error(error_msg)

            return False

    def backup(self, source_path, destination_path, overwrite=True):
        """
        Copy entire folder

        Args:
            source_path: path of source folder
            destination_path: path of destination folder
            overwrite: True if destination folder should be overwritten

        Returns:
            dict: backup operation result
        """
        start_time = time.time()

        # Reset counters
        self.total_files = 0
        self.copied_files = 0
        self.failed_files = 0
        self.total_size = 0
        self.copied_size = 0
        self.errors = []

        source = Path(source_path)
        destination = Path(destination_path)

        # Check source folder
        if not source.exists():
            error_msg = f"Source folder not found: {source_path}"
            if self.logger:
                self.logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg
            }

        if not source.is_dir():
            error_msg = f"Source is not a folder: {source_path}"
            if self.logger:
                self.logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg
            }

        # Initial log
        if self.logger:
            self.logger.info("=" * 60)
            self.logger.info(f"Starting backup")
            self.logger.info(f"From: {source_path}")
            self.logger.info(f"To: {destination_path}")

        # Count files
        if self.logger:
            self.logger.info("Counting files...")

        self.total_files, self.total_size = self._count_files(source)

        if self.logger:
            self.logger.info(f"Found {self.total_files:,} files (Total size: {self._format_size(self.total_size)})")

        if self.total_files == 0:
            warning_msg = "No files found in source folder"
            if self.logger:
                self.logger.warning(warning_msg)
            return {
                'success': True,
                'warning': warning_msg,
                'total_files': 0,
                'copied_files': 0
            }

        # Create destination folder name with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_folder_name = f"{source.name}_{timestamp}"
        final_destination = destination / backup_folder_name

        # Create destination folder
        try:
            final_destination.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            error_msg = f"Cannot create destination folder: {e}"
            if self.logger:
                self.logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg
            }

        # Start copying files
        if self.logger:
            self.logger.info(f"Starting file copy...")

        try:
            # Loop through and copy files one by one
            for root, dirs, files in os.walk(source):
                root_path = Path(root)
                relative_path = root_path.relative_to(source)
                dest_dir = final_destination / relative_path

                # Create subfolder
                dest_dir.mkdir(parents=True, exist_ok=True)

                # Copy files
                for file in files:
                    src_file = root_path / file
                    dst_file = dest_dir / file

                    self._copy_file_with_progress(src_file, dst_file)

        except Exception as e:
            error_msg = f"Error during copy: {e}"
            if self.logger:
                self.logger.error(error_msg)

        # Calculate elapsed time
        elapsed_time = time.time() - start_time

        # Summary
        success = self.failed_files == 0

        if self.logger:
            self.logger.info("-" * 60)
            self.logger.info(f"Backup completed")
            self.logger.info(f"Total files: {self.total_files:,}")
            self.logger.info(f"Copied successfully: {self.copied_files:,}")

            if self.failed_files > 0:
                self.logger.warning(f"Failed to copy: {self.failed_files:,}")

            self.logger.info(f"Total size: {self._format_size(self.copied_size)}")
            self.logger.info(f"Time elapsed: {elapsed_time:.2f} seconds")
            self.logger.info(f"Saved to: {final_destination}")

            if success:
                self.logger.success("Backup completed successfully")
            else:
                self.logger.warning("Backup completed but some files failed to copy")

            self.logger.info("=" * 60)

        return {
            'success': success,
            'total_files': self.total_files,
            'copied_files': self.copied_files,
            'failed_files': self.failed_files,
            'total_size': self.total_size,
            'copied_size': self.copied_size,
            'elapsed_time': elapsed_time,
            'destination': str(final_destination),
            'errors': self.errors
        }

    def quick_backup(self, source_path, destination_path):
        """
        Quick backup (uses shutil.copytree)

        Args:
            source_path: path of source folder
            destination_path: path of destination folder

        Returns:
            dict: backup operation result
        """
        start_time = time.time()

        source = Path(source_path)
        destination = Path(destination_path)

        # Check source folder
        if not source.exists() or not source.is_dir():
            error_msg = f"Invalid source folder: {source_path}"
            if self.logger:
                self.logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg
            }

        # Create destination folder name
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_folder_name = f"{source.name}_{timestamp}"
        final_destination = destination / backup_folder_name

        if self.logger:
            self.logger.info(f"Starting backup (quick mode)")
            self.logger.info(f"From: {source_path}")
            self.logger.info(f"To: {final_destination}")

        try:
            # Copy entire folder
            shutil.copytree(source, final_destination)

            elapsed_time = time.time() - start_time

            if self.logger:
                self.logger.success(f"Copy completed in {elapsed_time:.2f} seconds")
                self.logger.info(f"Saved to: {final_destination}")

            return {
                'success': True,
                'elapsed_time': elapsed_time,
                'destination': str(final_destination)
            }

        except Exception as e:
            error_msg = f"Error occurred: {e}"
            if self.logger:
                self.logger.error(error_msg)

            return {
                'success': False,
                'error': error_msg
            }
