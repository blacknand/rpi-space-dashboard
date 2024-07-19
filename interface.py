import sys
import random
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget
from rocket_launches import RocketLaunchesData
from bme280 import bme280_results                           # Comment during testing

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
 
        self.temp = QLabel(f"{bme280_results()[0]}°C")
        self.pressure = QLabel(f"{bme280_results()[1]} hPa")
        self.humidity = QLabel(f"{bme280_results()[2]} %")
        self.dew_point = QLabel(f"{bme280_results()[3]} °C")
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.temp)
        self.layout.addWidget(self.pressure)
        self.layout.addWidget(self.humidity)
        self.layout.addWidget(self.dew_point)

        # Update every second
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_temp)
        self.timer.timeout.connect(self.update_pressure)
        self.timer.timeout.connect(self.update_humidity)
        self.timer.timeout.connect(self.update_dew_point)
        self.timer.start(1000)


    def update_temp(self):
        self.temp.setText(f"{bme280_results()[0]} °C")

    def update_pressure(self):
        self.pressure.setText(f"{bme280_results()[1]} hPa")

    def update_humidity(self):
        self.humidity.setText(f"{bme280_results()[2]} %")

    def update_dew_point(self):
        self.dew_point.setText(f"{bme280_results()[3]} °C")


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
    widget = MainWidget()
    widget.showFullScreen()
    sys.exit(app.exec())
