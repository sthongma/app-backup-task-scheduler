"""
Entry point for CLI Application
Usage: python run_cli.py [options]
"""

import sys
from pathlib import Path

# Add path for importing modules
sys.path.insert(0, str(Path(__file__).parent))

from src.cli.cli_app import main

if __name__ == "__main__":
    main()
