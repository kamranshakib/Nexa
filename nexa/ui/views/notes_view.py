from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFrame
from qfluentwidgets import (TitleLabel, LineEdit, PrimaryPushButton, SmoothScrollArea, 
                            CheckBox, CardWidget, BodyLabel, TransparentToolButton, FluentIcon as FIF)
from nexa.infra.database import get_session, Note

class NoteCard(CardWidget):
    def __init__(self, note_id, title, is_completed, parent_view):
        super().__init__()
        self.note_id = note_id
        self.parent_view = parent_view
        
        self.setFixedHeight(60)
        self.hBoxLayout = QHBoxLayout(self)
        self.hBoxLayout.setContentsMargins(15, 0, 15, 0)
        
        self.checkbox = CheckBox()
        self.checkbox.setChecked(is_completed)
        self.checkbox.stateChanged.connect(self.toggle_completed)
        self.hBoxLayout.addWidget(self.checkbox)
        
        self.titleLabel = BodyLabel(title)
        if is_completed:
            self.titleLabel.setStyleSheet("text-decoration: line-through; color: gray;")
        self.hBoxLayout.addWidget(self.titleLabel, 1)
        
        self.deleteBtn = TransparentToolButton(FIF.DELETE, self)
        self.deleteBtn.clicked.connect(self.delete_note)
        self.hBoxLayout.addWidget(self.deleteBtn)
        
    def toggle_completed(self, state):
        is_checked = state == Qt.CheckState.Checked.value
        session = get_session()
        note = session.query(Note).filter_by(id=self.note_id).first()
        if note:
            note.is_completed = is_checked
            session.commit()
        session.close()
        
        if is_checked:
            self.titleLabel.setStyleSheet("text-decoration: line-through; color: gray;")
        else:
            self.titleLabel.setStyleSheet("")
            
    def delete_note(self):
        session = get_session()
        note = session.query(Note).filter_by(id=self.note_id).first()
        if note:
            session.delete(note)
            session.commit()
        session.close()
        self.parent_view.load_notes()

class NotesView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("NotesView")
        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setContentsMargins(40, 40, 40, 40)
        
        self.titleLabel = TitleLabel("Notes & Todos", self)
        self.vBoxLayout.addWidget(self.titleLabel, alignment=Qt.AlignmentFlag.AlignTop)
        
        self.inputLayout = QHBoxLayout()
        self.noteInput = LineEdit()
        self.noteInput.setPlaceholderText("Add a new note or task...")
        self.noteInput.returnPressed.connect(self.add_note)
        self.inputLayout.addWidget(self.noteInput, 1)
        
        self.addBtn = PrimaryPushButton("Add")
        self.addBtn.clicked.connect(self.add_note)
        self.inputLayout.addWidget(self.addBtn)
        
        self.vBoxLayout.addLayout(self.inputLayout)
        self.vBoxLayout.addSpacing(20)
        
        self.scrollArea = SmoothScrollArea(self)
        self.scrollArea.setWidgetResizable(True)
        self.scrollWidget = QWidget()
        self.scrollWidget.setObjectName("notesScrollWidget")
        self.scrollWidget.setStyleSheet("#notesScrollWidget { background: transparent; }")
        self.notesLayout = QVBoxLayout(self.scrollWidget)
        self.notesLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.notesLayout.setSpacing(10)
        self.scrollArea.setWidget(self.scrollWidget)
        
        self.vBoxLayout.addWidget(self.scrollArea, 1)
        
        self.load_notes()
        
    def add_note(self):
        title = self.noteInput.text().strip()
        if not title:
            return
            
        session = get_session()
        new_note = Note(title=title)
        session.add(new_note)
        session.commit()
        session.close()
        
        self.noteInput.clear()
        self.load_notes()
        
    def load_notes(self):
        while self.notesLayout.count():
            item = self.notesLayout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
        session = get_session()
        notes = session.query(Note).order_by(Note.created_at.desc()).all()
        for note in notes:
            card = NoteCard(note.id, note.title, note.is_completed, self)
            self.notesLayout.addWidget(card)
        session.close()
