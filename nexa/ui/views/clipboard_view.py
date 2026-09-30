from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QClipboard
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QApplication
from qfluentwidgets import (SubtitleLabel, CardWidget, BodyLabel, 
                            PrimaryPushButton, PushButton, FluentIcon as FIF,
                            ScrollArea, CaptionLabel, StrongBodyLabel, ComboBox)
from nexa.infra.database import get_session, ClipboardItem
import datetime

class ClipboardCard(CardWidget):
    deleteSignal = pyqtSignal(int)
    copySignal = pyqtSignal(str)
    
    def __init__(self, item: ClipboardItem, parent=None):
        super().__init__(parent=parent)
        self.item_id = item.id
        self.content_text = item.content
        self.setMinimumHeight(100)
        
        self.hBoxLayout = QHBoxLayout(self)
        self.hBoxLayout.setContentsMargins(20, 15, 20, 15)
        
        self.textLayout = QVBoxLayout()
        
        # Clean newlines and limit
        display_text = self.content_text.replace('\n', ' ')
        if len(display_text) > 130:
            display_text = display_text[:130] + "..."
            
        self.contentLabel = StrongBodyLabel(display_text, self)
        self.contentLabel.setWordWrap(True)
        
        # Format the time
        if item.created_at:
            utc_time = item.created_at.replace(tzinfo=datetime.timezone.utc)
            local_time = utc_time.astimezone()
            time_str = local_time.strftime("%A, %Y-%m-%d  %I:%M %p")
        else:
            time_str = "Unknown time"
            
        self.timeLabel = CaptionLabel(time_str, self)
        
        self.textLayout.addWidget(self.contentLabel)
        self.textLayout.addSpacing(5)
        self.textLayout.addWidget(self.timeLabel)
        self.textLayout.addStretch(1)
        
        self.hBoxLayout.addLayout(self.textLayout, 1)
        
        self.actionLayout = QVBoxLayout()
        self.btnCopy = PrimaryPushButton(FIF.COPY, "Copy")
        self.btnCopy.setFixedWidth(100)
        self.btnDelete = PushButton(FIF.DELETE, "Delete")
        self.btnDelete.setFixedWidth(100)
        
        self.actionLayout.addWidget(self.btnCopy)
        self.actionLayout.addSpacing(5)
        self.actionLayout.addWidget(self.btnDelete)
        self.actionLayout.addStretch(1)
        
        self.hBoxLayout.addLayout(self.actionLayout)
        
        self.btnCopy.clicked.connect(lambda: self.copySignal.emit(self.content_text))
        self.btnDelete.clicked.connect(lambda: self.deleteSignal.emit(self.item_id))

class ClipboardView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("ClipboardView")
        
        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.vBoxLayout.setContentsMargins(40, 40, 40, 40)
        
        self.headerLayout = QHBoxLayout()
        self.titleLabel = SubtitleLabel("Clipboard History")
        
        self.filterCombo = ComboBox()
        self.filterCombo.addItems(["All Time", "Today", "Yesterday", "Last 7 Days"])
        self.filterCombo.currentIndexChanged.connect(self.load_items)
        
        self.btnClear = PushButton(FIF.DELETE, "Clear All")
        
        self.headerLayout.addWidget(self.titleLabel)
        self.headerLayout.addStretch(1)
        self.headerLayout.addWidget(self.filterCombo)
        self.headerLayout.addSpacing(10)
        self.headerLayout.addWidget(self.btnClear)
        self.vBoxLayout.addLayout(self.headerLayout)
        self.vBoxLayout.addSpacing(20)
        
        self.scrollArea = ScrollArea(self)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        self.scrollWidget = QWidget()
        self.listLayout = QVBoxLayout(self.scrollWidget)
        self.listLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        self.scrollArea.setWidget(self.scrollWidget)
        self.vBoxLayout.addWidget(self.scrollArea)
        
        self.btnClear.clicked.connect(self.clear_all)
        
        self.load_items()
        
    def load_items(self):
        # Clear current
        while self.listLayout.count():
            item = self.listLayout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
        session = get_session()
        query = session.query(ClipboardItem).order_by(ClipboardItem.id.desc())
        
        filter_text = self.filterCombo.currentText()
        now = datetime.datetime.utcnow()
        if filter_text == "Today":
            start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            query = query.filter(ClipboardItem.created_at >= start)
        elif filter_text == "Yesterday":
            start = (now - datetime.timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
            end = now.replace(hour=0, minute=0, second=0, microsecond=0)
            query = query.filter(ClipboardItem.created_at >= start, ClipboardItem.created_at < end)
        elif filter_text == "Last 7 Days":
            start = now - datetime.timedelta(days=7)
            query = query.filter(ClipboardItem.created_at >= start)
            
        items = query.limit(50).all()
        
        for item in items:
            card = ClipboardCard(item)
            card.copySignal.connect(self.copy_to_clipboard)
            card.deleteSignal.connect(self.delete_item)
            self.listLayout.addWidget(card)
        session.close()

    def copy_to_clipboard(self, text):
        clipboard = QApplication.clipboard()
        clipboard.setText(text)
        
    def delete_item(self, item_id):
        session = get_session()
        item = session.query(ClipboardItem).filter_by(id=item_id).first()
        if item:
            session.delete(item)
            session.commit()
        session.close()
        self.load_items()

    def clear_all(self):
        session = get_session()
        session.query(ClipboardItem).delete()
        session.commit()
        session.close()
        self.load_items()

    def refresh(self):
        self.load_items()
