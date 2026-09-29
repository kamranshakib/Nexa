import sys
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout

from qfluentwidgets import (FluentWindow, NavigationItemPosition, setTheme, Theme,
                            SubtitleLabel, setFont, FluentIcon as FIF)

class HomeWidget(QWidget):
    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        self.setObjectName(text)
        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label = SubtitleLabel(text, self)
        setFont(self.label, 24)
        self.vBoxLayout.addWidget(self.label)

from nexa.ui.views.home_view import HomeView
from nexa.ui.views.launcher_view import LauncherView
from nexa.ui.views.workspaces_view import WorkspacesView
from nexa.ui.views.settings_view import SettingsView

class NexaApp(FluentWindow):
    def __init__(self):
        super().__init__()
        
        # Initialize Window
        self.initWindow()
        
        # Create sub interfaces (Views)
        self.homeInterface = HomeView(self)
        self.homeInterface.setObjectName('homeInterface')
        
        self.launcherInterface = LauncherView(self)
        self.launcherInterface.setObjectName('launcherInterface')
        
        self.workspacesInterface = WorkspacesView(self)
        self.workspacesInterface.setObjectName('workspacesInterface')

        self.clipboardInterface = HomeWidget('Clipboard', self)
        self.clipboardInterface.setObjectName('clipboardInterface')

        self.filesInterface = HomeWidget('Files & Search', self)
        self.filesInterface.setObjectName('filesInterface')

        self.activityInterface = HomeWidget('Activity Timeline', self)
        self.activityInterface.setObjectName('activityInterface')

        self.focusInterface = HomeWidget('Focus Mode', self)
        self.focusInterface.setObjectName('focusInterface')

        self.systemInterface = HomeWidget('System Dashboard', self)
        self.systemInterface.setObjectName('systemInterface')
        
        self.settingsInterface = SettingsView(self)
        self.settingsInterface.setObjectName('settingsInterface')
        
        self.initNavigation()
        
    def initNavigation(self):
        self.addSubInterface(self.homeInterface, FIF.HOME, 'Home')
        self.addSubInterface(self.launcherInterface, FIF.SEARCH, 'Launcher')
        self.addSubInterface(self.workspacesInterface, FIF.FOLDER, 'Workspaces')
        self.addSubInterface(self.clipboardInterface, FIF.COPY, 'Clipboard')
        self.addSubInterface(self.filesInterface, FIF.DOCUMENT, 'Files')
        self.addSubInterface(self.activityInterface, FIF.HISTORY, 'Activity')
        self.addSubInterface(self.focusInterface, FIF.STOP_WATCH, 'Focus')
        self.addSubInterface(self.systemInterface, FIF.APPLICATION, 'System')
        
        # Add settings to the bottom
        self.addSubInterface(self.settingsInterface, FIF.SETTING, 'Settings', NavigationItemPosition.BOTTOM)
        
    def initWindow(self):
        self.resize(1000, 700)
        self.setWindowIcon(QIcon('nexa/ui/assets/icon.png'))
        self.setWindowTitle('NEXA')
        
        # Center the window
        desktop = QApplication.primaryScreen().availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w//2 - self.width()//2, h//2 - self.height()//2)
        
        setTheme(Theme.LIGHT)
