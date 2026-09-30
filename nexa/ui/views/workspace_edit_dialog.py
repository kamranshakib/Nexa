from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QFileDialog, QInputDialog, QListWidget, QListWidgetItem, QLineEdit
from qfluentwidgets import MessageBoxBase, SubtitleLabel, PushButton, PrimaryPushButton, FluentIcon as FIF
from nexa.infra.database import get_session, Workspace, WorkspaceItem
import os

class AppPickerDialog(MessageBoxBase):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.titleLabel = SubtitleLabel("Select Installed App", self)
        self.searchEdit = QLineEdit(self)
        self.searchEdit.setPlaceholderText("Search apps (e.g. Postman)...")
        self.appsList = QListWidget(self)
        
        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addWidget(self.searchEdit)
        self.viewLayout.addWidget(self.appsList)
        
        self.widget.setMinimumWidth(400)
        self.widget.setMinimumHeight(500)
        
        self.all_apps = self.get_start_menu_apps()
        self.populate_list(self.all_apps)
        
        self.searchEdit.textChanged.connect(self.filter_apps)
        
    def get_start_menu_apps(self):
        apps = []
        paths_to_scan = [
            os.path.join(os.environ.get('APPDATA', ''), r'Microsoft\Windows\Start Menu\Programs'),
            os.path.join(os.environ.get('PROGRAMDATA', ''), r'Microsoft\Windows\Start Menu\Programs')
        ]
        for base_path in paths_to_scan:
            if not os.path.exists(base_path):
                continue
            for root, dirs, files in os.walk(base_path):
                for file in files:
                    if file.lower().endswith('.lnk'):
                        app_name = os.path.splitext(file)[0]
                        if "uninstall" in app_name.lower(): continue
                        full_path = os.path.join(root, file)
                        apps.append((app_name, full_path))
        
        apps.sort(key=lambda x: x[0].lower())
        unique_apps = {}
        for name, path in apps:
            if name not in unique_apps:
                unique_apps[name] = path
        return [(k, v) for k, v in unique_apps.items()]

    def populate_list(self, apps_to_show):
        self.appsList.clear()
        for name, path in apps_to_show:
            item = QListWidgetItem(name)
            item.setData(Qt.ItemDataRole.UserRole, path)
            self.appsList.addItem(item)
            
    def filter_apps(self, text):
        text = text.lower()
        filtered = [(name, path) for name, path in self.all_apps if text in name.lower()]
        self.populate_list(filtered)

class EditWorkspaceDialog(MessageBoxBase):
    def __init__(self, workspace_id, parent=None):
        super().__init__(parent)
        self.workspace_id = workspace_id
        self.widget.setMinimumWidth(500)
        self.widget.setMinimumHeight(400)
        
        # UI Elements
        self.titleLabel = SubtitleLabel("Edit Workspace", self)
        
        self.itemsList = QListWidget(self)
        
        self.btnAddApp = PushButton(FIF.APPLICATION, "Add App")
        self.btnAddFile = PushButton(FIF.DOCUMENT, "Add File")
        self.btnAddFolder = PushButton(FIF.FOLDER, "Add Folder")
        self.btnAddUrl = PushButton(FIF.LINK, "Add URL")
        self.btnAddProject = PrimaryPushButton(FIF.CODE, "Add Antigravity Project")
        self.btnRemove = PushButton(FIF.DELETE, "Remove Selected")
        self.btnSetAntigravity = PrimaryPushButton(FIF.CODE, "Set as Antigravity Project")
        
        # Layouts
        self.viewLayout.addWidget(self.titleLabel)
        
        btnLayout = QHBoxLayout()
        btnLayout.addWidget(self.btnAddApp)
        btnLayout.addWidget(self.btnAddFile)
        btnLayout.addWidget(self.btnAddFolder)
        btnLayout.addWidget(self.btnAddUrl)
        self.viewLayout.addLayout(btnLayout)
        
        self.viewLayout.addWidget(self.itemsList)
        
        actionLayout = QHBoxLayout()
        actionLayout.addWidget(self.btnSetAntigravity)
        actionLayout.addWidget(self.btnRemove)
        self.viewLayout.addLayout(actionLayout)
        
        # Connections
        self.btnAddApp.clicked.connect(self.add_installed_app)
        self.btnAddFile.clicked.connect(self.add_file)
        self.btnAddFolder.clicked.connect(self.add_folder)
        self.btnAddUrl.clicked.connect(self.add_url)
        self.btnRemove.clicked.connect(self.remove_selected)
        self.btnSetAntigravity.clicked.connect(self.set_as_antigravity)
        
        self.load_data()
        
    def load_data(self):
        self.itemsList.clear()
        session = get_session()
        ws = session.query(Workspace).filter_by(id=self.workspace_id).first()
        if ws:
            self.titleLabel.setText(f"Edit Workspace: {ws.name}")
            for item in ws.items:
                list_item = QListWidgetItem(f"[{item.item_type.upper()}] {item.path}")
                list_item.setData(Qt.ItemDataRole.UserRole, item.id)
                self.itemsList.addItem(list_item)
        session.close()

    def add_item_to_db(self, item_type, path):
        session = get_session()
        new_item = WorkspaceItem(workspace_id=self.workspace_id, item_type=item_type, path=path)
        session.add(new_item)
        session.commit()
        session.close()
        self.load_data()

    def add_installed_app(self):
        dialog = AppPickerDialog(self)
        if dialog.exec():
            selected = dialog.appsList.currentItem()
            if selected:
                app_path = selected.data(Qt.ItemDataRole.UserRole)
                self.add_item_to_db('file', app_path)

    def add_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File")
        if file_path:
            self.add_item_to_db('file', file_path)
            
    def add_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder_path:
            self.add_item_to_db('folder', folder_path)
            
    def add_url(self):
        url, ok = QInputDialog.getText(self, "Add URL", "Enter URL (e.g., https://google.com):")
        if ok and url:
            self.add_item_to_db('url', url)
            
    def set_as_antigravity(self):
        selected = self.itemsList.currentItem()
        if selected:
            item_id = selected.data(Qt.ItemDataRole.UserRole)
            session = get_session()
            item = session.query(WorkspaceItem).filter_by(id=item_id).first()
            if item:
                if item.item_type in ['file', 'folder']:
                    # Convert to Antigravity command
                    item.item_type = 'command'
                    item.path = f'agy-ide "{item.path}"'
                    session.commit()
            session.close()
            self.load_data()

    def remove_selected(self):
        selected = self.itemsList.currentItem()
        if selected:
            item_id = selected.data(Qt.ItemDataRole.UserRole)
            session = get_session()
            item = session.query(WorkspaceItem).filter_by(id=item_id).first()
            if item:
                session.delete(item)
                session.commit()
            session.close()
            self.load_data()
