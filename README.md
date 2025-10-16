# File Backup Application

Simple and reliable file backup application with GUI and CLI interfaces. Designed to work seamlessly with Windows Task Scheduler for automatic backups.

## Features

- ✅ **Simple GUI** - Easy folder selection and one-click backup
- ✅ **CLI Support** - Run backups from command line or scripts
- ✅ **Windows Task Scheduler Ready** - Includes BAT files for easy automation
- ✅ **Progress Tracking** - Real-time backup progress with file counting
- ✅ **Timestamped Backups** - Each backup saved with date/time stamp
- ✅ **Detailed Logging** - All operations logged with automatic cleanup
- ✅ **Error Handling** - Comprehensive error handling and reporting

## Quick Start

### 1. Configure Backup (First Time)

Double-click **`open_gui.bat`** to open the GUI:
1. Click "Browse" next to Source Folder - select folder to backup
2. Click "Browse" next to Destination Folder - select where to save backups
3. Click "Backup Now" to test (optional)
4. Settings are saved automatically

### 2. Run Manual Backup

**Option A: Using GUI**
- Double-click **`open_gui.bat`**
- Click "Backup Now" button

**Option B: Using Command Line**
- Double-click **`backup_now.bat`** (shows progress)
- Or double-click **`backup_now_silent.bat`** (runs in background)

### 3. Set Up Automatic Backup (Recommended)

See **`WINDOWS_TASK_SCHEDULER_SETUP.txt`** for detailed instructions.

**Quick Setup:**
1. Open Task Scheduler (search in Start menu)
2. Click "Create Basic Task..."
3. Name: "File Backup"
4. Choose schedule (e.g., Daily at 2:00 AM)
5. Action: Start a program
6. Browse to: **`backup_now_silent.bat`**
7. Finish!

## Available BAT Files

| File | Description | When to Use |
|------|-------------|-------------|
| **`open_gui.bat`** | Open GUI application | Configure folders, manual backup with UI |
| **`backup_now.bat`** | Run backup (visible) | Manual testing, see progress |
| **`backup_now_silent.bat`** | Run backup (silent) | **Windows Task Scheduler** |
| **`check_status.bat`** | Show system status | Check last backup time, verify settings |
| **`cleanup_logs.bat`** | Clean old log files | Free up disk space |

## Command Line Usage

```bash
# Run backup using saved configuration
python run_cli.py --backup

# Display system status
python run_cli.py --status

# Clean up old log files
python run_cli.py --cleanup-logs

# Show help
python run_cli.py --help
```

## How Backups Work

1. **Timestamped Folders**: Each backup creates a new folder with format:
   ```
   FolderName_YYYYMMDD_HHMMSS
   ```
   Example: `MyData_20251016_140530`

2. **File Structure Preserved**: All subfolders and files are copied exactly as-is

3. **Progress Tracking**: Shows real-time progress during backup

4. **Logging**: All operations logged to `logs/backup_YYYY-MM-DD.log`

## Requirements

- Python 3.7 or higher
- Windows OS (for BAT files and Task Scheduler integration)

### Python Dependencies

```
customtkinter>=5.2.0
Pillow>=10.0.0
```

Install dependencies:
```bash
pip install -r requirements.txt
```

## Project Structure

```
app-backup-task-scheduler/
├── backup_now.bat                    # Run backup (visible console)
├── backup_now_silent.bat             # Run backup (silent, for Task Scheduler)
├── open_gui.bat                      # Open GUI application
├── check_status.bat                  # Show system status
├── cleanup_logs.bat                  # Clean old logs
├── WINDOWS_TASK_SCHEDULER_SETUP.txt  # Detailed setup guide
├── run_gui.py                        # GUI entry point
├── run_cli.py                        # CLI entry point
├── requirements.txt                  # Python dependencies
├── config/
│   └── settings.json                 # Configuration file
├── logs/                             # Log files (auto-created)
├── src/
│   ├── gui/
│   │   └── main_window.py           # GUI application
│   ├── cli/
│   │   └── cli_app.py               # CLI application
│   ├── core/
│   │   ├── backup_engine.py         # Backup logic
│   │   └── config_manager.py        # Configuration management
│   └── utils/
│       ├── logger.py                # Logging system
│       └── log_manager.py           # Log file management
```

## Configuration

Configuration is stored in `config/settings.json`:

```json
{
    "backup": {
        "input_path": "C:/source/folder",
        "output_path": "C:/destination/folder",
        "last_backup": "2025-10-16T14:30:00.000000"
    },
    "logs": {
        "retention_days": 30,
        "max_file_size_mb": 10,
        "compress_old_logs": false
    },
    "ui": {
        "theme": "dark"
    }
}
```

## Logs

- **Location**: `logs/backup_YYYY-MM-DD.log`
- **Retention**: 30 days (configurable)
- **Content**: All backup operations, errors, and system events
- **Cleanup**: Run `cleanup_logs.bat` or it happens automatically

## Troubleshooting

### Backup doesn't run from Task Scheduler
- Make sure Python is installed and in system PATH
- Try running `backup_now.bat` manually first
- Check Task Scheduler task settings (run whether user logged on or not)
- Verify the path to BAT file in Task Scheduler is correct

### "Source/destination not configured" error
- Run `open_gui.bat` and configure folders
- Or run `check_status.bat` to see current settings

### Backup fails
- Check if source folder exists and is accessible
- Check if you have write permission to destination folder
- Review log files in `logs/` folder for detailed error messages

### GUI doesn't open
- Make sure Python is installed: `python --version`
- Install dependencies: `pip install -r requirements.txt`
- Try running: `python run_gui.py`

## Tips

1. **Schedule Daily Backups**: Set Task Scheduler to run at 2:00 AM daily
2. **Check Status Regularly**: Run `check_status.bat` to verify last backup time
3. **Monitor Logs**: Check log files occasionally for any errors
4. **Clean Old Backups**: Manually delete old backup folders from destination when not needed
5. **Test First**: Always test backup manually before setting up Task Scheduler

## License

This project is provided as-is for personal use.

## Support

For issues or questions, check:
- `WINDOWS_TASK_SCHEDULER_SETUP.txt` for detailed setup instructions
- Log files in `logs/` folder for error details
- Run `check_status.bat` to verify configuration

---

**Version:** 1.0.0
**Last Updated:** 2025-10-16
