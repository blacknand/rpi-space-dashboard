import sys
import signal
from PySide6.QtCore import Qt, QTimer, QEvent, Slot, QThreadPool
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QGridLayout, QPushButton, QHBoxLayout, QSizePolicy, QStackedWidget, QScrollArea, QScroller
from rocket_launches import RocketLaunchesData
from bme280 import TempWidget, HumidityWidget, PressureWidget, DewPointWidget, bme280_results
from custom_widgets import DragonImageWidget, FooterButtonsWidget, BMEDataWidget, HeaderWidget, LaunchEntryWidget, NewsEntryWidget
from rocket_launches import RocketLaunchesData
from nasa_apis import ApodWidget
from space_news import SpaceNewsAPI
from workers import APIWorker
from datetime import timedelta


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

        # Config

        self.stacked_widget = QStackedWidget(self)

        self.header_widget = HeaderWidget()
        self.center_grid_widget = CenterGridWidget()
        self.bottom_widget = BottomWidget()

        # Create other views
        self.launch_view = LaunchWidget()
        self.apod_view = ApodWidget()
        self.bme_data_view = BMEDataWidget()
        self.space_news_view = SpaceNewsWidget()

        # Add widgets to QStackedWidget
        self.stacked_widget.addWidget(self.center_grid_widget)
        self.stacked_widget.addWidget(self.launch_view)
        self.stacked_widget.addWidget(self.apod_view)
        self.stacked_widget.addWidget(self.bme_data_view)
        self.stacked_widget.addWidget(self.space_news_view)

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
        self.bottom_widget.buttons_widget.bme_data_button.clicked.connect(self.display_bme_data_widget)
        self.bottom_widget.buttons_widget.spacex_button.clicked.connect(self.display_news_widget)

        self.header_widget.setParent(self)
        self.bottom_widget.setParent(self)
        
        self.setCursor(Qt.BlankCursor)
        self.center_positioned = False
        self.display_main_widget()

        self.threadpool = QThreadPool()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.updateWidgetPositions()

    def closeEvent(self, event):
        # Make sure all threads are closed before app exits
        self.threadpool.waitForDone()
        event.accept()

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

    def display_bme_data_widget(self, event=None):
        self.stacked_widget.setCurrentWidget(self.bme_data_view)
        self.header_widget.hide()
        self.bottom_widget.buttons_widget.set_active_button(self.bottom_widget.buttons_widget.bme_data_button)

    def display_news_widget(self, event=None):
        self.stacked_widget.setCurrentWidget(self.space_news_view)
        self.header_widget.hide()
        self.bottom_widget.buttons_widget.set_active_button(self.bottom_widget.buttons_widget.spacex_button)


class LaunchWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff) 
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  
        QScroller.grabGesture(self.scroll_area.viewport(), QScroller.LeftMouseButtonGesture)            # Enable kinetic scrolling

        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_area.setWidget(self.scroll_content)

        self.layout.addWidget(self.scroll_area)

        self.setFixedHeight(425)

        self.setStyleSheet("""
            QWidget {
                border: none;
            }
        """)

        # Config for rocket launches
        launch_api_url = "https://lldev.thespacedevs.com/2.2.0/launch/upcoming/"
        api_url_filters = "limit=10&include_suborbital=true&hide_recent_previous=true&ordering=net&mode=list&tbd=true"
        self.api_url = f"{launch_api_url}?{api_url_filters}"
        self.rocket_launch_obj = RocketLaunchesData(self.api_url)
        self.rocket_launch_obj.rocket_query_results()
        self.rocket_launch_obj.get_filtered_results()

        self.api_timer = QTimer(self)
        self.api_timer.timeout.connect(self.send_api_request)
        self.api_timer.start(timedelta(minutes=1).total_seconds() * 1000)                          # LL2 API request every 4 minutes to use all 15 requests every hour

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_launches)
        self.timer.start(1000)

        self.threadpool = QThreadPool()
        self.send_api_request()

    def send_api_request(self):
        worker = APIWorker(self.api_url)
        print(f"Active threads: {self.threadpool.activeThreadCount()}")
        worker.signals.result.connect(self.handle_api_response)
        worker.signals.error.connect(self.handle_error)
        # worker.signals.finished.connect(self.finished_thread)
        self.threadpool.start(worker)

    @Slot()
    def finished_thread(self):
        print("thread finished")

    @Slot(object)
    def handle_api_response(self, result):
        # Check if LL2 API request send back error
        if isinstance(result, str) and result.startswith("Error:"):
            print(result)
            return
        
        self.rocket_launch_obj.query_results = result
        self.rocket_launch_obj.get_filtered_results()
        self.update_launches()

    @Slot(str)
    def handle_error(self, error):
        print(error)

    def update_launches(self):
        launches = self.rocket_launch_obj.updated_net()
        self.display_launches(launches)

    def display_launches(self, launches):
        existing_widgets = {self.scroll_layout.itemAt(i).widget().launch_data['name']: self.scroll_layout.itemAt(i).widget()
                            for i in range(self.scroll_layout.count())}
        
        for launch_data in launches:
            if launch_data['name'] in existing_widgets:
                existing_widgets[launch_data['name']].update_data(launch_data)
            else:
                launch_entry = LaunchEntryWidget(launch_data)
                self.scroll_layout.addWidget(launch_entry)
        
        for i in reversed(range(self.scroll_layout.count())):
            widget = self.scroll_layout.itemAt(i).widget()
            if widget.launch_data['name'] not in [ld['name'] for ld in launches]:
                widget.deleteLater()

    def event(self, event):
        if event.type() == QEvent.TouchBegin or event.type() == QEvent.TouchUpdate or event.type() == QEvent.TouchEnd:
            return self.scroll_area.event(event)
        return super().event(event)


class SpaceNewsWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        QScroller.grabGesture(self.scroll_area.viewport(), QScroller.LeftMouseButtonGesture)  # Enable kinetic scrolling

        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_area.setWidget(self.scroll_content)

        self.layout.addWidget(self.scroll_area)

        self.setFixedHeight(425)

        self.setStyleSheet("""
            QWidget {
                border: none;
            }
        """)

        self.article_url = "https://api.spaceflightnewsapi.net/v4/articles?limit=10&is_feature=true"
        self.report_url = "https://api.spaceflightnewsapi.net/v4/reports?limit=10"

        self.news_obj = SpaceNewsAPI(article_url=self.article_url, report_url=self.report_url)
        self.news_results = self.news_obj.get_filtered_results(type_="article")

        self.image_cache = {}

        self.api_timer = QTimer(self)
        self.api_timer.timeout.connect(self.send_api_request)
        self.api_timer.start(timedelta(hours=1).total_seconds() * 1000)

        self.threadpool = QThreadPool()
        self.send_api_request()

    def send_api_request(self):
        worker = APIWorker(self.article_url)
        print(f"Active threads: {self.threadpool.activeThreadCount()}")

        worker.signals.result.connect(self.handle_api_response)
        worker.signals.error.connect(self.handle_error)
        # worker.signals.finished.connect(self.finished_thread)
        self.threadpool.start(worker)

    @Slot()
    def finished_thread(self):
        print("thread finished")

    @Slot(object)
    def handle_api_response(self, result):
        if isinstance(result, str):
            print(result)
            return

        self.news_obj.query_results = result
        self.news_results = self.news_obj.get_filtered_results(type_="article")
        self.display_news(self.news_results)

    @Slot(str)
    def handle_error(self, error):
        print(error)

    def display_news(self, news):
        # Get the set of currently displayed article URLs
        displayed_urls = {self.scroll_layout.itemAt(i).widget().news_data['url'] for i in range(self.scroll_layout.count())}

        # Add new news entries if not already displayed
        for news_data in news:
            if news_data['url'] not in displayed_urls:
                news_entry = NewsEntryWidget(news_data, image_cache=self.image_cache)
                self.scroll_layout.addWidget(news_entry)
                displayed_urls.add(news_data['url'])

        # Remove widgets that are already displayed
        current_news_urls = {nd['url'] for nd in news}
        for i in reversed(range(self.scroll_layout.count())):
            widget = self.scroll_layout.itemAt(i).widget()
            if widget.news_data['url'] not in current_news_urls:
                widget.deleteLater()

    def event(self, event):
        if event.type() == QEvent.TouchBegin or event.type() == QEvent.TouchUpdate or event.type() == QEvent.TouchEnd:
            return self.scroll_area.event(event)
        return super().event(event)


if __name__ == "__main__":
    app = QApplication([])
    signal.signal(signal.SIGINT, QApplication.quit)     # Signal handler for ESC
    widget = MainWidget()
    widget.showFullScreen()
    # widget.resize(800, 480)
    widget.show()
    sys.exit(app.exec())
 