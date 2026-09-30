from PyQt6.QtCore import Qt, QSize
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QScrollArea
from qfluentwidgets import (CardWidget, SubtitleLabel, BodyLabel, TitleLabel, 
                            FluentIcon as FIF, IconWidget, setFont, PrimaryPushButton, PushButton, ScrollArea)
from nexa.infra.database import get_session, Activity
from datetime import datetime
import webbrowser
import subprocess
import os

def time_ago(dt: datetime) -> str:
    now = datetime.utcnow()
    diff = now - dt
    if diff.days > 0:
        return f"{diff.days} days ago"
    elif diff.seconds >= 3600:
        return f"{diff.seconds // 3600} hours ago"
    elif diff.seconds >= 60:
        return f"{diff.seconds // 60} mins ago"
    else:
        return "Just now"

class TimelineItem(QWidget):
    def __init__(self, activity: Activity, parent=None):
        super().__init__(parent=parent)
        self.setFixedHeight(80)
        self.activity = activity
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Icon mapping
        icon_map = {
            'workspace': FIF.FOLDER,
            'clipboard': FIF.COPY,
            'focus': FIF.STOP_WATCH,
            'file': FIF.DOCUMENT
        }
        icon = icon_map.get(activity.activity_type, FIF.HISTORY)
        
        self.iconWidget = IconWidget(icon)
        self.iconWidget.setFixedSize(24, 24)
        layout.addWidget(self.iconWidget)
        
        layout.addSpacing(15)
        
        # Content
        contentLayout = QVBoxLayout()
        contentLayout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        
        self.titleLabel = SubtitleLabel(activity.title)
        setFont(self.titleLabel, 14)
        self.descLabel = BodyLabel(activity.description or "")
        self.descLabel.setStyleSheet("color: gray;")
        
        contentLayout.addWidget(self.titleLabel)
        contentLayout.addWidget(self.descLabel)
        
        layout.addLayout(contentLayout)
        layout.addStretch(1)
        
        # Time
        self.timeLabel = BodyLabel(time_ago(activity.created_at))
        self.timeLabel.setStyleSheet("color: gray; margin-right: 20px;")
        layout.addWidget(self.timeLabel)
        
        # Action Button
        if activity.activity_type == 'workspace':
            self.actionBtn = PrimaryPushButton(FIF.PLAY, "Launch Again")
            self.actionBtn.clicked.connect(self.on_launch_workspace)
            layout.addWidget(self.actionBtn)
        elif activity.activity_type == 'clipboard':
            self.actionBtn = PushButton(FIF.COPY, "Copy Again")
            self.actionBtn.clicked.connect(self.on_copy_clipboard)
            layout.addWidget(self.actionBtn)

    def on_launch_workspace(self):
        try:
            ws_id = int(self.activity.action_data)
            from nexa.infra.database import get_session, Workspace
            session = get_session()
            ws = session.query(Workspace).filter_by(id=ws_id).first()
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
                        print(f"Failed: {e}")
            session.close()
        except Exception as e:
            print("Launch failed:", e)

    def on_copy_clipboard(self):
        if self.activity.action_data:
            from PyQt6.QtWidgets import QApplication
            QApplication.clipboard().setText(self.activity.action_data)

class ActivityView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("ActivityView")
        self.setStyleSheet("#ActivityView { background-color: transparent; }")
        
        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.vBoxLayout.setContentsMargins(40, 40, 40, 40)
        
        # Header
        self.headerLayout = QHBoxLayout()
        
        title_layout = QVBoxLayout()
        self.titleLabel = TitleLabel("Activity Timeline")
        self.subtitleLabel = BodyLabel("Your recent activities and events (Actionable Time Machine)")
        self.subtitleLabel.setStyleSheet("color: gray; font-size: 14px;")
        title_layout.addWidget(self.titleLabel)
        title_layout.addWidget(self.subtitleLabel)
        
        self.headerLayout.addLayout(title_layout)
        self.headerLayout.addStretch(1)
        
        self.btnRefresh = PushButton(FIF.SYNC, "Refresh")
        self.btnRefresh.clicked.connect(self.load_activities)
        self.headerLayout.addWidget(self.btnRefresh)
        
        self.vBoxLayout.addLayout(self.headerLayout)
        self.vBoxLayout.addSpacing(20)
        
        # Timeline Area
        self.scrollArea = QScrollArea()
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        
        self.scrollWidget = QWidget()
        self.scrollWidget.setObjectName("scrollWidget")
        self.scrollWidget.setStyleSheet("#scrollWidget { background-color: transparent; }")
        self.scrollLayout = QVBoxLayout(self.scrollWidget)
        self.scrollLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        self.scrollArea.setWidget(self.scrollWidget)
        self.vBoxLayout.addWidget(self.scrollArea)
        
        self.load_activities()
        
    def load_activities(self):
        # Clear
        while self.scrollLayout.count():
            item = self.scrollLayout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
        try:
            session = get_session()
            activities = session.query(Activity).order_by(Activity.id.desc()).limit(30).all()
            if not activities:
                emptyLabel = SubtitleLabel("No activities recorded yet.\nStart launching workspaces or copying text to see them here!")
                emptyLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.scrollLayout.addWidget(emptyLabel)
            else:
                for act in activities:
                    self.add_timeline_item(act)
            session.close()
        except Exception as e:
            print("Error loading activities:", e)
            
        self.scrollLayout.addStretch(1)
            
    def add_timeline_item(self, activity):
        item = TimelineItem(activity)
        card = CardWidget()
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(15, 10, 15, 10)
        card_layout.addWidget(item)
        
        self.scrollLayout.addWidget(card)
        self.scrollLayout.addSpacing(10)
