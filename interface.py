import sys
import signal
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPainter, QCursor, QColor
from PySide6.QtWidgets import QApplication, QLabel, QWidget, QHBoxLayout, QGridLayout, QPushButton
from rocket_launches import RocketLaunchesData
from bme280 import TempWidget, HumidityWidget, PressureWidget, DewPointWidget, bme280_results
from custom_widgets import DragonImageWidget, HeaderWidget, FooterButtonsWidget

# Config
launch_api_url = "https://lldev.thespacedevs.com/2.2.0/launch/upcoming/"
api_url_filters = "limit=10&include_suborbital=true&hide_recent_previous=true&ordering=net&mode=list&tbd=true"
api_url = f"{launch_api_url}?{api_url_filters}"
rocket_launch_obj = RocketLaunchesData(api_url)


class MainWidget(QWidget):
    def __init__(self):
        super().__init__()     

        layout = QGridLayout()
 
        self.header_widget = HeaderWidget()
        self.temp_display = TempWidget()
        self.humidity_display = HumidityWidget()
        self.pressure_display = PressureWidget()
        self.dew_point_display = DewPointWidget()
        self.dragon_image_widget = DragonImageWidget(600, 400)
        buttons_widget = FooterButtonsWidget()
        self.eject_button = QPushButton("EJECT")

        self.eject_button.setStyleSheet("background-color: transparent; border: 2px solid white; color: white; padding: 5px; border-radius: 7.5px;")
        self.setStyleSheet("""
            background-color: #050A30;
            QLabel {
                font-size: 18px;
                color: white;
            }
            QLabel#dragon_image {
                border: none;
            }
            QPushButton {
                background-color: transparent;
                border: none;
                color: white;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #444;
            }
        """)

        # Add widgets to the grid layout with appropriate spanning and alignment
        layout.addWidget(self.header_widget, 0, 0, 1, 2)               # Header spans across both columns in row 0
        layout.addWidget(self.humidity_display, 1, 0)                  # Humidity display in row 1, column 0
        layout.addWidget(self.temp_display, 1, 1)                      # Temperature display in row 1, column 1
        layout.addWidget(self.pressure_display, 2, 0)                  # Pressure display in row 2, column 0
        layout.addWidget(self.dew_point_display, 2, 1)                 # Dew point display in row 2, column 1
        layout.addWidget(self.dragon_image_widget, 1, 2, 2, 1, Qt.AlignCenter)  # Dragon image spans rows 1 and 2, and column 2
        layout.addWidget(buttons_widget, 3, 0, 1, 3, Qt.AlignCenter)   # Buttons widget spans across all columns in row 3
        layout.addWidget(self.eject_button, 3, 0)

        # Add stretch to push the buttons widget to the bottom
        layout.setRowStretch(2, 1)
        layout.setRowStretch(3, 0)

        self.setCursor(Qt.BlankCursor)
        self.eject_button.clicked.connect(self.eject_dashboard)

        # Update every second
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_labels)
        self.timer.start(1000)

        self.setLayout(layout)

    def update_labels(self):
        # BME data
        temp, humidity, pressure, dew_point = bme280_results()
        self.temp_display.setValue(float(temp))
        self.pressure_display.setValue(float(pressure))
        self.humidity_display.setValue(float(humidity))
        self.dew_point_display.setValue(float(dew_point))

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()

    def eject_dashboard(self, event):
        print("Safely ejected out of capsule.")
        QApplication.quit()


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


if __name__ == "__main__":
    app = QApplication([])
    signal.signal(signal.SIGINT, QApplication.quit)     # Signal handler for ESC
    widget = MainWidget()
    widget.showFullScreen()
    sys.exit(app.exec())
