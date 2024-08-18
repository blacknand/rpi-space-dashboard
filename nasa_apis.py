import requests
import json
import os
import importlib.util
import sys
from dotenv import load_dotenv
from datetime import datetime, timedelta
from custom_widgets import ImageDownloadWorker
from PySide6.QtCore import Slot, QThreadPool, QTimer, QTime, Qt
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton, QStackedLayout, QSizePolicy
from PySide6.QtGui import QPixmap
from workers import APODWorker

load_dotenv("keys.env")

# Setup relative path to the directory containing module
dir_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'apod-api'))

# Add the directory to the Python path
sys.path.append(dir_path)

# Define the module name and file path
module_name = 'apod_object_parser'
file_path = os.path.join(dir_path, 'apod_parser', 'apod_object_parser.py')

# Load the module
spec = importlib.util.spec_from_file_location(module_name, file_path)
apod_object_parser = importlib.util.module_from_spec(spec)
spec.loader.exec_module(apod_object_parser)

class APODPopUpWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("APOD")
        self.setFixedSize(400, 300) 

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(5)

        self.title = QLabel("No Data", self)
        self.explanation = QLabel("No Data", self)

        self.explanation.setWordWrap(True)  
        self.title.setAlignment(Qt.AlignCenter)
        self.explanation.setAlignment(Qt.AlignCenter)

        self.layout.addSpacing(10)
        self.layout.addWidget(self.title, alignment=Qt.AlignCenter)
        self.layout.addSpacing(10)
        self.layout.addWidget(self.explanation, alignment=Qt.AlignCenter)

        self.layout.addStretch(1)

        self.close_button = QPushButton("Close", self)
        self.close_button.clicked.connect(self.close)
        self.layout.addWidget(self.close_button, alignment=Qt.AlignCenter)

        self.setLayout(self.layout)

    def update_content(self, title, explanation, apod_date):
        self.title.setText(title)
        self.explanation.setText(explanation)
        self.setWindowTitle(f"APOD - {apod_date}")


class ApodWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.apod_title = None
        self.apod_explaination = None
        self.apod_url = None
        self.media_type = None
        self.apod_download = False
        self.current_date = datetime.today()
        self.apod_date = None

        self.apod_label = QLabel(self)
        self.apod_label.setScaledContents(False)
        self.apod_label.setAlignment(Qt.AlignCenter)
        self.apod_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.apod_label.setStyleSheet("background-color: transparent;")

        self.download_button = QPushButton("!", self)
        self.download_button.setFixedSize(30, 30)
        self.download_button.setStyleSheet("""
            QPushButton {
                border-radius: 15px;
                background-color: #3498db;
                color: white;
                font-weight: bold;
                border: 2px solid #2980b9;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #1abc9c;
            }
        """)
        self.download_button.clicked.connect(self.show_apod_popup)

        stacked_layout = QStackedLayout()
        stacked_layout.addWidget(self.apod_label)

        main_layout = QVBoxLayout()
        main_layout.addLayout(stacked_layout)
        main_layout.setContentsMargins(0, 0, 0, 0)  
        main_layout.setSpacing(0) 
        self.setLayout(main_layout)
        self.setObjectName("ApodWidget")  
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)
        self.setStyleSheet("""
            QWidget#ApodWidget {
                background-color: black;
            }
        """)

        self.download_button.setParent(self)
        self.download_button.raise_()
        self.download_button.move(self.width() - self.download_button.width() - 10, 10)  

        self.threadpool = QThreadPool()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.send_apod_request)
        # self.start_timer()

        self.send_apod_request()

        self.apod_popup_widget = APODPopUpWidget()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.download_button.move(self.width() - self.download_button.width() - 10, 10)
        self.scale_pixmap()

    def scale_pixmap(self):
        if not self.apod_download:
            return
        pixmap = self.apod_label.pixmap()
        if pixmap:
            self.apod_label.setPixmap(pixmap.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def start_timer(self):
        current_time = QTime.currentTime()
        request_et = QTime(5, 0)  # **Send APOD request @ 5 AM instead of midnight**
        if current_time < request_et:
            secs_till_request = current_time.secsTo(request_et)
        else:
            secs_till_request = current_time.secsTo(request_et) + 86400  # **Calculate time until next 5 AM**

        self.timer.setInterval(secs_till_request * 1000)
        self.timer.start()

        # **Trigger first request at the calculated time and set the daily timer afterward**
        QTimer.singleShot(secs_till_request * 1000, self.set_daily_timer)

    def set_daily_timer(self):
        self.timer.setInterval(86400000)  # **24 hours in milliseconds**
        self.send_apod_request()  # **Ensure the request is sent as soon as the timer starts**
        self.timer.start()

    def send_apod_request(self, date=None):
        if date:
            date_str = date.strftime('%Y-%m-%d')
        else:
            date_str = None
        worker = APODWorker(date_str)
        worker.signals.result.connect(self.handle_apod_response)
        worker.signals.error.connect(self.handle_error)
        self.threadpool.start(worker)

    @Slot(object)
    def handle_apod_response(self, response):
        if isinstance(response, str) and response.startswith("APOD Error:"):
            print(response)
            return
        
        self.apod_title = apod_object_parser.get_title(response)
        self.apod_explaination = apod_object_parser.get_explaination(response)
        self.apod_url = apod_object_parser.get_url(response)
        self.media_type = apod_object_parser.get_media_type(response)
        self.apod_date = apod_object_parser.get_date(response)

        if self.media_type == "image":
            self.start_apod_download(self.apod_url)
        else:
            self.fetch_previous_image_apod()

    def fetch_previous_image_apod(self):
        self.current_date -= timedelta(days=1)
        self.send_apod_request(self.current_date)

    @Slot(str)
    def handle_error(self, error):
        print(error)

    def start_apod_download(self, apod_url):
        if not self.apod_download:
            worker = ImageDownloadWorker(apod_url)
            worker.signals.result.connect(self.handle_apod_download)
            worker.signals.error.connect(self.handle_error)
            self.threadpool.start(worker)

    @Slot(object)
    def handle_apod_download(self, raw_data):
        pixmap = QPixmap()
        pixmap.loadFromData(raw_data)
        self.apod_label.setPixmap(pixmap.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.apod_download = True

    def show_apod_popup(self):
        if self.apod_title and self.apod_explaination:
            self.apod_popup_widget.update_content(self.apod_title, self.apod_explaination, self.apod_date)
        self.apod_popup_widget.show()


class MarsImagesWidget(QWidget):
    def __init__(self):
        super().__init__()

    def curiosity_rover_query():
        mars_url = r'https://api.nasa.gov/mars-photos/api/v1/rovers/curiosity/latest_photos?api_key=' + os.environ.get("nasa_key")
        mars_data = requests.get(mars_url)
        mars_jso = json.loads(mars_data.text)
        # name = mars_jso["latest_photos"][0]["camera"]["full_name"]
        # earth_date = mars_jso["latest_photos"][0]["earth_date"]
        # mars_img_url = mars_jso["latest_photos"][0]["img_src"]
        # sol_date = mars_jso["latest_photos"][0]["sol"]
        # rover = mars_jso["latest_photos"][0]["rover"]["name"]
        # mars_img = requests.get(mars_img_url).content
        # with open('mars_img.jpg', 'wb') as handler:
        #     handler.write(mars_img)

        # return [name, earth_date, sol_date, rover]
        print(mars_jso)

    def opportunity_rover_query():
        mars_url = r'https://api.nasa.gov/mars-photos/api/v1/rovers/opportunity/latest_photos?api_key=' + os.environ.get("nasa_key")
        mars_data = requests.get(mars_url)
        mars_jso = json.loads(mars_data.text)
        print(mars_jso)

    def spirit_rover_query():
        mars_url = r'https://api.nasa.gov/mars-photos/api/v1/rovers/spirity/latest_photos?api_key=' + os.environ.get("nasa_key")
        mars_data = requests.get(mars_url)
        mars_jso = json.loads(mars_data.text)
        print(mars_jso)

# test = MarsImagesWidget()
# test.curiosity_rover_query()
# print()
# test.opportunity_rover_query()
# print()
# test.spirit_rover_query()