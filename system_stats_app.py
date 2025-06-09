import sys
import time
import socket
import psutil
import platform
import subprocess
from datetime import datetime
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QTextEdit, QFileDialog
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QFont

class SystemStatsApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.prev_net = psutil.net_io_counters()
        self.prev_disk_io = psutil.disk_io_counters()
        self.update_stats()

    def initUI(self):
        self.setWindowTitle("System Stats App")
        self.setGeometry(100, 100, 700, 760)

        layout = QVBoxLayout()
        self.text_area = QTextEdit(self)
        self.text_area.setReadOnly(True)
        self.text_area.setFont(QFont("Courier", 10))

        self.export_button = QPushButton("Export to TXT", self)
        self.export_button.clicked.connect(self.export_to_txt)

        layout.addWidget(self.text_area)
        layout.addWidget(self.export_button)
        self.setLayout(layout)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_stats)
        self.timer.start(1000)

    '''
    def get_packet_loss(self):
        try:
            if platform.system() == "Windows":
                command = ["ping", "-n", "5", "8.8.8.8"]
            else:
                command = ["ping", "-c", "5", "8.8.8.8"]

            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            output = result.stdout.lower()

            if "lost =" in output or "received" in output:
                if platform.system() == "Windows":
                    # Extract "Lost = x (y% loss)"
                    percent = output.split("lost =")[1].split("(")[1].split("%")[0].strip()
                else:
                    # Extract from "x% packet loss"
                    percent = output.split("packet loss")[0].split()[-1].replace("%", "")
                return f"Packet Loss: {percent}%"
            else:
                return "Packet Loss: Unable to determine"
        except Exception:
            return "Packet Loss: Error running ping"
    '''

    def update_stats(self):
        stats = []

        # Timezone and current time
        tz = time.tzname[time.daylight]
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        stats.append(f"Timezone: {tz}")
        stats.append(f"Current Time: {current_time}")

        # System info
        stats.append(f"System: {platform.system()} {platform.release()} ({platform.machine()})")
        #stats.append(f"Hostname: {socket.gethostname()}")
        stats.append(f"System Model: {platform.node()}")

        # Boot time
        boot_time = datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S")
        stats.append(f"Boot Time: {boot_time}")

        # CPU usage
        stats.append("CPU Usage per Core:")
        for i, perc in enumerate(psutil.cpu_percent(percpu=True)):
            stats.append(f"  Core {i + 1}: {perc}%")
        stats.append(f"Total CPU Usage: {psutil.cpu_percent()}%")

        # CPU frequency
        freq = psutil.cpu_freq()
        if freq:
            stats.append(f"CPU Frequency: {freq.current:.2f} MHz")

        # CPU temperature
        try:
            temps = psutil.sensors_temperatures()
            if temps:
                for name, entries in temps.items():
                    for entry in entries:
                        stats.append(f"{entry.label or name} Temp: {entry.current}°C")
        except Exception:
            stats.append("CPU Temp: Not available")

        # Memory
        virtual_mem = psutil.virtual_memory()
        stats.append(f"Memory Used: {virtual_mem.used / (1024 ** 3):.2f} GB / {virtual_mem.total / (1024 ** 3):.2f} GB")

        # Swap
        swap = psutil.swap_memory()
        stats.append(f"Swap Used: {swap.used / (1024 ** 3):.2f} GB / {swap.total / (1024 ** 3):.2f} GB")

        # Disk partitions
        stats.append("Disk Partitions:")
        for part in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(part.mountpoint)
                stats.append(f"  {part.device} ({part.mountpoint}) - Used: {usage.used / (1024 ** 3):.2f} GB / {usage.total / (1024 ** 3):.2f} GB")
            except PermissionError:
                continue

        # Disk I/O
        disk_io = psutil.disk_io_counters()
        read_speed = (disk_io.read_bytes - self.prev_disk_io.read_bytes) / 1024
        write_speed = (disk_io.write_bytes - self.prev_disk_io.write_bytes) / 1024
        stats.append(f"Disk Read Speed: {read_speed:.2f} KB/s")
        stats.append(f"Disk Write Speed: {write_speed:.2f} KB/s")
        self.prev_disk_io = disk_io

        # Network
        net = psutil.net_io_counters()
        sent = (net.bytes_sent - self.prev_net.bytes_sent) / 1024
        recv = (net.bytes_recv - self.prev_net.bytes_recv) / 1024
        stats.append(f"Total Bytes Sent: {net.bytes_sent / (1024 ** 2):.2f} MB")
        stats.append(f"Total Bytes Received: {net.bytes_recv / (1024 ** 2):.2f} MB")
        stats.append(f"Upload Speed: {sent:.2f} KB/s")
        stats.append(f"Download Speed: {recv:.2f} KB/s")
        self.prev_net = net

        # Packet Loss
        # stats.append(self.get_packet_loss())

        # Battery
        battery = psutil.sensors_battery()
        if battery:
            if battery.secsleft != psutil.POWER_TIME_UNLIMITED:
                mins_left = battery.secsleft // 60
                stats.append(f"Battery Time Left: {mins_left} min")
            else:
                stats.append("Battery: Charging / Unlimited")
        else:
            stats.append("Battery: Not available")

        # Screen resolution
        try:
            from PyQt5.QtWidgets import QDesktopWidget
            screen = QDesktopWidget().screenGeometry()
            stats.append(f"Screen Resolution: {screen.width()}x{screen.height()}")
        except Exception:
            stats.append("Screen Resolution: Not available")

        # Fan speed
        try:
            fans = psutil.sensors_fans()
            if fans:
                for name, entries in fans.items():
                    for fan in entries:
                        stats.append(f"{fan.label or name} Fan Speed: {fan.current} RPM")
        except Exception:
            stats.append("Fan Speed: Not available")

        self.text_area.setPlainText("\n".join(stats))

    def export_to_txt(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Save Stats", "", "Text Files (*.txt)")
        if filename:
            with open(filename, "w") as f:
                f.write(self.text_area.toPlainText())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SystemStatsApp()
    window.show()
    sys.exit(app.exec_())
