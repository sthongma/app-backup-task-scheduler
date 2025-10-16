"""
Application Configuration Management System
- Save and load settings from JSON file
- Manage input/output paths
"""

import json
import os
from pathlib import Path
from datetime import datetime


class ConfigManager:
    """Manage application settings"""

    def __init__(self, config_file="config/settings.json"):
        """
        Create ConfigManager instance

        Args:
            config_file: path to config file
        """
        self.config_file = Path(config_file)
        self.config_file.parent.mkdir(parents=True, exist_ok=True)

        # Load config or create new
        self.config = self.load_config()

    def get_default_config(self):
        """
        Create default settings

        Returns:
            dict: default settings
        """
        return {
            "backup": {
                "input_paths": [],  # Changed from input_path to input_paths (array)
                "output_path": "",
                "last_backup": None
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
        Load settings from file

        Returns:
            dict: settings
        """
        if not self.config_file.exists():
            # Create new config file
            default_config = self.get_default_config()
            self.save_config(default_config)
            return default_config

        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)

            # Backward compatibility: convert old input_path to input_paths
            if 'backup' in config:
                if 'input_path' in config['backup'] and 'input_paths' not in config['backup']:
                    old_path = config['backup']['input_path']
                    config['backup']['input_paths'] = [old_path] if old_path else []
                    del config['backup']['input_path']
                elif 'input_paths' not in config['backup']:
                    config['backup']['input_paths'] = []

            # Update last_updated
            if 'app_info' not in config:
                config['app_info'] = {}
            config['app_info']['last_updated'] = datetime.now().isoformat()

            return config

        except json.JSONDecodeError as e:
            print(f"Error loading config: {e}")
            return self.get_default_config()

    def save_config(self, config=None):
        """
        Save settings to file

        Args:
            config: settings to save (uses self.config if not specified)

        Returns:
            bool: True if successful
        """
        if config is None:
            config = self.config

        try:
            # Update last_updated
            if 'app_info' not in config:
                config['app_info'] = {}
            config['app_info']['last_updated'] = datetime.now().isoformat()

            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)

            return True

        except Exception as e:
            print(f"Error saving config: {e}")
            return False

    def get(self, key_path, default=None):
        """
        Get value from config using dot notation

        Args:
            key_path: key path (e.g., "backup.input_path")
            default: default value if not found

        Returns:
            requested value
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
        Set value in config using dot notation

        Args:
            key_path: key path (e.g., "backup.input_path")
            value: value to set
        """
        keys = key_path.split('.')
        target = self.config

        # Loop to second-to-last key
        for key in keys[:-1]:
            if key not in target:
                target[key] = {}
            target = target[key]

        # Set value
        target[keys[-1]] = value

    def get_backup_settings(self):
        """Get backup settings"""
        return self.config.get('backup', {})

    def set_backup_settings(self, input_paths, output_path):
        """
        Set backup paths

        Args:
            input_paths: list of source folder paths
            output_path: destination folder path
        """
        self.set('backup.input_paths', input_paths if isinstance(input_paths, list) else [input_paths])
        self.set('backup.output_path', output_path)

    def add_input_path(self, path):
        """
        Add a source folder path

        Args:
            path: source folder path to add
        """
        input_paths = self.get('backup.input_paths', [])
        if path and path not in input_paths:
            input_paths.append(path)
            self.set('backup.input_paths', input_paths)

    def remove_input_path(self, path):
        """
        Remove a source folder path

        Args:
            path: source folder path to remove
        """
        input_paths = self.get('backup.input_paths', [])
        if path in input_paths:
            input_paths.remove(path)
            self.set('backup.input_paths', input_paths)

    def clear_input_paths(self):
        """Clear all source folder paths"""
        self.set('backup.input_paths', [])

    def update_last_backup(self):
        """Update last backup time"""
        self.set('backup.last_backup', datetime.now().isoformat())

    def get_log_settings(self):
        """Get log settings"""
        return self.config.get('logs', {})

    def set_log_retention_days(self, days):
        """Set log retention days"""
        self.set('logs.retention_days', days)

    def get_ui_settings(self):
        """Get UI settings"""
        return self.config.get('ui', {})

    def set_ui_theme(self, theme):
        """
        Set theme

        Args:
            theme: "dark" or "light"
        """
        self.set('ui.theme', theme)

    def validate_paths(self):
        """
        Validate configured paths

        Returns:
            tuple: (input_valid, output_valid, error_message)
        """
        input_paths = self.get('backup.input_paths', [])
        output_path = self.get('backup.output_path')

        # Check input paths
        if not input_paths or len(input_paths) == 0:
            return False, False, "Please add at least one source folder"

        # Validate each input path
        for input_path in input_paths:
            input_path_obj = Path(input_path)
            if not input_path_obj.exists():
                return False, False, f"Source folder not found: {input_path}"

            if not input_path_obj.is_dir():
                return False, False, f"Source is not a folder: {input_path}"

        # Check output path
        if not output_path:
            return True, False, "Please select destination folder"

        # output path can be created
        return True, True, None

    def export_config(self, export_path):
        """
        Export settings to another file

        Args:
            export_path: path to export file

        Returns:
            bool: True if successful
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
        Import settings from file

        Args:
            import_path: path to import file

        Returns:
            bool: True if successful
        """
        try:
            import_path = Path(import_path)

            if not import_path.exists():
                return False

            with open(import_path, 'r', encoding='utf-8') as f:
                imported_config = json.load(f)

            # Merge config with default
            default_config = self.get_default_config()
            self.config = {**default_config, **imported_config}

            # Save
            self.save_config()

            return True

        except Exception as e:
            print(f"Error importing config: {e}")
            return False
