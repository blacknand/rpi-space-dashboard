import sys
import random
from PySide6 import QtCore, QtWidgets, QtGui
from rocket_launches import RocketLaunchesData

# from bme280 import bme280_results                           # Comment during testing

# Config
launch_api_url = "https://lldev.thespacedevs.com/2.2.0/launch/upcoming/"
api_url_filters = "limit=10&include_suborbital=true&hide_recent_previous=true&ordering=net&mode=list&tbd=true"
api_url = f"{launch_api_url}?{api_url_filters}"
rocket_launch_obj = RocketLaunchesData(api_url)

# For testing purposes (BME data only available on R pi) - comment out during deployment
def bme280_results():
    temp = "28°C"
    pressure = "1250 hPa"
    humidity = "40 %"
    dew_point = "10°C"
    return [temp, pressure, humidity, dew_point]


class MainWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()     
 
        self.text = QtWidgets.QLabel("TEMP data", alignment=QtCore.Qt.AlignCenter)
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.text)


# TODO: List of launches
class LaunchWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.text = QtWidgets.QLabel("ROCKET LAUNCHES", alignment=QtCore.Qt.AlignCenter)


# TODO: Randomly selected SpaceX image
class SpaceXWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.text = QtWidgets.QLabel("SPACEX IMAGES", alignment=QtCore.Qt.AlignCenter)


# TODO: APOD image
class ApodWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.text = QtWidgets.QLabel("APOD", alignment=QtCore.Qt.AlignCenter)


# TODO: Mars data
class MarsWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.text = QtWidgets.QLabel("MARS DATA", alignment=QtCore.Qt.AlignCenter)


# TODO: Space related news
class NewsWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.text = QtWidgets.QLabel("SPACE NEWS", alignment=QtCore.Qt.AlignCenter)


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    widget = MainWidget()
    widget.showFullScreen()
    sys.exit(app.exec())
