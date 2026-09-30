from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLineEdit
from qfluentwidgets import (SubtitleLabel, CardWidget, PrimaryPushButton, 
                            PushButton, FlowLayout, BodyLabel, FluentIcon as FIF,
                            MessageBoxBase)
import os
import webbrowser
import subprocess
from nexa.infra.database import get_session, Workspace
from nexa.ui.views.workspace_edit_dialog import EditWorkspaceDialog

class WorkspaceCard(CardWidget):
    deleteSignal = pyqtSignal(int)
    editSignal = pyqtSignal(int)
    launchSignal = pyqtSignal(int)
    
    def __init__(self, workspace: Workspace, parent=None):
        super().__init__(parent=parent)
        self.workspace_id = workspace.id
        self.setFixedSize(250, 150)
        self.vBoxLayout = QVBoxLayout(self)
        
        self.titleLabel = SubtitleLabel(workspace.name, self)
        self.vBoxLayout.addWidget(self.titleLabel)
        
        apps_count = len(workspace.items) if workspace.items else 0
        self.descLabel = BodyLabel(f"{apps_count} apps / folders configured", self)
        self.descLabel.setStyleSheet("color: gray;")
        self.vBoxLayout.addWidget(self.descLabel)
        
        self.vBoxLayout.addStretch(1)
        
        self.actionLayout = QHBoxLayout()
        self.btnLaunch = PrimaryPushButton("Launch")
        self.btnEdit = PushButton("Edit")
        self.btnDelete = PushButton(FIF.DELETE, "")
        
        self.actionLayout.addWidget(self.btnLaunch)
        self.actionLayout.addWidget(self.btnEdit)
        self.actionLayout.addWidget(self.btnDelete)
        self.vBoxLayout.addLayout(self.actionLayout)
        
        self.btnLaunch.clicked.connect(lambda: self.launchSignal.emit(self.workspace_id))
        self.btnEdit.clicked.connect(lambda: self.editSignal.emit(self.workspace_id))
        self.btnDelete.clicked.connect(lambda: self.deleteSignal.emit(self.workspace_id))

class NewWorkspaceDialog(MessageBoxBase):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.titleLabel = SubtitleLabel("New Workspace", self)
        self.nameEdit = QLineEdit(self)
        self.nameEdit.setPlaceholderText("Workspace Name...")
        
        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addWidget(self.nameEdit)
        
        self.widget.setMinimumWidth(300)

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
        self.btnNew.clicked.connect(self.on_new_workspace)
        
        self.headerLayout.addWidget(self.titleLabel)
        self.headerLayout.addStretch(1)
        self.headerLayout.addWidget(self.btnNew)
        self.vBoxLayout.addLayout(self.headerLayout)
        
        self.vBoxLayout.addSpacing(30)
        
        # Grid of workspaces
        self.flowLayout = FlowLayout()
        self.vBoxLayout.addLayout(self.flowLayout)
        self.vBoxLayout.addStretch(1)
        
        self.load_workspaces()
        
    def load_workspaces(self):
        # clear existing widgets
        while self.flowLayout.count():
            item = self.flowLayout.takeAt(0)
            if item:
                w = item.widget() if hasattr(item, 'widget') else item
                if w:
                    w.deleteLater()
                
        session = get_session()
        workspaces = session.query(Workspace).all()
        for ws in workspaces:
            card = WorkspaceCard(ws)
            card.deleteSignal.connect(self.on_delete_workspace)
            card.editSignal.connect(self.on_edit_workspace)
            card.launchSignal.connect(self.on_launch_workspace)
            self.flowLayout.addWidget(card)
        session.close()

    def on_new_workspace(self):
        dialog = NewWorkspaceDialog(self)
        if dialog.exec():
            name = dialog.nameEdit.text().strip()
            if name:
                session = get_session()
                # Check if exists
                existing = session.query(Workspace).filter_by(name=name).first()
                if not existing:
                    ws = Workspace(name=name)
                    session.add(ws)
                    session.commit()
                session.close()
                self.load_workspaces()
                
    def on_delete_workspace(self, ws_id):
        session = get_session()
        ws = session.query(Workspace).filter_by(id=ws_id).first()
        if ws:
            session.delete(ws)
            session.commit()
        session.close()
        self.load_workspaces()

    def on_edit_workspace(self, ws_id):
        dialog = EditWorkspaceDialog(ws_id, self)
        dialog.exec()
        self.load_workspaces()

    def on_launch_workspace(self, ws_id):
        from nexa.infra.database import get_session, Workspace, log_activity
        session = get_session()
        ws = session.query(Workspace).filter_by(id=ws_id).first()
        if ws:
            # Log the activity
            log_activity('workspace', 'Workspace Launched', f"Launched '{ws.name}' workspace", str(ws.id))
            for item in ws.items:
                try:
                    if item.item_type == 'url':
                        webbrowser.open(item.path)
                    elif item.item_type == 'command':
                        subprocess.Popen(item.path, shell=True)
                    else: # file, folder
                        os.startfile(item.path)
                except Exception as e:
                    print(f"Failed to launch {item.path}: {e}")
        session.close()

