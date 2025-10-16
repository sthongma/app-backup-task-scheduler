@echo off
REM Backup Now (Silent) - Run backup without any console window
REM Ideal for Windows Task Scheduler - runs completely in background

cd /d "%~dp0"
pythonw run_cli.py --backup > nul 2>&1
