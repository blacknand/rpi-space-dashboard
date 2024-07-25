import sys
import signal
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout, QGridLayout, QPushButton, QHBoxLayout, QSizePolicy, QDialog, QStackedWidget
from rocket_launches import RocketLaunchesData
from bme280 import TempWidget, HumidityWidget, PressureWidget, DewPointWidget, bme280_results
from custom_widgets import DragonImageWidget, HeaderWidget, FooterButtonsWidget
from rocket_launches import RocketLaunchesData


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

        layout.setContentsMargins(0, -300, 0, 0)                    # Move everything up by reducing top margin
        layout.setVerticalSpacing(20)  

    def update_labels(self):
        # BME data
        temp, humidity, pressure, dew_point = bme280_results()
        self.temp_display.setValue(float(temp))
        self.pressure_display.setValue(float(pressure))
        self.humidity_display.setValue(float(humidity))
        self.dew_point_display.setValue(float(dew_point))

    def move_temp_display(self, dx, dy):
        self.temp_display.move(self.temp_display.x() + dx, self.temp_display.y() + dy)

    def move_humidity_display(self, dx, dy):
        self.humidity_display.move(self.humidity_display.x() + dx, self.humidity_display.y() + dy)

    def move_pressure_display(self, dx, dy):
        self.pressure_display.move(self.pressure_display.x() + dx, self.pressure_display.y() + dy)

    def move_dew_point_display(self, dx, dy):
        self.dew_point_display.move(self.dew_point_display.x() + dx, self.dew_point_display.y() + dy)
        

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

        self.buttons_widget = FooterButtonsWidget()
        layout_h.addWidget(self.buttons_widget)  

        # Ensure the BottomWidget expands horizontally
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setFixedHeight(80)  

    def eject_dashboard(self):
        print("Safely ejected out of capsule.")
        QApplication.quit()


