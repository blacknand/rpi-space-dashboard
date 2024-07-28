from dotenv import load_dotenv
import requests
import json
import os
import importlib.util
import sys
from datetime import datetime, timedelta
from custom_widgets import ImageDownloadWorker, WorkerSignals
from PySide6.QtCore import Slot, QThreadPool, QRunnable
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton
from PySide6.QtGui import QPixmap

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


class APODWorker(QRunnable):
    def __init__(self, date=None):
        super().__init__()
        self.signals = WorkerSignals()
        self.date = date

    @Slot()
    def run(self):
        try:
            url = f'https://api.nasa.gov/planetary/apod?api_key={os.environ.get("nasa_key")}'
            if self.date:
                url += f"&date={self.date}"
            raw_response = requests.get(url).text
            response = json.loads(raw_response)
            self.signals.result.emit(response)
        except requests.RequestException as e:
            self.signals.error.emit(f"APOD Error: {e}")
        finally:
            self.signals.finished.emit()


class ApodWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.apod_title = None
        self.apod_explaination = None
        self.apod_url = None
        self.media_type = None
        self.apod_download = False
        self.current_date = datetime.today()

        self.apod_label = QLabel(self)
        self.apod_label.setScaledContents(True)
        self.download_button = QPushButton("!", self)
        self.download_button.setMaximumSize(100, 30)

        main_layout = QVBoxLayout()
        image_layout = QHBoxLayout()
        button_layout = QHBoxLayout()
        image_layout.addWidget(self.apod_label)
        button_layout.addStretch()
        button_layout.addWidget(self.download_button)
        main_layout.addLayout(button_layout)
        main_layout.addLayout(image_layout)
        self.setLayout(main_layout)

        self.threadpool = QThreadPool()
        self.send_apod_request()

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
        
        print(response)
        self.apod_title = apod_object_parser.get_title(response)
        self.apod_explaination = apod_object_parser.get_explaination(response)
        self.apod_url = apod_object_parser.get_url(response)
        self.media_type = apod_object_parser.get_media_type(response)

        """
        if the media type is a video then display the previous APOD
        """
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
        self.apod_label.setPixmap(pixmap)
        self.apod_download = True

    