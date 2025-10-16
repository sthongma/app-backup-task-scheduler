@echo off
REM Check Status - Display backup system status
REM Shows source/destination folders, last backup time, and log info

cd /d "%~dp0"
python run_cli.py --status

pause
