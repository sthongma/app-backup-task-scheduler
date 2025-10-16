@echo off
REM Backup Now - Run immediate backup using saved configuration
REM This script runs the CLI backup command

cd /d "%~dp0"
python run_cli.py --backup

REM Pause to see results (remove this line if running from Task Scheduler)
REM pause
