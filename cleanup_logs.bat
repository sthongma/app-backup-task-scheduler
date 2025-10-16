@echo off
REM Cleanup Logs - Remove old log files
REM Deletes log files older than retention period (default: 30 days)

cd /d "%~dp0"
python run_cli.py --cleanup-logs

pause
