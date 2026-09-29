import os
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime

Base = declarative_base()

class UserSettings(Base):
    __tablename__ = 'user_settings'
    id = Column(Integer, primary_key=True)
    key = Column(String(100), unique=True, nullable=False)
    value = Column(Text, nullable=False)

class Workspace(Base):
    __tablename__ = 'workspaces'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    is_favorite = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    items = relationship("WorkspaceItem", back_populates="workspace", cascade="all, delete-orphan")

class WorkspaceItem(Base):
    __tablename__ = 'workspace_items'
    id = Column(Integer, primary_key=True)
    workspace_id = Column(Integer, ForeignKey('workspaces.id'), nullable=False)
    item_type = Column(String(50), nullable=False) # 'app', 'folder', 'url', 'command'
    path = Column(String(500), nullable=False)
    
    workspace = relationship("Workspace", back_populates="items")

class ClipboardItem(Base):
    __tablename__ = 'clipboard_history'
    id = Column(Integer, primary_key=True)
    content_type = Column(String(50), nullable=False) # 'text', 'image', 'file'
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_pinned = Column(Boolean, default=False)

def init_db(db_path="nexa.db"):
    engine = create_engine(f"sqlite:///{db_path}", echo=False)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)
