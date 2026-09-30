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

class Activity(Base):
    __tablename__ = 'activities'
    id = Column(Integer, primary_key=True)
    activity_type = Column(String(50), nullable=False) # 'workspace', 'clipboard', 'focus', 'file'
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    action_data = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

SessionLocal = None

def init_db(db_path="nexa.db"):
    global SessionLocal
    engine = create_engine(f"sqlite:///{db_path}", echo=False)
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    return SessionLocal

def get_session():
    if SessionLocal:
        return SessionLocal()
    raise Exception("Database not initialized")

def log_activity(activity_type: str, title: str, description: str = None, action_data: str = None):
    try:
        if get_setting('track_activity', 'True') != 'True':
            return
            
        session = get_session()
        new_activity = Activity(
            activity_type=activity_type, 
            title=title, 
            description=description, 
            action_data=action_data
        )
        session.add(new_activity)
        session.commit()
        session.close()
    except Exception as e:
        print(f"Failed to log activity: {e}")

def get_setting(key, default_val):
    try:
        session = get_session()
        s = session.query(UserSettings).filter_by(key=key).first()
        val = s.value if s else default_val
        session.close()
        return val
    except:
        return default_val

def set_setting(key, val):
    try:
        session = get_session()
        s = session.query(UserSettings).filter_by(key=key).first()
        if s:
            s.value = str(val)
        else:
            s = UserSettings(key=key, value=str(val))
            session.add(s)
        session.commit()
        session.close()
    except Exception as e:
        print("Failed to set setting:", e)
