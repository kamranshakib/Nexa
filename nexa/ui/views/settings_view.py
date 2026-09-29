from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from qfluentwidgets import (SubtitleLabel, SwitchSettingCard, ComboBoxSettingCard,
                            FluentIcon as FIF, ExpandLayout, SettingCardGroup)

class SettingsView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("SettingsView")
        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.vBoxLayout.setContentsMargins(40, 40, 40, 40)
        
        self.titleLabel = SubtitleLabel("Settings")
        self.vBoxLayout.addWidget(self.titleLabel)
        
        self.vBoxLayout.addSpacing(20)
        
        # General Settings Group
        self.generalGroup = SettingCardGroup("General", self)
        
        self.themeCard = ComboBoxSettingCard(
            None,
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
        self.generalGroup.addSettingCard(self.startupCard)
        
        self.vBoxLayout.addWidget(self.generalGroup)
        
        # Privacy & Data Group
        self.privacyGroup = SettingCardGroup("Privacy & Data", self)
        
        self.activityCard = SwitchSettingCard(
            FIF.HISTORY,
            "Activity Tracking",
            "Remember recently opened apps and workspaces (stored locally)",
            parent=self.privacyGroup
        )
        self.privacyGroup.addSettingCard(self.activityCard)
        
        self.clipboardCard = SwitchSettingCard(
            FIF.COPY,
            "Clipboard History",
            "Save copied text and images (stored locally)",
            parent=self.privacyGroup
        )
        self.privacyGroup.addSettingCard(self.clipboardCard)
        
        self.vBoxLayout.addWidget(self.privacyGroup)
        self.vBoxLayout.addStretch(1)
