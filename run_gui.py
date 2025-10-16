"""
Entry point for GUI Application
Usage: python run_gui.py
"""

import sys
from pathlib import Path

# Add path for importing modules
sys.path.insert(0, str(Path(__file__).parent))

from src.gui.main_window import main

if __name__ == "__main__":
    main()
