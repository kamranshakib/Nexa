from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QListWidgetItem
from qfluentwidgets import (SearchLineEdit, SubtitleLabel, CardWidget)

class LauncherView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("LauncherView")
        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.vBoxLayout.setContentsMargins(40, 40, 40, 40)
        
        self.titleLabel = SubtitleLabel("Global Launcher")
        self.vBoxLayout.addWidget(self.titleLabel)
        
        self.vBoxLayout.addSpacing(20)
        
        self.searchBox = SearchLineEdit()
        self.searchBox.setPlaceholderText("Search apps, files, workspaces...")
        self.searchBox.setFixedWidth(600)
        self.vBoxLayout.addWidget(self.searchBox, alignment=Qt.AlignmentFlag.AlignLeft)
        
        self.vBoxLayout.addSpacing(20)
        
        # Results list
        self.resultsList = QListWidget()
        self.resultsList.setFixedWidth(600)
        self.resultsList.setStyleSheet("""
            QListWidget {
                border: none;
                background-color: transparent;
                outline: none;
            }
            QListWidget::item {
                padding: 10px;
                border-radius: 5px;
            }
            QListWidget::item:selected {
                background-color: #e0e0e0;
                color: black;
            }
        """)
        self.vBoxLayout.addWidget(self.resultsList, alignment=Qt.AlignmentFlag.AlignLeft)
        
        # Populate dummy data
        self.add_dummy_results()
        
    def add_dummy_results(self):
        items = [
            "Edulinn Development (Workspace)",
            "Visual Studio Code (App)",
            "server.js (File)",
            "Focus Mode 90m (Command)"
        ]
        for text in items:
            item = QListWidgetItem(text)
            self.resultsList.addItem(item)
