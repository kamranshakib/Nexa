from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from qfluentwidgets import (CardWidget, SubtitleLabel, BodyLabel, TitleLabel,
                            PrimaryPushButton, PushButton, SearchLineEdit,
                            FluentIcon as FIF)

class HomeView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("HomeView")
        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.vBoxLayout.setContentsMargins(40, 40, 40, 40)
        
        # Greeting
        self.greetingLabel = TitleLabel("Good Morning")
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
        self.continueTitle = BodyLabel("Edulinn Development")
        self.continueBtn = PrimaryPushButton("Continue")
        self.continueLayout.addWidget(self.continueTitle)
        self.continueLayout.addStretch(1)
        self.continueLayout.addWidget(self.continueBtn)
        self.continueCard.setFixedWidth(500)
        self.vBoxLayout.addWidget(self.continueCard)
        
        self.vBoxLayout.addSpacing(30)
        
        # Quick Actions
        self.actionsLabel = SubtitleLabel("Quick Actions")
        self.vBoxLayout.addWidget(self.actionsLabel)
        
        self.actionsLayout = QHBoxLayout()
        self.btnLaunch = PushButton(FIF.SEARCH, "Launch")
        self.btnClipboard = PushButton(FIF.COPY, "Clipboard")
        self.btnFiles = PushButton(FIF.DOCUMENT, "Files")
        self.btnFocus = PushButton(FIF.ALARM, "Focus")
        
        self.actionsLayout.addWidget(self.btnLaunch)
        self.actionsLayout.addWidget(self.btnClipboard)
        self.actionsLayout.addWidget(self.btnFiles)
        self.actionsLayout.addWidget(self.btnFocus)
        self.actionsLayout.addStretch(1)
        
        self.vBoxLayout.addLayout(self.actionsLayout)
        
        self.vBoxLayout.addSpacing(30)
        
        # System status
        self.sysLabel = SubtitleLabel("System")
        self.vBoxLayout.addWidget(self.sysLabel)
        
        self.sysCard = CardWidget()
        self.sysCard.setFixedWidth(500)
        self.sysLayout = QHBoxLayout(self.sysCard)
        self.sysText = BodyLabel("CPU: 18%  |  Memory: 47%  |  Storage: 62%")
        self.sysLayout.addWidget(self.sysText)
        self.vBoxLayout.addWidget(self.sysCard)
        
        self.vBoxLayout.addStretch(1)
