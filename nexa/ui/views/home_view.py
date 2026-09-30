from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from qfluentwidgets import (CardWidget, SubtitleLabel, BodyLabel, TitleLabel,
                            PrimaryPushButton, PushButton, SearchLineEdit,
                            FluentIcon as FIF)
import datetime
import psutil
import os
import webbrowser
import subprocess
from nexa.infra.database import get_session, Workspace

class HomeView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("HomeView")
        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.vBoxLayout.setContentsMargins(40, 40, 40, 40)
        
        # Greeting
        self.greetingLabel = TitleLabel(self.get_greeting())
        self.vBoxLayout.addWidget(self.greetingLabel)
        
        self.subtitleLabel = BodyLabel("What are you doing today?")
        self.subtitleLabel.setStyleSheet("color: gray; font-size: 16px;")
        self.vBoxLayout.addWidget(self.subtitleLabel)
        
        self.vBoxLayout.addSpacing(25)
        
        # Search
        self.searchBox = SearchLineEdit()
        self.searchBox.setPlaceholderText("Search anything... (Alt + Space)")
        self.searchBox.setFixedWidth(500)
        self.vBoxLayout.addWidget(self.searchBox, alignment=Qt.AlignmentFlag.AlignLeft)
        
        self.vBoxLayout.addSpacing(40)
        
        # Continue Workspace
        self.continueLabel = SubtitleLabel("Continue where you left off")
        self.vBoxLayout.addWidget(self.continueLabel)
        
        self.continueCard = CardWidget()
        self.continueLayout = QHBoxLayout(self.continueCard)
        self.continueTitle = BodyLabel("No workspace found")
        self.continueBtn = PrimaryPushButton("Launch")
        self.continueBtn.clicked.connect(self.launch_latest_workspace)
        
        self.continueLayout.addWidget(self.continueTitle)
        self.continueLayout.addStretch(1)
        self.continueLayout.addWidget(self.continueBtn)
        self.continueCard.setFixedWidth(500)
        self.vBoxLayout.addWidget(self.continueCard)
        
        self.latest_workspace_id = None
        self.load_latest_workspace()
        
        self.vBoxLayout.addSpacing(30)
        
        # Quick Actions
        self.actionsLabel = SubtitleLabel("Quick Actions")
        self.vBoxLayout.addWidget(self.actionsLabel)
        
        self.actionsLayout = QHBoxLayout()
        self.btnLaunch = PushButton(FIF.SEARCH, "Launcher")
        self.btnWorkspaces = PushButton(FIF.FOLDER, "Workspaces")
        self.btnSettings = PushButton(FIF.SETTING, "Settings")
        
        self.btnLaunch.clicked.connect(self.switch_to_launcher)
        self.btnWorkspaces.clicked.connect(self.switch_to_workspaces)
        self.btnSettings.clicked.connect(self.switch_to_settings)
        
        self.actionsLayout.addWidget(self.btnLaunch)
        self.actionsLayout.addWidget(self.btnWorkspaces)
        self.actionsLayout.addWidget(self.btnSettings)
        self.actionsLayout.addStretch(1)
        
        self.vBoxLayout.addLayout(self.actionsLayout)
        
        self.vBoxLayout.addSpacing(30)
        
        # System status
        self.sysLabel = SubtitleLabel("System")
        self.vBoxLayout.addWidget(self.sysLabel)
        
        self.sysCard = CardWidget()
        self.sysCard.setFixedWidth(500)
        self.sysLayout = QHBoxLayout(self.sysCard)
        self.sysText = BodyLabel("Loading system info...")
        self.sysLayout.addWidget(self.sysText)
        self.vBoxLayout.addWidget(self.sysCard)
        
        self.vBoxLayout.addStretch(1)
        
        # Timer for system stats
        self.sysTimer = QTimer(self)
        self.sysTimer.timeout.connect(self.update_system_stats)
        self.sysTimer.start(2000)
        self.update_system_stats()

    def get_greeting(self):
        hour = datetime.datetime.now().hour
        if 5 <= hour < 12:
            return "Good Morning"
        elif 12 <= hour < 17:
            return "Good Afternoon"
        elif 17 <= hour < 21:
            return "Good Evening"
        else:
            return "Good Night"

    def load_latest_workspace(self):
        session = get_session()
        ws = session.query(Workspace).order_by(Workspace.id.desc()).first()
        if ws:
            self.continueTitle.setText(ws.name)
            self.latest_workspace_id = ws.id
            self.continueBtn.setEnabled(True)
        else:
            self.continueTitle.setText("No workspaces found. Go to Workspaces to create one.")
            self.continueBtn.setEnabled(False)
        session.close()
        
    def launch_latest_workspace(self):
        if not self.latest_workspace_id: return
        session = get_session()
        ws = session.query(Workspace).filter_by(id=self.latest_workspace_id).first()
        if ws:
            for item in ws.items:
                try:
                    if item.item_type == 'url':
                        webbrowser.open(item.path)
                    elif item.item_type == 'command':
                        subprocess.Popen(item.path, shell=True)
                    else:
                        os.startfile(item.path)
                except Exception as e:
                    print(f"Failed to launch {item.path}: {e}")
        session.close()

    def update_system_stats(self):
        try:
            cpu = psutil.cpu_percent(interval=None)
            mem = psutil.virtual_memory().percent
            
            total_disk = 0
            used_disk = 0
            for part in psutil.disk_partitions(all=False):
                if os.name == 'nt' and ('cdrom' in part.opts or part.fstype == ''):
                    continue
                try:
                    usage = psutil.disk_usage(part.mountpoint)
                    total_disk += usage.total
                    used_disk += usage.used
                except Exception:
                    pass
            
            disk = round((used_disk / total_disk) * 100, 1) if total_disk > 0 else 0
            self.sysText.setText(f"CPU: {cpu}%  |  Memory: {mem}%  |  Storage: {disk}%")
        except Exception:
            self.sysText.setText("System info not available")

    def switch_to_workspaces(self):
        if hasattr(self.window(), 'switchTo') and hasattr(self.window(), 'workspacesInterface'):
            self.window().switchTo(self.window().workspacesInterface)

    def switch_to_launcher(self):
        if hasattr(self.window(), 'switchTo') and hasattr(self.window(), 'launcherInterface'):
            self.window().switchTo(self.window().launcherInterface)
            
    def switch_to_settings(self):
        if hasattr(self.window(), 'switchTo') and hasattr(self.window(), 'settingsInterface'):
            self.window().switchTo(self.window().settingsInterface)
