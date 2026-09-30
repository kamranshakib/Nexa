from PyQt6.QtCore import Qt, QTimer, QPoint
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QApplication, QStackedWidget
from qfluentwidgets import (SubtitleLabel, BodyLabel, TitleLabel, 
                            PrimaryPushButton, PushButton, setFont, CardWidget, SpinBox, 
                            InfoBar, InfoBarPosition, SegmentedWidget, LineEdit)
from nexa.infra.database import log_activity
import winsound

class MiniTimerWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(120, 50)
        
        self.card = CardWidget(self)
        self.card.setFixedSize(120, 50)
        layout = QVBoxLayout(self.card)
        layout.setContentsMargins(5, 5, 5, 5)
        
        self.timeLabel = SubtitleLabel("00:00")
        self.timeLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.timeLabel)
        
        self.offset = None

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.offset = event.pos()

    def mouseMoveEvent(self, event):
        if self.offset is not None and event.buttons() == Qt.MouseButton.LeftButton:
            self.move(self.pos() + event.pos() - self.offset)

    def mouseReleaseEvent(self, event):
        self.offset = None


class PomodoroWidget(QWidget):
    def __init__(self, mini_timer, parent=None):
        super().__init__(parent=parent)
        self.mini_timer = mini_timer
        
        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Time Selector
        self.timeSelectLayout = QHBoxLayout()
        self.timeSelectLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.hourSpinBox = SpinBox()
        self.hourSpinBox.setRange(0, 24)
        self.hourSpinBox.setValue(0)
        self.hourSpinBox.setFixedWidth(80)
        self.hourSpinBox.valueChanged.connect(self.on_time_changed)
        
        self.minuteSpinBox = SpinBox()
        self.minuteSpinBox.setRange(0, 59)
        self.minuteSpinBox.setValue(25)
        self.minuteSpinBox.setFixedWidth(80)
        self.minuteSpinBox.valueChanged.connect(self.on_time_changed)
        
        self.timeSelectLayout.addWidget(BodyLabel("Hours:"))
        self.timeSelectLayout.addWidget(self.hourSpinBox)
        self.timeSelectLayout.addSpacing(15)
        self.timeSelectLayout.addWidget(BodyLabel("Minutes:"))
        self.timeSelectLayout.addWidget(self.minuteSpinBox)
        
        self.vBoxLayout.addLayout(self.timeSelectLayout)
        self.vBoxLayout.addSpacing(20)
        
        # Timer Display
        self.timerCard = CardWidget()
        self.timerCard.setFixedSize(300, 200)
        cardLayout = QVBoxLayout(self.timerCard)
        cardLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.timeLabel = TitleLabel("25:00")
        setFont(self.timeLabel, 64)
        self.timeLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cardLayout.addWidget(self.timeLabel)
        
        self.vBoxLayout.addWidget(self.timerCard, alignment=Qt.AlignmentFlag.AlignCenter)
        self.vBoxLayout.addSpacing(30)
        
        # Controls
        self.controlsLayout = QHBoxLayout()
        self.controlsLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.btnStart = PrimaryPushButton("Start Focus")
        self.btnStart.setFixedWidth(120)
        self.btnStart.clicked.connect(self.toggle_timer)
        
        self.btnReset = PushButton("Reset")
        self.btnReset.setFixedWidth(120)
        self.btnReset.clicked.connect(self.reset_timer)
        
        self.controlsLayout.addWidget(self.btnStart)
        self.controlsLayout.addSpacing(20)
        self.controlsLayout.addWidget(self.btnReset)
        
        self.vBoxLayout.addLayout(self.controlsLayout)
        
        # Timer Logic
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)
        
        self.default_time = (self.hourSpinBox.value() * 3600) + (self.minuteSpinBox.value() * 60)
        self.remaining_time = self.default_time
        self.is_running = False

    def on_time_changed(self, val):
        if not self.is_running:
            self.default_time = (self.hourSpinBox.value() * 3600) + (self.minuteSpinBox.value() * 60)
            self.remaining_time = self.default_time
            self.update_display()

    def toggle_timer(self):
        if self.is_running:
            self.timer.stop()
            self.btnStart.setText("Resume")
            self.is_running = False
            self.hourSpinBox.setEnabled(True)
            self.minuteSpinBox.setEnabled(True)
        else:
            if self.remaining_time <= 0:
                self.default_time = (self.hourSpinBox.value() * 3600) + (self.minuteSpinBox.value() * 60)
                self.remaining_time = self.default_time
                
            if self.default_time == 0:
                return 
            
            self.timer.start(1000)
            self.btnStart.setText("Pause")
            self.is_running = True
            self.hourSpinBox.setEnabled(False)
            self.minuteSpinBox.setEnabled(False)
            
            if not self.mini_timer.isVisible():
                self.mini_timer.show()
                desktop = QApplication.primaryScreen().availableGeometry()
                self.mini_timer.move(desktop.width() - 150, 50)

    def reset_timer(self):
        self.timer.stop()
        self.is_running = False
        self.hourSpinBox.setEnabled(True)
        self.minuteSpinBox.setEnabled(True)
        self.default_time = (self.hourSpinBox.value() * 3600) + (self.minuteSpinBox.value() * 60)
        self.remaining_time = self.default_time
        self.btnStart.setText("Start Focus")
        self.update_display()
        self.mini_timer.hide()

    def update_timer(self):
        if self.remaining_time > 0:
            self.remaining_time -= 1
            self.update_display()
        else:
            self.timer.stop()
            self.is_running = False
            self.hourSpinBox.setEnabled(True)
            self.minuteSpinBox.setEnabled(True)
            self.btnStart.setText("Start Focus")
            self.mini_timer.hide()
            
            try:
                winsound.MessageBeep(winsound.MB_ICONASTERISK)
            except:
                pass
                
            total_minutes = self.default_time // 60
            InfoBar.success(
                title='Focus Finished!',
                content=f'Great job! You stayed focused for {total_minutes} minutes.',
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=5000,
                parent=self.window()
            )
            
            log_activity('focus', 'Focus Session Completed', f"You stayed focused for {total_minutes} minutes!", str(self.default_time))
            
            self.remaining_time = self.default_time
            self.update_display()

    def update_display(self):
        h = self.remaining_time // 3600
        m = (self.remaining_time % 3600) // 60
        s = self.remaining_time % 60
        if h > 0:
            time_str = f"{h:02d}:{m:02d}:{s:02d}"
        else:
            time_str = f"{m:02d}:{s:02d}"
        self.timeLabel.setText(time_str)
        self.mini_timer.timeLabel.setText(time_str)


