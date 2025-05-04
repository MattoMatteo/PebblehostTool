import sys
import os
from pathlib import Path

def resource_path(relative_path):
    """Used to create a single executable file with pyinstaller except for config.json"""
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS  # PyInstaller executable
    else:
        base_path = Path(__file__).resolve().parent # Normal execution
    return os.path.join(base_path, relative_path)