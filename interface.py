import sys
import signal
import random
import math
from PySide6.QtCore import Qt, QTimer, QRectF, QPointF
from PySide6.QtGui import QKeyEvent, QPainter, QPen, QColor, QFont, QPainterPath
from PySide6.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget, QMainWindow, QGridLayout, QHBoxLayout
from rocket_launches import RocketLaunchesData
# from bme280 import bme280_results                           # Comment during testing
from bme280 import TempWidget, HumidityWidget, PressureWidget, DewPointWidget, bme280_results

# Config
launch_api_url = "https://lldev.thespacedevs.com/2.2.0/launch/upcoming/"
api_url_filters = "limit=10&include_suborbital=true&hide_recent_previous=true&ordering=net&mode=list&tbd=true"
api_url = f"{launch_api_url}?{api_url_filters}"
rocket_launch_obj = RocketLaunchesData(api_url)

# For testing purposes (BME data only available on R pi) - comment out during deployment
# def bme280_results():
#     temp = "28"
#     pressure = "1250"
#     humidity = "40"
#     dew_point = "10"
#     return [temp, pressure, humidity, dew_point]


class MainWidget(QWidget):
    def __init__(self):
        super().__init__()     
 
        self.temp_display = TempWidget()
        self.humidity_display = HumidityWidget()
        self.pressure_display = PressureWidget()
        self.dew_point_display = DewPointWidget()

        self.layout = QHBoxLayout(self)
        self.layout.addWidget(self.temp_display)
        self.layout.addWidget(self.humidity_display)
        self.layout.addWidget(self.pressure_display)
        self.layout.addWidget(self.dew_point_display)

        # Update every second
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_labels)
        self.timer.start(1000)


    def update_labels(self):
        temp, pressure, humidity, dew_point = bme280_results()
        self.temp_display.setValue(float(temp))
        self.pressure_display.setValue(float(pressure))
        self.humidity_display.setValue(float(humidity))
        self.dew_point_display.setValue(float(dew_point))

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
