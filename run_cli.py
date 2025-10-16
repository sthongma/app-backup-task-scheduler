"""
Entry point สำหรับ CLI Application
เรียกใช้งาน: python run_cli.py [options]
"""

import sys
from pathlib import Path

# เพิ่ม path สำหรับ import modules
sys.path.insert(0, str(Path(__file__).parent))

from src.cli.cli_app import main

if __name__ == "__main__":
    main()
