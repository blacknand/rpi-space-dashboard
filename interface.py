import sys
import signal
import random
import math
from PySide6.QtCore import Qt, QTimer, QRectF, QPointF
from PySide6.QtGui import QKeyEvent, QPainter, QPen, QColor, QFont, QPainterPath
from PySide6.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget, QMainWindow
from rocket_launches import RocketLaunchesData
# from bme280 import bme280_results                           # Comment during testing

# Config
launch_api_url = "https://lldev.thespacedevs.com/2.2.0/launch/upcoming/"
api_url_filters = "limit=10&include_suborbital=true&hide_recent_previous=true&ordering=net&mode=list&tbd=true"
api_url = f"{launch_api_url}?{api_url_filters}"
rocket_launch_obj = RocketLaunchesData(api_url)

# For testing purposes (BME data only available on R pi) - comment out during deployment
def bme280_results():
    temp = "28"
    pressure = "1250"
    humidity = "40"
    dew_point = "10"
    return [temp, pressure, humidity, dew_point]

class TempWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.value = 0
        self.max_value = 50         # Most is 50 °C
        self.min_value = -10        # Least is -10 °C
        self.unit = "°C"
        self.label = "CABIN TEMP"
        self.start_color = QColor(0, 0, 255)        # Blue
        self.end_color = QColor(255, 0, 0)          # Red
        self.font = QFont("Arial", 15)
        self.setFixedSize(300, 300) 


    def setValue(self, value):
        self.value = value
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Calculate the dimensions
        rect = QRectF(0, 0, self.width(), self.height())
        center = rect.center()
        radius = min(self.width(), self.height()) / 2 - 20  # Adjust for padding

        # Draw debug border
        painter.setPen(QPen(Qt.red, 1, Qt.SolidLine))
        painter.drawRect(rect)

        # Calculate the percentage
        percentage = (self.value - self.min_value) / (self.max_value - self.min_value)
        pd = percentage * 360
        rd = 360 - pd

        # Draw progress arc
        path, path2 = QPainterPath(), QPainterPath()
        circle_rect = QRectF(center.x() - radius, center.y() - radius, 2 * radius, 2 * radius)
        path.arcMoveTo(circle_rect, 90)  # Move to the starting point of the arc
        path.arcTo(circle_rect, 90, -pd)
        pen, pen2 = QPen(), QPen()
        pen.setCapStyle(Qt.FlatCap)
        pen.setColor(self.get_gradient_color())
        pen_width = self.width() / 25
        pen.setWidth(pen_width)
        painter.strokePath(path, pen)

        path2.arcMoveTo(circle_rect, 90)  # Move to the starting point of the remaining arc
        path2.arcTo(circle_rect, 90, rd)
        pen2.setWidth(pen_width)
        pen2.setColor(QColor("#d7d7d7"))
        pen2.setCapStyle(Qt.FlatCap)
        pen2.setDashPattern([0.5, 1.105])
        pen2.setDashOffset(2.2)
        painter.strokePath(path2, pen2)

        # Draw description label at the top
        painter.setFont(QFont("Arial", 15))
        painter.setPen(Qt.white)
        painter.drawText(QRectF(center.x() - radius, center.y() - radius * 0.55, 2 * radius, radius / 2), Qt.AlignCenter, self.label)

        # Draw temperature label in the middle
        painter.setFont(QFont("Arial", 40, QFont.Bold))
        painter.setPen(Qt.white)
        painter.drawText(QRectF(center.x() - radius, center.y() - radius / 4, 2 * radius, radius / 2), Qt.AlignCenter, f"{self.value:.2f}")

        # Draw unit label at the bottom
        painter.setFont(QFont("Arial", 30))
        painter.setPen(Qt.white)
        painter.drawText(QRectF(center.x() - radius, center.y() + radius / 5, 2 * radius, radius / 2), Qt.AlignCenter, self.unit)



    def get_gradient_color(self):
        # Determine color based on temperature value
        if self.value < 8:
            return QColor(255, 0, 0)  # Red
        elif 8 <= self.value <= 15:
            return QColor(0, 255, 0)  # Green
        elif 16 <= self.value <= 30:
            return QColor(0, 0, 255)  # Blue
        elif 31 <= self.value <= 50:
            return QColor(255, 69, 0)  # Bright Red
        else:
            return QColor(255, 255, 255)  # White for undefined ranges



class MainWidget(QWidget):
    def __init__(self):
        super().__init__()     
 

        self.temp_display = TempWidget()
        # self.temp = QLabel(f"{bme280_results()[0]}")            # °C
        # self.humidity = QLabel(f"{bme280_results()[1]}")        # %
        # self.pressure = QLabel(f"{bme280_results()[2]}")        # %
        # self.dew_point = QLabel(f"{bme280_results()[3]}")       # °C
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.temp_display)
        # self.layout.addWidget(self.temp)
        # self.layout.addWidget(self.pressure)
        # self.layout.addWidget(self.humidity)
        # self.layout.addWidget(self.dew_point)

        # Update every second
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_labels)
        self.timer.start(1000)


    def update_labels(self):
        temp, humidity, pressure, dew_point = bme280_results()
        self.temp_display.setValue(float(temp))

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()


# TODO: List of launches
class LaunchWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.text = QLabel("ROCKET LAUNCHES", alignment=Qt.AlignCenter)


# TODO: Randomly selected SpaceX image
class SpaceXWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.text = QLabel("SPACEX IMAGES", alignment=Qt.AlignCenter)


# TODO: APOD image
class ApodWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.text = QLabel("APOD", alignment=Qt.AlignCenter)


# TODO: Mars data
class MarsWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.text = QLabel("MARS DATA", alignment=Qt.AlignCenter)


# TODO: Space related news
class NewsWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.text = QLabel("SPACE NEWS", alignment=Qt.AlignCenter)


if __name__ == "__main__":
    app = QApplication([])
    signal.signal(signal.SIGINT, QApplication.quit)     # Signal handler for ESC
    widget = MainWidget()
    widget.showFullScreen()
    sys.exit(app.exec())
