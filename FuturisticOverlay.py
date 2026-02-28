# ================= FINAL STABLE WITH CLOSE BUTTON ================= #

import sys
import psutil
import datetime
import time
import csv
import wmi

from PyQt6.QtCore import Qt, QTimer, QPoint
from PyQt6.QtGui import QPainter, QColor, QFont, QPen, QAction
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout,
    QSystemTrayIcon, QMenu, QProgressBar,
    QSlider, QPushButton
)

# ================= SAFE NVML ================= #

NVML_AVAILABLE = False
GPU_HANDLE = None

try:
    from pynvml import (
        nvmlInit,
        nvmlDeviceGetHandleByIndex,
        nvmlDeviceGetUtilizationRates,
        nvmlDeviceGetTemperature,
        nvmlDeviceGetGraphicsRunningProcesses,
        nvmlDeviceGetMemoryInfo,
        NVML_TEMPERATURE_GPU,
        NVMLError,
    )
    nvmlInit()
    GPU_HANDLE = nvmlDeviceGetHandleByIndex(0)
    NVML_AVAILABLE = True
except Exception:
    NVML_AVAILABLE = False


# ================= SYSTEM MONITOR ================= #

class SystemMonitor:

    def __init__(self):
        self.fps_last = time.time()
        self.fps = 0
        self.wmi_conn = self._init_wmi()

    @staticmethod
    def _init_wmi():
        try:
            return wmi.WMI(namespace="root\\OpenHardwareMonitor")
        except Exception:
            return None

    @staticmethod
    def cpu_total():
        return int(psutil.cpu_percent())

    def cpu_temp(self):
        if not self.wmi_conn:
            return 0
        try:
            for sensor in self.wmi_conn.Sensor():
                if sensor.SensorType == "Temperature" and "CPU" in sensor.Name:
                    return int(sensor.Value)
        except Exception:
            return 0
        return 0

    @staticmethod
    def gpu_usage():
        if not NVML_AVAILABLE:
            return 0
        try:
            return nvmlDeviceGetUtilizationRates(GPU_HANDLE).gpu
        except Exception:
            return 0

    @staticmethod
    def gpu_temp():
        if not NVML_AVAILABLE:
            return 0
        try:
            return nvmlDeviceGetTemperature(GPU_HANDLE, NVML_TEMPERATURE_GPU)
        except Exception:
            return 0

    @staticmethod
    def active_game():
        if not NVML_AVAILABLE:
            return "N/A"
        try:
            processes = nvmlDeviceGetGraphicsRunningProcesses(GPU_HANDLE)
            if not processes:
                return "Idle"
            top = max(processes, key=lambda p: p.usedGpuMemory)
            return psutil.Process(top.pid).name()
        except Exception:
            return "Unknown"

    def update_fps(self):
        now = time.time()
        delta = now - self.fps_last
        self.fps_last = now
        if delta > 0:
            self.fps = int(1 / delta)
        return self.fps


# ================= GRAPH ================= #

class GraphWidget(QWidget):

    def __init__(self):
        super().__init__()
        self.data = []
        self.max_points = 60
        self.color = QColor(0, 255, 255)

    def update_value(self, value):
        self.data.append(value)
        if len(self.data) > self.max_points:
            self.data.pop(0)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(QPen(self.color, 2))

        if len(self.data) < 2:
            return

        width = self.width()
        height = self.height()
        step = width / len(self.data)

        for i in range(len(self.data) - 1):
            x1 = i * step
            y1 = height - (self.data[i] / 100) * height
            x2 = (i + 1) * step
            y2 = height - (self.data[i + 1] / 100) * height
            painter.drawLine(int(x1), int(y1), int(x2), int(y2))


# ================= MAIN UI ================= #

