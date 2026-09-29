from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from qfluentwidgets import (SubtitleLabel, CardWidget, PrimaryPushButton, 
                            PushButton, FlowLayout, BodyLabel, FluentIcon as FIF)

class WorkspaceCard(CardWidget):
    def __init__(self, title, apps_count, parent=None):
        super().__init__(parent=parent)
        self.setFixedSize(250, 150)
        self.vBoxLayout = QVBoxLayout(self)
        
        self.titleLabel = SubtitleLabel(title, self)
        self.vBoxLayout.addWidget(self.titleLabel)
        
        self.descLabel = BodyLabel(f"{apps_count} apps / folders configured", self)
        self.descLabel.setStyleSheet("color: gray;")
        self.vBoxLayout.addWidget(self.descLabel)
        
        self.vBoxLayout.addStretch(1)
        
        self.actionLayout = QHBoxLayout()
        self.btnLaunch = PrimaryPushButton("Launch")
        self.btnEdit = PushButton("Edit")
        self.actionLayout.addWidget(self.btnLaunch)
        self.actionLayout.addWidget(self.btnEdit)
        self.vBoxLayout.addLayout(self.actionLayout)

class WorkspacesView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("WorkspacesView")
        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.vBoxLayout.setContentsMargins(40, 40, 40, 40)
        
        self.headerLayout = QHBoxLayout()
        self.titleLabel = SubtitleLabel("Your Workspaces")
        self.btnNew = PrimaryPushButton(FIF.ADD, "New Workspace")
        self.headerLayout.addWidget(self.titleLabel)
        self.headerLayout.addStretch(1)
        self.headerLayout.addWidget(self.btnNew)
        self.vBoxLayout.addLayout(self.headerLayout)
        
        self.vBoxLayout.addSpacing(30)
        
        # Grid of workspaces
        self.flowLayout = FlowLayout()
        
        # Dummy data
        self.flowLayout.addWidget(WorkspaceCard("Edulinn Development", 5))
        self.flowLayout.addWidget(WorkspaceCard("University", 3))
        self.flowLayout.addWidget(WorkspaceCard("Gaming", 2))
        self.flowLayout.addWidget(WorkspaceCard("General Work", 4))
        
        self.vBoxLayout.addLayout(self.flowLayout)
        self.vBoxLayout.addStretch(1)
