from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGridLayout
from qfluentwidgets import (SubtitleLabel, BodyLabel, TitleLabel, 
                            ProgressRing, CardWidget, setFont, FluentIcon as FIF)
import psutil
import platform
import os

class StatCard(CardWidget):
    def __init__(self, title, icon=FIF.INFO, parent=None):
        super().__init__(parent=parent)
        self.setFixedSize(250, 250)
        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.titleLabel = SubtitleLabel(title)
        self.titleLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.vBoxLayout.addWidget(self.titleLabel)
        
        self.vBoxLayout.addSpacing(15)
        
        self.progressRing = ProgressRing()
        self.progressRing.setFixedSize(120, 120)
        self.progressRing.setTextVisible(True)
        self.progressRing.setStrokeWidth(8)
        self.vBoxLayout.addWidget(self.progressRing, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.vBoxLayout.addSpacing(15)
        
        self.descLabel = BodyLabel("-")
        self.descLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.descLabel.setStyleSheet("color: gray;")
        self.vBoxLayout.addWidget(self.descLabel)

    def update_data(self, percent, desc_text):
        self.progressRing.setValue(int(percent))
        self.descLabel.setText(desc_text)


class SystemView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("SystemView")
        self.setStyleSheet("#SystemView { background-color: transparent; }")
        
        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.vBoxLayout.setContentsMargins(40, 40, 40, 40)
        
        # Header
        self.titleLabel = TitleLabel("System Dashboard")
        self.vBoxLayout.addWidget(self.titleLabel)
        
        self.subtitleLabel = BodyLabel("Real-time metrics and system health")
        self.subtitleLabel.setStyleSheet("color: gray; font-size: 14px;")
        self.vBoxLayout.addWidget(self.subtitleLabel)
        
        self.vBoxLayout.addSpacing(40)
        
        # Stats Layout
        self.statsLayout = QHBoxLayout()
        self.statsLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.statsLayout.setSpacing(30)
        
        self.cpuCard = StatCard("CPU Usage")
        self.memCard = StatCard("Memory")
        self.diskCard = StatCard("Storage")
        
        self.statsLayout.addWidget(self.cpuCard)
        self.statsLayout.addWidget(self.memCard)
        self.statsLayout.addWidget(self.diskCard)
        self.statsLayout.addStretch(1)
        
        self.vBoxLayout.addLayout(self.statsLayout)
        
        self.vBoxLayout.addSpacing(40)
        
        # System Info Card
        self.infoCard = CardWidget()
        infoLayout = QVBoxLayout(self.infoCard)
        infoLayout.setContentsMargins(20, 20, 20, 20)
        
        infoTitle = SubtitleLabel("System Information")
        infoLayout.addWidget(infoTitle)
        infoLayout.addSpacing(10)
        
        sys_info = f"OS: {platform.system()} {platform.release()} ({platform.architecture()[0]})\n" \
                   f"Processor: {platform.processor()}\n" \
                   f"Computer Name: {platform.node()}"
        self.infoLabel = BodyLabel(sys_info)
        infoLayout.addWidget(self.infoLabel)
        
        self.vBoxLayout.addWidget(self.infoCard)
        
        self.vBoxLayout.addStretch(1)
        
        # Timer for updates
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_stats)
        self.timer.start(2000)
        
        # Initialize with CPU zeroed properly
        psutil.cpu_percent(interval=None) 
        self.update_stats()

    def update_stats(self):
        try:
            # CPU
            cpu_percent = psutil.cpu_percent(interval=None)
            cpu_freq = psutil.cpu_freq()
            freq_text = f"{cpu_freq.current:.0f} MHz" if cpu_freq else ""
            self.cpuCard.update_data(cpu_percent, f"Current Load: {cpu_percent}%\n{freq_text}")
            
            # RAM
            mem = psutil.virtual_memory()
            mem_used_gb = mem.used / (1024 ** 3)
            mem_total_gb = mem.total / (1024 ** 3)
            self.memCard.update_data(mem.percent, f"{mem_used_gb:.1f} GB / {mem_total_gb:.1f} GB")
            
            # DISK
            total_disk = 0
            used_disk = 0
            for part in psutil.disk_partitions(all=False):
                if os.name == 'nt' and ('cdrom' in part.opts or part.fstype == ''):
                    continue
                try:
                    usage = psutil.disk_usage(part.mountpoint)
                    total_disk += usage.total
                    used_disk += usage.used
                except:
                    pass
            
            disk_percent = (used_disk / total_disk * 100) if total_disk > 0 else 0
            disk_used_gb = used_disk / (1024 ** 3)
            disk_total_gb = total_disk / (1024 ** 3)
            self.diskCard.update_data(disk_percent, f"{disk_used_gb:.0f} GB / {disk_total_gb:.0f} GB")
            
        except Exception as e:
            print("Error updating system stats:", e)