class FuturisticOverlay(QWidget):

    def __init__(self):
        super().__init__()

        self.monitor = SystemMonitor()

        self.setGeometry(300, 150, 520, 620)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.drag_pos = QPoint()
        self.opacity_level = 240
        self.hovered = False

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_stats)
        self.timer.start(1000)

        self._setup_ui()
        self._setup_tray()

    # ---------------- UI ---------------- #

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 50, 25, 25)

        # Close Button
        self.close_btn = QPushButton("✕", self)
        self.close_btn.setGeometry(480, 10, 30, 30)
        self.close_btn.setStyleSheet("color:white;background:transparent;border:none;font-size:16px;")
        self.close_btn.clicked.connect(QApplication.instance().quit)

        # Minimize Button
        self.min_btn = QPushButton("—", self)
        self.min_btn.setGeometry(450, 10, 30, 30)
        self.min_btn.setStyleSheet("color:white;background:transparent;border:none;font-size:16px;")
        self.min_btn.clicked.connect(self.showMinimized)

        self.clock = QLabel()
        self.clock.setFont(QFont("Segoe UI", 18))
        self.clock.setStyleSheet("color:white;")

        self.game = QLabel("GAME: Idle")
        self.game.setStyleSheet("color:white;")

        self.cpu_bar = self.create_bar("CPU")
        self.gpu_bar = self.create_bar("GPU")
        self.gpu_temp_bar = self.create_bar("GPU TEMP")
        self.fps_bar = self.create_bar("FPS")

        self.graph = GraphWidget()
        self.graph.setFixedHeight(120)

        self.opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.opacity_slider.setRange(150, 255)
        self.opacity_slider.setValue(240)
        self.opacity_slider.valueChanged.connect(self.change_opacity)

        layout.addWidget(self.clock)
        layout.addWidget(self.game)
        layout.addWidget(self.cpu_bar)
        layout.addWidget(self.gpu_bar)
        layout.addWidget(self.gpu_temp_bar)
        layout.addWidget(self.fps_bar)
        layout.addWidget(self.graph)
        layout.addWidget(self.opacity_slider)

    def create_bar(self, name):
        bar = QProgressBar()
        bar.setRange(0, 240)
        bar.setFormat(f"{name}  %v")
        bar.setStyleSheet("""
            QProgressBar {
                border-radius:6px;
                background-color: rgba(255,255,255,25);
                color:black;
            }
            QProgressBar::chunk {
                background-color:#00FFFF;
            }
        """)
        return bar

    # ---------------- UPDATE ---------------- #

    def update_stats(self):
        self.clock.setText(datetime.datetime.now().strftime("%H:%M:%S"))
        self.cpu_bar.setValue(self.monitor.cpu_total())
        self.gpu_bar.setValue(self.monitor.gpu_usage())
        self.gpu_temp_bar.setValue(self.monitor.gpu_temp())
        self.fps_bar.setValue(self.monitor.update_fps())
        self.graph.update_value(self.monitor.cpu_total())
        self.game.setText("GAME: " + self.monitor.active_game())

    # ---------------- TRAY ---------------- #

    def _setup_tray(self):
        self.tray = QSystemTrayIcon(self)
        menu = QMenu()

        export = QAction("Export Log", self)
        export.triggered.connect(self.export_log)

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(QApplication.instance().quit)

        menu.addAction(export)
        menu.addAction(exit_action)

        self.tray.setContextMenu(menu)
        self.tray.show()

    def export_log(self):
        filename = f"log_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        with open(filename, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Time", "CPU", "GPU", "GPU Temp", "FPS", "Game"])
            writer.writerow([
                datetime.datetime.now().strftime("%H:%M:%S"),
                self.cpu_bar.value(),
                self.gpu_bar.value(),
                self.gpu_temp_bar.value(),
                self.fps_bar.value(),
                self.monitor.active_game()
            ])

    # ---------------- BEHAVIOR ---------------- #

    def change_opacity(self, val):
        self.opacity_level = val
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_pos)

    def enterEvent(self, event):
        self.hovered = True
        self.update()

    def leaveEvent(self, event):
        self.hovered = False
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QColor(15, 20, 30, self.opacity_level))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(self.rect(), 20, 20)

        if self.hovered:
            glow_pen = QPen(QColor(0, 255, 255), 3)
            painter.setPen(glow_pen)
            painter.drawRoundedRect(self.rect().adjusted(2, 2, -2, -2), 20, 20)


# ================= MAIN ================= #

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FuturisticOverlay()
    window.show()
    sys.exit(app.exec())