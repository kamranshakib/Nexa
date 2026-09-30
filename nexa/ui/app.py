import sys
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout

from qfluentwidgets import (FluentWindow, NavigationItemPosition, setTheme, Theme,
                            SubtitleLabel, setFont, FluentIcon as FIF, qconfig)

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
from nexa.ui.views.clipboard_view import ClipboardView
from nexa.ui.views.files_view import FilesView
from nexa.ui.views.settings_view import SettingsView
from nexa.ui.views.activity_view import ActivityView
from nexa.ui.views.focus_view import FocusView
from nexa.ui.views.system_view import SystemView

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

        self.clipboardInterface = ClipboardView(self)
        self.clipboardInterface.setObjectName('clipboardInterface')

        self.filesInterface = FilesView(self)
        self.filesInterface.setObjectName('filesInterface')

        self.activityInterface = ActivityView(self)
        self.activityInterface.setObjectName('activityInterface')

        self.focusInterface = FocusView(self)
        self.focusInterface.setObjectName('focusInterface')

        self.systemInterface = SystemView(self)
        self.systemInterface.setObjectName('systemInterface')
        
        self.settingsInterface = SettingsView(self)
        self.settingsInterface.setObjectName('settingsInterface')
        
        self.initNavigation()
        self.init_clipboard_listener()
        
    def init_clipboard_listener(self):
        self.app_clipboard = QApplication.clipboard()
        self.app_clipboard.dataChanged.connect(self.on_clipboard_changed)
        self.last_clipboard_text = ""

    def on_clipboard_changed(self):
        mime_data = self.app_clipboard.mimeData()
        if mime_data.hasText():
            text = mime_data.text().strip()
            if text and text != self.last_clipboard_text:
                self.last_clipboard_text = text
                from nexa.infra.database import get_session, ClipboardItem, log_activity, get_setting
                try:
                    if get_setting('track_clipboard', 'True') != 'True':
                        return
                        
                    session = get_session()
                    latest = session.query(ClipboardItem).order_by(ClipboardItem.id.desc()).first()
                    if not latest or latest.content != text:
                        new_item = ClipboardItem(content_type='text', content=text)
                        session.add(new_item)
                        session.commit()
                        
                        # Log to activity timeline
                        snippet = text[:50] + "..." if len(text) > 50 else text
                        log_activity('clipboard', 'Copied text', snippet, text)
                        
                    session.close()
                    
                    if hasattr(self, 'clipboardInterface') and hasattr(self.clipboardInterface, 'refresh'):
                        self.clipboardInterface.refresh()
                except Exception as e:
                    print("Clipboard save error:", e)

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
        
        # Connect Theme Changes and Set Initial Theme
        qconfig.themeChanged.connect(setTheme)
        setTheme(qconfig.theme)
