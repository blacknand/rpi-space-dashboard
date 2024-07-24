import sys
import signal
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout, QGridLayout, QPushButton, QHBoxLayout, QSizePolicy
from rocket_launches import RocketLaunchesData
from bme280 import TempWidget, HumidityWidget, PressureWidget, DewPointWidget, bme280_results
from custom_widgets import DragonImageWidget, HeaderWidget, FooterButtonsWidget

# Config
launch_api_url = "https://lldev.thespacedevs.com/2.2.0/launch/upcoming/"
api_url_filters = "limit=10&include_suborbital=true&hide_recent_previous=true&ordering=net&mode=list&tbd=true"
api_url = f"{launch_api_url}?{api_url_filters}"
rocket_launch_obj = RocketLaunchesData(api_url)

class CenterGridWidget(QWidget):
    def __init__(self):
        super().__init__()  

        layout = QGridLayout()
        self.setLayout(layout)

        self.temp_display = TempWidget()
        self.humidity_display = HumidityWidget()
        self.pressure_display = PressureWidget()
        self.dew_point_display = DewPointWidget()
        dragon_image_widget = DragonImageWidget(width=300, height=600)

        # Display Dragon and BME data in grid
        layout.addWidget(self.humidity_display, 0, 0)
        layout.addWidget(self.temp_display, 0, 2)
        layout.addWidget(dragon_image_widget, 0, 1, 2, 1)
        layout.addWidget(self.pressure_display, 1, 0)
        layout.addWidget(self.dew_point_display, 1, 2)

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


class BottomWidget(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        self.setLayout(layout)

        layout_h = QHBoxLayout()
        layout.addLayout(layout_h)  

        self.eject_button = QPushButton("EJECT", self)
        self.eject_button.setStyleSheet(
            "background-color: white; border: 2px solid white; padding: 10px; border-radius: 7.5px; width: 100px;"
        )
        self.eject_button.setMaximumWidth(100) 
        self.eject_button.setFixedSize(100, 40)
        self.eject_button.clicked.connect(self.eject_dashboard)

        self.eject_button.move(20, 15)

        buttons_widget = FooterButtonsWidget()
        layout_h.addWidget(buttons_widget)  

        # Ensure the BottomWidget expands horizontally
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setFixedHeight(80)  

    def eject_dashboard(self):
        print("Safely ejected out of capsule.")
        QApplication.quit()


class MainWidget(QWidget):
    def __init__(self):
        super().__init__()     

        layout = QVBoxLayout()
 
        self.header_widget = HeaderWidget()
        self.center_grid_widget = CenterGridWidget()
        self.bottom_widget = BottomWidget()

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

        self.header_widget.setParent(self)
        self.center_grid_widget.setParent(self)
        self.bottom_widget.setParent(self)

        self.setCursor(Qt.BlankCursor)
        self.updateWidgetPositions()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.updateWidgetPositions()

    def updateWidgetPositions(self):
        self.header_widget.move(0, 0)
        self.center_grid_widget.move(50, 50)
        # Adjust BottomWidget's width to span the full width of the parent
        self.bottom_widget.setFixedWidth(self.width())
        self.bottom_widget.move(0, self.height() - self.bottom_widget.height() + 10)

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