class StopwatchWidget(QWidget):
    def __init__(self, mini_timer, parent=None):
        super().__init__(parent=parent)
        self.mini_timer = mini_timer
        
        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Project Input
        self.inputLayout = QHBoxLayout()
        self.inputLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.projectInput = LineEdit()
        self.projectInput.setPlaceholderText("What are you working on? (e.g. Design UI)")
        self.projectInput.setFixedWidth(300)
        self.inputLayout.addWidget(self.projectInput)
        self.vBoxLayout.addLayout(self.inputLayout)
        
        self.vBoxLayout.addSpacing(20)
        
        # Timer Display
        self.timerCard = CardWidget()
        self.timerCard.setFixedSize(300, 200)
        cardLayout = QVBoxLayout(self.timerCard)
        cardLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.timeLabel = TitleLabel("00:00:00")
        setFont(self.timeLabel, 64)
        self.timeLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cardLayout.addWidget(self.timeLabel)
        
        self.vBoxLayout.addWidget(self.timerCard, alignment=Qt.AlignmentFlag.AlignCenter)
        self.vBoxLayout.addSpacing(30)
        
        # Controls
        self.controlsLayout = QHBoxLayout()
        self.controlsLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.btnStart = PrimaryPushButton("Start Tracking")
        self.btnStart.setFixedWidth(120)
        self.btnStart.clicked.connect(self.toggle_timer)
        
        self.btnReset = PushButton("Stop & Log")
        self.btnReset.setFixedWidth(120)
        self.btnReset.clicked.connect(self.stop_timer)
        
        self.controlsLayout.addWidget(self.btnStart)
        self.controlsLayout.addSpacing(20)
        self.controlsLayout.addWidget(self.btnReset)
        self.vBoxLayout.addLayout(self.controlsLayout)
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)
        self.elapsed_time = 0
        self.is_running = False

    def toggle_timer(self):
        if self.is_running:
            self.timer.stop()
            self.btnStart.setText("Resume")
            self.is_running = False
        else:
            self.timer.start(1000)
            self.btnStart.setText("Pause")
            self.is_running = True
            
            if not self.mini_timer.isVisible():
                self.mini_timer.show()
                desktop = QApplication.primaryScreen().availableGeometry()
                self.mini_timer.move(desktop.width() - 150, 50)

    def stop_timer(self):
        self.timer.stop()
        self.is_running = False
        
        project = self.projectInput.text().strip() or "Untitled Task"
        
        if self.elapsed_time > 0:
            h = self.elapsed_time // 3600
            m = (self.elapsed_time % 3600) // 60
            s = self.elapsed_time % 60
            duration_str = f"{h:02d}:{m:02d}:{s:02d}"
            
            log_activity('focus', f'Tracked: {project}', f"Spent {duration_str} on this task", str(self.elapsed_time))
            
            InfoBar.success(
                title='Time Tracked!',
                content=f'Logged {duration_str} for {project}',
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=5000,
                parent=self.window()
            )
            
        self.elapsed_time = 0
        self.btnStart.setText("Start Tracking")
        self.projectInput.clear()
        self.update_display()
        self.mini_timer.hide()

    def update_timer(self):
        self.elapsed_time += 1
        self.update_display()

    def update_display(self):
        h = self.elapsed_time // 3600
        m = (self.elapsed_time % 3600) // 60
        s = self.elapsed_time % 60
        time_str = f"{h:02d}:{m:02d}:{s:02d}"
        self.timeLabel.setText(time_str)
        self.mini_timer.timeLabel.setText(time_str)


