import sys
import os
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from nexa.ui.app import NexaApp
from nexa.infra.database import init_db

def main():
    # Init DB
    init_db("nexa_data.db")
    
    # Enable High DPI scaling
    if hasattr(Qt.ApplicationAttribute, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling)
    if hasattr(Qt.ApplicationAttribute, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps)

    app = QApplication(sys.argv)
    
    # Initialize the main application window
    window = NexaApp()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
