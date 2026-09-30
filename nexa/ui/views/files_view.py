import os
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from qfluentwidgets import (SearchLineEdit, TitleLabel, BodyLabel, ProgressBar,
                            FluentIcon as FIF, IconWidget, PushButton, CardWidget,
                            SmoothScrollArea, StrongBodyLabel, CaptionLabel, TransparentToolButton)
import subprocess

class SearchWorker(QThread):
    result_found = pyqtSignal(str, str) # name, path
    search_finished = pyqtSignal()
    
    def __init__(self, query):
        super().__init__()
        self.query = query.lower()
        self.is_cancelled = False
        
    def run(self):
        user_profile = os.path.expanduser('~')
        drives = [user_profile]
        
        import string
        from ctypes import windll
        bitmask = windll.kernel32.GetLogicalDrives()
        for letter in string.ascii_uppercase:
            if bitmask & 1:
                drive = f"{letter}:\\"
                if drive != "C:\\" and os.path.exists(drive):
                    drives.append(drive)
            bitmask >>= 1
            
        for base_path in drives:
            if self.is_cancelled: break
            
            for root, dirs, files in os.walk(base_path):
                if self.is_cancelled: break
                dirs[:] = [d for d in dirs if not d.startswith('.') and d.lower() not in ['appdata', 'node_modules', 'windows', 'program files', 'program files (x86)', 'venv']]
                
                for file in files:
                    if self.is_cancelled: break
                    if self.query in file.lower():
                        self.result_found.emit(file, os.path.join(root, file))
                        
        self.search_finished.emit()

    def cancel(self):
        self.is_cancelled = True

class SearchResultCard(CardWidget):
    def __init__(self, name, path, parent=None):
        super().__init__(parent)
        self.path = path
        self.setFixedHeight(70)
        
        self.hBoxLayout = QHBoxLayout(self)
        self.hBoxLayout.setContentsMargins(15, 10, 15, 10)
        
        # Icon
        ext = os.path.splitext(path)[1].lower()
        if ext == '.pdf': icon = FIF.DOCUMENT
        elif ext in ['.jpg', '.png', '.jpeg']: icon = FIF.PHOTO
        elif ext in ['.mp4', '.mkv']: icon = FIF.VIDEO
        elif ext in ['.py', '.js', '.html']: icon = FIF.CODE
        else: icon = FIF.FOLDER if os.path.isdir(path) else FIF.DOCUMENT
        
        self.iconWidget = IconWidget(icon, self)
        self.iconWidget.setFixedSize(24, 24)
        self.hBoxLayout.addWidget(self.iconWidget)
        self.hBoxLayout.addSpacing(10)
        
        # Texts
        self.textLayout = QVBoxLayout()
        self.nameLabel = StrongBodyLabel(name, self)
        self.pathLabel = CaptionLabel(path, self)
        
        self.textLayout.addWidget(self.nameLabel)
        self.textLayout.addWidget(self.pathLabel)
        self.hBoxLayout.addLayout(self.textLayout, 1)
        
        # Open Button
        self.btnOpen = PushButton(FIF.CHEVRON_RIGHT_MED, "Open")
        self.btnOpen.clicked.connect(self.open_file)
        self.hBoxLayout.addWidget(self.btnOpen)

    def open_file(self):
        try:
            os.startfile(self.path)
        except Exception as e:
            print(f"Error opening file: {e}")

class FilesView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("FilesView")
        self.mainLayout = QVBoxLayout(self)
        self.mainLayout.setContentsMargins(40, 40, 40, 40)
        
        # Top Logo & Title
        self.headerLayout = QVBoxLayout()
        self.headerLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.titleLabel = TitleLabel("Global Search", self)
        self.titleLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.headerLayout.addWidget(self.titleLabel)
        
        self.subtitleLabel = BodyLabel("Search everything on your computer", self)
        self.subtitleLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.headerLayout.addWidget(self.subtitleLabel)
        
        self.mainLayout.addLayout(self.headerLayout)
        self.mainLayout.addSpacing(20)
        
        # Search Box
        self.searchLayout = QHBoxLayout()
        self.searchBox = SearchLineEdit()
        self.searchBox.setPlaceholderText("Type a file name and press Enter...")
        self.searchBox.setFixedWidth(600)
        self.searchBox.setFixedHeight(45)
        # REMOVED setStyleSheet so it doesn't break fluent design!
        self.searchBox.returnPressed.connect(self.start_search)
        
        self.searchLayout.addStretch(1)
        self.searchLayout.addWidget(self.searchBox)
        self.searchLayout.addStretch(1)
        self.mainLayout.addLayout(self.searchLayout)
        
        # Progress Bar (Hidden by default)
        self.progressLayout = QHBoxLayout()
        self.progressBar = ProgressBar(self)
        self.progressBar.setFixedWidth(600)
        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(0)
        self.progressBar.hide()
        self.progressLayout.addStretch(1)
        self.progressLayout.addWidget(self.progressBar)
        self.progressLayout.addStretch(1)
        self.mainLayout.addSpacing(10)
        self.mainLayout.addLayout(self.progressLayout)
        
        self.mainLayout.addSpacing(20)
        
        # Results List using ScrollArea and Cards
        self.scrollArea = SmoothScrollArea(self)
        self.scrollArea.setWidgetResizable(True)
        
        self.scrollWidget = QWidget()
        self.scrollWidget.setObjectName("searchScrollWidget")
        self.scrollWidget.setStyleSheet("#searchScrollWidget { background: transparent; }")
        
        self.resultsLayout = QVBoxLayout(self.scrollWidget)
        self.resultsLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.resultsLayout.setSpacing(10)
        self.resultsLayout.setContentsMargins(10, 10, 10, 10)
        
        self.scrollArea.setWidget(self.scrollWidget)
        self.mainLayout.addWidget(self.scrollArea)
        
        self.worker = None

    def start_search(self):
        query = self.searchBox.text().strip()
        if not query:
            return
            
        if self.worker and self.worker.isRunning():
            self.worker.cancel()
            self.worker.wait()
            
        # Clear current results
        while self.resultsLayout.count():
            item = self.resultsLayout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
        self.progressBar.show()
        
        self.worker = SearchWorker(query)
        self.worker.result_found.connect(self.add_result)
        self.worker.search_finished.connect(self.on_search_finished)
        self.worker.start()

    def add_result(self, name, path):
        # Prevent adding more than 100 results to avoid UI lag
        if self.resultsLayout.count() > 100:
            return
            
        card = SearchResultCard(name, path)
        self.resultsLayout.addWidget(card)

    def on_search_finished(self):
        self.progressBar.hide()
        if self.resultsLayout.count() == 0:
            label = BodyLabel("No results found.", self)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.resultsLayout.addWidget(label)
