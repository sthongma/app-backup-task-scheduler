"""
Entry point สำหรับ GUI Application
เรียกใช้งาน: python run_gui.py
"""

import sys
from pathlib import Path

# เพิ่ม path สำหรับ import modules
sys.path.insert(0, str(Path(__file__).parent))

from src.gui.main_window import main

if __name__ == "__main__":
    main()