class MainWidget(QWidget):
    def __init__(self):
        super().__init__()     
 
        self.stacked_widget = QStackedWidget(self)

        self.header_widget = HeaderWidget()
        self.center_grid_widget = CenterGridWidget()
        self.bottom_widget = BottomWidget()

        # Create other views
        self.launch_view = LaunchWidget()
        self.apod_view = ApodWidget()
        self.mars_view = MarsWidget()
        self.spacex_view = SpaceXWidget()

        # Add widgets to QStackedWidget
        self.stacked_widget.addWidget(self.center_grid_widget)
        self.stacked_widget.addWidget(self.launch_view)
        self.stacked_widget.addWidget(self.apod_view)
        self.stacked_widget.addWidget(self.mars_view)
        self.stacked_widget.addWidget(self.spacex_view)

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

        # Links all buttons in footer to different displays
        self.bottom_widget.buttons_widget.dragon_button.clicked.connect(self.display_main_widget)
        self.bottom_widget.buttons_widget.fh_button.clicked.connect(self.display_rocket_launches_widget)
        self.bottom_widget.buttons_widget.apod_button.clicked.connect(self.display_apod_widget)
        self.bottom_widget.buttons_widget.rover_button.clicked.connect(self.display_mars_widget)
        self.bottom_widget.buttons_widget.spacex_button.clicked.connect(self.display_spacex_widget)

        self.header_widget.setParent(self)
        # self.center_grid_widget.setParent(self)
        self.bottom_widget.setParent(self)
        
        self.setCursor(Qt.BlankCursor)
        self.center_positioned = False
        self.display_main_widget()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.updateWidgetPositions()

    def updateWidgetPositions(self):
        # Fixed positions for 800x480 screen
        header_y_position = 40 
        bottom_widget_y_position = 480 - 70 
        self.header_widget.move((800 - self.header_widget.width()) // 2, header_y_position - 30)
        self.stacked_widget.setGeometry(0, 0, 800, 480)             # Set stacked widget to cover whole screen

        # Position bottom widget permanently flush with bottom of screen
        self.bottom_widget.setFixedWidth(800)
        self.bottom_widget.move(0, bottom_widget_y_position)

        # Ensure proper positioning of center_grid_widget elements
        if self.stacked_widget.currentWidget() == self.center_grid_widget:
            center_grid_widget_y_offset = 52.5              # Move center_grid_wdiget down
            center_grid_widget_height = self.stacked_widget.height() - center_grid_widget_y_offset 
            self.center_grid_widget.setGeometry(0, center_grid_widget_y_offset, self.stacked_widget.width(), center_grid_widget_height)
            self.center_grid_widget.move_temp_display(-130, -20)      
            self.center_grid_widget.move_humidity_display(130, -20)
            self.center_grid_widget.move_pressure_display(80, -60)
            self.center_grid_widget.move_dew_point_display(-80, -60)
            self.center_positioned = True

    def display_main_widget(self, event=None):
        self.stacked_widget.setCurrentWidget(self.center_grid_widget)
        self.header_widget.show()
        self.bottom_widget.buttons_widget.set_active_button(self.bottom_widget.buttons_widget.dragon_button)
        self.updateWidgetPositions()            # Ensure proper positioning when displayed

    def display_rocket_launches_widget(self, event=None):
        self.stacked_widget.setCurrentWidget(self.launch_view)
        self.header_widget.hide()
        self.bottom_widget.buttons_widget.set_active_button(self.bottom_widget.buttons_widget.fh_button)

    def display_apod_widget(self, event=None):
        self.stacked_widget.setCurrentWidget(self.apod_view)
        self.header_widget.hide()
        self.bottom_widget.buttons_widget.set_active_button(self.bottom_widget.buttons_widget.apod_button)

    def display_mars_widget(self, event=None):
        self.stacked_widget.setCurrentWidget(self.mars_view)
        self.header_widget.hide()
        self.bottom_widget.buttons_widget.set_active_button(self.bottom_widget.buttons_widget.rover_button)

    def display_spacex_widget(self, event=None):
        self.stacked_widget.setCurrentWidget(self.spacex_view)
        self.header_widget.hide()
        self.bottom_widget.buttons_widget.set_active_button(self.bottom_widget.buttons_widget.spacex_button)



# TODO: List of launches
class LaunchWidget(QWidget):
    def __init__(self):
        super().__init__()
        
        layout = QVBoxLayout()
        layout.addWidget(QLabel("TODO: Launch page"))

        # Config
        launch_api_url = "https://lldev.thespacedevs.com/2.2.0/launch/upcoming/"
        api_url_filters = "limit=10&include_suborbital=true&hide_recent_previous=true&ordering=net&mode=list&tbd=true"
        api_url = f"{launch_api_url}?{api_url_filters}"
        rocket_launch_obj = RocketLaunchesData(api_url)

        rocket_launch_obj.rocket_query_results()
        rocket_launch_obj.get_filtered_results()
        while True:
            print(rocket_launch_obj.updated_net())

        self.setLayout(layout)


# TODO: Randomly selected SpaceX image
class SpaceXWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.text = QLabel("SPACEX IMAGES", alignment=Qt.AlignCenter)
        layout = QVBoxLayout()
        layout.addWidget(self.text)
        self.setLayout(layout)


# TODO: APOD image
class ApodWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.text = QLabel("SPACEX IMAGES", alignment=Qt.AlignCenter)
        layout = QVBoxLayout()
        layout.addWidget(self.text)
        self.setLayout(layout)


# TODO: Mars data
class MarsWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.text = QLabel("SPACEX IMAGES", alignment=Qt.AlignCenter)
        layout = QVBoxLayout()
        layout.addWidget(self.text)
        self.setLayout(layout)


if __name__ == "__main__":
    app = QApplication([])
    signal.signal(signal.SIGINT, QApplication.quit)     # Signal handler for ESC
    widget = MainWidget()
    widget.showFullScreen()
    sys.exit(app.exec())