class FocusView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("FocusView")
        self.setStyleSheet("#FocusView { background-color: transparent; }")
        
        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.vBoxLayout.setContentsMargins(40, 40, 40, 40)
        
        # Header
        self.titleLabel = TitleLabel("Focus & Time Tracker")
        self.titleLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.vBoxLayout.addWidget(self.titleLabel)
        
        self.subtitleLabel = BodyLabel("Stay productive or track exactly where your time goes")
        self.subtitleLabel.setStyleSheet("color: gray;")
        self.subtitleLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.vBoxLayout.addWidget(self.subtitleLabel)
        self.vBoxLayout.addSpacing(20)
        
        self.mini_timer = MiniTimerWindow()
        
        # Tabs / Segmented
        self.pivot = SegmentedWidget(self)
        self.pivot.addItem('pomodoro', 'Pomodoro Timer')
        self.pivot.addItem('stopwatch', 'Time Tracker')
        
        self.vBoxLayout.addWidget(self.pivot, alignment=Qt.AlignmentFlag.AlignCenter)
        self.vBoxLayout.addSpacing(20)
        
        # Stacked widgets
        self.stackedWidget = QStackedWidget(self)
        self.pomodoro = PomodoroWidget(self.mini_timer)
        self.stopwatch = StopwatchWidget(self.mini_timer)
        
        self.stackedWidget.addWidget(self.pomodoro)
        self.stackedWidget.addWidget(self.stopwatch)
        
        self.vBoxLayout.addWidget(self.stackedWidget)
        
        self.pivot.currentItemChanged.connect(self.on_tab_changed)
        self.pivot.setCurrentItem('pomodoro')

    def on_tab_changed(self, key):
        if key == 'pomodoro':
            self.stackedWidget.setCurrentWidget(self.pomodoro)
        else:
            self.stackedWidget.setCurrentWidget(self.stopwatch)
