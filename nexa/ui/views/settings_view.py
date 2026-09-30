from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from qfluentwidgets import (SubtitleLabel, SwitchSettingCard, ComboBoxSettingCard,
                            FluentIcon as FIF, ExpandLayout, SettingCardGroup, qconfig,
                            PushSettingCard, InfoBar, InfoBarPosition, SmoothScrollArea)
from nexa.infra.database import get_session, UserSettings, ClipboardItem, Activity, get_setting, set_setting
import winreg
import os
import sys

class SettingsView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("SettingsView")
        self.setStyleSheet("#SettingsView { background-color: transparent; }")
        
        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        
        self.scrollArea = SmoothScrollArea(self)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        
        self.scrollWidget = QWidget()
        self.scrollWidget.setObjectName("scrollWidget")
        self.scrollWidget.setStyleSheet("#scrollWidget { background-color: transparent; }")
        
        self.scrollLayout = QVBoxLayout(self.scrollWidget)
        self.scrollLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scrollLayout.setContentsMargins(40, 40, 40, 40)
        
        self.titleLabel = SubtitleLabel("Settings")
        self.scrollLayout.addWidget(self.titleLabel)
        self.scrollLayout.addSpacing(20)
        
        # General Settings Group
        self.generalGroup = SettingCardGroup("General", self)
        
        self.themeCard = ComboBoxSettingCard(
            qconfig.themeMode,
            FIF.BRUSH,
            "Application Theme",
            "Change the appearance of NEXA",
            texts=["Light", "Dark", "System default"],
            parent=self.generalGroup
        )
        self.generalGroup.addSettingCard(self.themeCard)
        
        self.startupCard = SwitchSettingCard(
            FIF.POWER_BUTTON,
            "Run at startup",
            "Automatically start NEXA when you log into Windows",
            parent=self.generalGroup
        )
        self.startupCard.checkedChanged.connect(self.toggle_startup)
        self.generalGroup.addSettingCard(self.startupCard)
        
        self.scrollLayout.addWidget(self.generalGroup)
        
        # Privacy & Data Group
        self.privacyGroup = SettingCardGroup("Privacy & Data", self)
        
        self.activityCard = SwitchSettingCard(
            FIF.HISTORY,
            "Activity Tracking",
            "Remember recently opened apps and workspaces",
            parent=self.privacyGroup
        )
        self.activityCard.checkedChanged.connect(lambda c: set_setting('track_activity', str(c)))
        self.privacyGroup.addSettingCard(self.activityCard)
        
        self.clipboardCard = SwitchSettingCard(
            FIF.COPY,
            "Clipboard History",
            "Save copied text and images to local database",
            parent=self.privacyGroup
        )
        self.clipboardCard.checkedChanged.connect(lambda c: set_setting('track_clipboard', str(c)))
        self.privacyGroup.addSettingCard(self.clipboardCard)
        
        self.scrollLayout.addWidget(self.privacyGroup)
        
        # Data Management Group
        self.dataGroup = SettingCardGroup("Data Management", self)
        
        self.clearActivityCard = PushSettingCard(
            "Clear",
            FIF.DELETE,
            "Clear Activity Timeline",
            "Permanently delete all recorded activity history",
            self.dataGroup
        )
        self.clearActivityCard.clicked.connect(self.clear_activity_history)
        self.dataGroup.addSettingCard(self.clearActivityCard)
        
        self.clearClipboardCard = PushSettingCard(
            "Clear",
            FIF.DELETE,
            "Clear Clipboard History",
            "Permanently delete all saved clipboard items",
            self.dataGroup
        )
        self.clearClipboardCard.clicked.connect(self.clear_clipboard_history)
        self.dataGroup.addSettingCard(self.clearClipboardCard)
        
        self.scrollLayout.addWidget(self.dataGroup)
        self.scrollLayout.addStretch(1)
        
        self.scrollArea.setWidget(self.scrollWidget)
        self.vBoxLayout.addWidget(self.scrollArea)
        
        self.load_settings()

    def load_settings(self):
        # Startup
        key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
        app_name = "NEXA"
        is_startup = False
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_READ) as key:
                winreg.QueryValueEx(key, app_name)
                is_startup = True
        except:
            pass
        self.startupCard.setChecked(is_startup)
        
        # DB Settings
        self.activityCard.setChecked(get_setting('track_activity', 'True') == 'True')
        self.clipboardCard.setChecked(get_setting('track_clipboard', 'True') == 'True')

    def toggle_startup(self, checked):
        key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
        app_name = "NEXA"
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_WRITE) as key:
                if checked:
                    # In real app, this should be the path to the compiled .exe
                    exe_path = sys.executable
                    script_path = os.path.abspath(sys.argv[0])
                    cmd = f'"{exe_path}" "{script_path}"'
                    winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, cmd)
                else:
                    winreg.DeleteValue(key, app_name)
        except Exception as e:
            print("Failed to toggle startup:", e)

    def clear_activity_history(self):
        session = get_session()
        session.query(Activity).delete()
        session.commit()
        session.close()
        InfoBar.success('Success', 'Activity history cleared!', duration=2000, parent=self.window())

    def clear_clipboard_history(self):
        session = get_session()
        session.query(ClipboardItem).delete()
        session.commit()
        session.close()
        InfoBar.success('Success', 'Clipboard history cleared!', duration=2000, parent=self.window())
