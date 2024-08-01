import sqlite3
from PySide6.QtGui import QPixmap, QColor, QPainter, QIcon, QRegion
from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QGraphicsDropShadowEffect, QVBoxLayout, QSpacerItem, QSizePolicy, QPushButton
from PySide6.QtCore import Qt, QTimer, QRectF, QSize, QPoint, Slot, QThreadPool
from PySide6.QtWidgets import QWidget, QGraphicsScene, QGraphicsView, QGraphicsPixmapItem, QVBoxLayout, QGraphicsDropShadowEffect
from PySide6.QtGui import QPixmap, QColor, QFont, QPolygon
from datetime import datetime, date, timezone, timedelta
from workers import ImageDownloadWorker, CollectBMEWorker, BMEDayMaxWorker, BMEHourMaxWorker
from db_operations import DBOperations


class DragonImageWidget(QWidget):
    def __init__(self, width=None, height=None):
        super().__init__()

        self.image_path = "images/spacex_images/file.png"
        self.image = QPixmap(self.image_path)

        if width is None or height is None:
            width = self.image.width()
            height = self.image.height()

        # Scale the image to the desired size
        self.scaled_image = self.image.scaled(width, height, Qt.KeepAspectRatio, Qt.SmoothTransformation)

        # Create a QGraphicsScene
        self.scene = QGraphicsScene(self)
        self.view = QGraphicsView(self.scene, self)
        self.view.setStyleSheet("background: transparent; border: none;")
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setRenderHint(QPainter.SmoothPixmapTransform)

        self.capsule_item = QGraphicsPixmapItem(self.scaled_image)

        # Create the shadow effect to simulate the bottom glow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(50)
        shadow.setColor(QColor(255, 255, 255, 160))                 # White glow
        shadow.setOffset(0, 20)                                     # Set shadow offset for more emphasis on the bottom
        self.capsule_item.setGraphicsEffect(shadow)

        self.scene.addItem(self.capsule_item)
        self.scene.setSceneRect(QRectF(self.scaled_image.rect()))

        # Set up the layout
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.view)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(self.layout)

        # Set fixed size for the widget based on the scaled image size
        self.setFixedSize(self.scaled_image.size())

    def sizeHint(self):
        return QSize(self.scaled_image.width(), self.scaled_image.height())



class HeaderWidget(QWidget):
    # Header widget with title, date and time
    def __init__(self):
        super().__init__()

        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        self.header_title = QLabel("CABIN OVERVIEW")
        today = date.today()
        self.formatted_cur_date = f'{today.strftime("%a")}, {today.strftime("%b")} {today.strftime("%d")}'
        self.current_time = datetime.now().strftime("%H:%M:%S")
        self.date_label = QLabel(self.formatted_cur_date)
        self.time_label = QLabel(self.current_time)

        self.date_label.setFont(QFont("Arial", 18, QFont.Bold))
        self.time_label.setFont(QFont("Arial", 18, QFont.Bold))
        self.header_title.setFont(QFont("Arial", 14, QFont.Bold))

        self.layout.addSpacerItem(QSpacerItem(20, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.layout.addWidget(self.date_label)
        self.layout.addSpacerItem(QSpacerItem(40, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.layout.addWidget(self.header_title)
        self.layout.addSpacerItem(QSpacerItem(40, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.layout.addWidget(self.time_label)
        self.layout.addSpacerItem(QSpacerItem(20, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))

        self.setStyleSheet("""
            QLabel {color: white;}
        """)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_labels)
        self.timer.start(1000)

    def update_labels(self):
        today = date.today()
        formatted_cur_date = f'{today.strftime("%a")}, {today.strftime("%b")} {today.strftime("%d")}'
        current_time = datetime.now().strftime("%H:%M:%S")
        self.date_label.setText(formatted_cur_date)
        self.time_label.setText(current_time)


class FooterButtonsWidget(QWidget):
    # Footer widget with buttons + icons to other views
    def __init__(self):
        super().__init__()
        self.setObjectName("footerButtonsWidget")       # Set obj name to apply CSS stylesheet directly
        layout = QHBoxLayout(self)

        self.dragon_button = self.create_icon_button("images/spacex_images/dragon-button-icon.png")
        self.fh_button = self.create_icon_button("images/spacex_images/fh-button-icon.png")
        self.apod_button = self.create_icon_button("images/nasa_images/nasa-button.png")
        self.bme_data_button = self.create_icon_button("images/nasa_images/space-data.png")
        self.spacex_button = self.create_icon_button("images/nasa_images/space-station.png")

        layout.addWidget(self.dragon_button)
        layout.addWidget(self.fh_button)
        layout.addWidget(self.apod_button)
        layout.addWidget(self.bme_data_button)
        layout.addWidget(self.spacex_button)
        self.setFixedSize(60,400)

        self.setMinimumHeight(60)
        self.setMinimumWidth(400)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)           # Required to apply style sheet on QWidget
        self.setStyleSheet("""
            QWidget#footerButtonsWidget {
                background-color: #000000;
            }
        """)

        self.current_button = None  # Track the currently active button

    def create_icon_button(self, icon_path):
        button = QPushButton()
        button.setIcon(QIcon(icon_path))
        button.setIconSize(QSize(40, 40))
        button.setFixedSize(40, 40)
        button.setStyleSheet("QPushButton { background-color: transparent; border: none; }")
        return button
    
    def set_active_button(self, button):
        self.current_button = button
        self.update()  # Trigger a repaint

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)

        # Define the downward sloped trapezoid shape
        width = self.width()
        height = self.height()
        trapezoid = QPolygon([
            QPoint(20, 0),
            QPoint(width - 20, 0),
            QPoint(width, height),
            QPoint(0, height)
        ])

        # Set the brush to black and draw the trapezoid
        painter.setBrush(QColor("#002B5A"))
        painter.setPen(Qt.NoPen)                # Remove the border
        painter.drawPolygon(trapezoid)

        # Apply the shape to the widget
        region = QRegion(trapezoid)
        self.setMask(region)

        # Draw the line under the active button
        if self.current_button:
            button_rect = self.current_button.geometry()
            line_y = button_rect.bottom() + 5  # Position the line just below the button
            painter.setPen(QColor("white"))
            painter.drawLine(button_rect.left(), line_y, button_rect.right(), line_y)
            

class LaunchEntryWidget(QWidget):
    def __init__(self, launch_data):
        super().__init__()
        self.launch_data = launch_data
        self.image_downloaded = False

        self.image_label = QLabel(self)
        self.image_label.setFixedSize(190, 190)
        self.image_label.setScaledContents(True)

        layout = QHBoxLayout()
        layout.addSpacing(7.5)
        layout.addWidget(self.image_label)
        layout.setSpacing(0)  
        layout.setContentsMargins(0, 0, 0, 0)  
        self.info_layout = QVBoxLayout()
        self.name = QLabel(launch_data["name"])
        self.name.setFont(QFont("Arial", 14, QFont.Bold))
        self.name.setAlignment(Qt.AlignmentFlag.AlignCenter) 
        self.info_layout.addWidget(self.name)
        self.lsp = QLabel(launch_data["lsp_name"])
        self.lsp.setFont(QFont("Arial", 14, QFont.Bold))
        self.lsp.setAlignment(Qt.AlignmentFlag.AlignCenter) 
        self.info_layout.addWidget(self.lsp)
        self.location = QLabel(launch_data['location'])
        self.location.setFont(QFont("Arial", 14, QFont.Bold))
        self.location.setAlignment(Qt.AlignmentFlag.AlignCenter) 
        self.info_layout.addWidget(self.location)
        self.pad = QLabel(launch_data['pad'])
        self.pad.setFont(QFont("Arial", 14, QFont.Bold))
        self.pad.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.info_layout.addWidget(self.pad)
        self.mission = QLabel(launch_data["mission_type"])
        self.mission.setFont(QFont("Arial", 14, QFont.Bold))
        self.mission.setAlignment(Qt.AlignmentFlag.AlignCenter) 
        self.info_layout.addWidget(self.mission)
        self.countdown_label = QLabel()
        self.countdown_label.setFont(QFont('Arial', 14, QFont.Bold))
        self.countdown_label.setAlignment(Qt.AlignmentFlag.AlignCenter) 
        self.info_layout.addWidget(self.countdown_label)
        self.update_countdown()
        self.time_data = QLabel(f"{launch_data['net']} | {launch_data['status']}")
        self.time_data.setFont(QFont("Arial", 14, QFont.Bold))
        self.time_data.setAlignment(Qt.AlignmentFlag.AlignCenter) 
        self.info_layout.addWidget(self.time_data)

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)
        self.setStyleSheet("""
            QWidget {
                background-color: #2E2D4D;
                border-radius: 5%;  
            }
            QLabel {
                color: white;
            }

        """)

        info_widget = QWidget()
        info_widget.setLayout(self.info_layout)

        layout.addWidget(info_widget)
        self.setLayout(layout)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_countdown)
        self.timer.start(1000)

        self.threadpool = QThreadPool()
        self.start_image_download(launch_data["image"])

    def start_image_download(self, image_url):
        if not self.image_downloaded:
            worker = ImageDownloadWorker(image_url)
            worker.signals.result.connect(self.handle_image_download)
            worker.signals.error.connect(self.handle_error)
            self.threadpool.start(worker)

    @Slot(object)
    def handle_image_download(self, image_data):
        pixmap = QPixmap()
        pixmap.loadFromData(image_data)
        
        target_size = self.image_label.size()
        scaled_pixmap = pixmap.scaled(target_size, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        
        x_offset = (scaled_pixmap.width() - target_size.width()) // 2
        y_offset = (scaled_pixmap.height() - target_size.height()) // 2
        cropped_pixmap = scaled_pixmap.copy(x_offset, y_offset, target_size.width(), target_size.height())
        
        self.image_label.setPixmap(cropped_pixmap)
        self.image_downloaded = True

    @Slot(str)
    def handle_error(self, error):
        print(error)

    def update_data(self, launch_data):
        self.launch_data.update(launch_data)
        self.name.setText(launch_data["name"])
        self.lsp.setText(launch_data["lsp_name"])
        self.location.setText(launch_data['location'])
        self.pad.setText(launch_data["pad"])
        self.mission.setText(launch_data["mission_type"])
        self.time_data.setText(f"{launch_data['net']} | {launch_data['status']}")
        self.update_countdown()

    def update_countdown(self):
        countdown_dict = self.launch_data["countdown"]
        countdown_delta = timedelta(days=countdown_dict['days'],
                                    hours=countdown_dict['hours'],
                                    minutes=countdown_dict['minutes'],
                                    seconds=countdown_dict['seconds'])
        time_diff = datetime.now(timezone.utc) - countdown_delta
        sign = "T+" if datetime.now(timezone.utc) < time_diff else "T-"
        countdown_text = f"{sign} {countdown_dict['days']:02d} : {countdown_dict['hours']:02d} : {countdown_dict['minutes']:02d} : {countdown_dict['seconds']:02d}"
        self.countdown_label.setText(countdown_text)


class NewsEntryWidget(QWidget):
    def __init__(self, news_data, entry_type, image_cache):
        super().__init__()
        self.news_data = news_data
        self.image_cache = image_cache

        self.setFixedSize(765, 200)
        self.setObjectName("newsEntryWidget")

        self.image_label = QLabel(self)
        self.image_label.setGeometry(10, 10, 250, 180) 
        self.image_label.setScaledContents(True)

        start_x = 270 + 10

        published_date = self.convert_iso(news_data["published"])
        self.published = QLabel(published_date, self)
        self.published.setGeometry(start_x, 10, 200, 20)  
        self.published.setStyleSheet("color: white; font-size: 12px;")

        self.news_site = QLabel(news_data["news_site"], self)
        self.news_site.setGeometry(540, 10, 200, 20)  
        self.news_site.setStyleSheet("color: white; font-size: 12px;")
        self.news_site.setAlignment(Qt.AlignRight)

        self.title = QLabel(news_data["title"], self)
        self.title.setGeometry(start_x, 40, 475, 40)  
        self.title.setStyleSheet("font-size: 16px; font-weight: bold; color: white;")
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setWordWrap(True)

        self.summary = QLabel(news_data["summary"], self)
        self.summary.setGeometry(start_x, 90, 475, 100)  
        self.summary.setStyleSheet("font-size: 14px; color: white;")
        self.summary.setWordWrap(True)

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)
        self.setStyleSheet("""
            QWidget#newsEntryWidget {
                background-color: #2E2D4D; 
                border-radius: 5%;
            }
            QWidget {
                background-color: #2E2D4D; 
            }
        """)

        self.threadpool = QThreadPool()
        self.start_image_download(news_data["image_url"])

    def convert_iso(self, iso_date):
        dt = datetime.fromisoformat(iso_date)
        return dt.strftime("%d/%m/%Y, %H:%M:%S")


    def start_image_download(self, image_url):
        if image_url in self.image_cache:
            self.handle_image_download(self.image_cache[image_url])
        else:
            worker = ImageDownloadWorker(image_url)
            worker.signals.result.connect(self.handle_image_download)
            worker.signals.error.connect(self.handle_error)
            self.threadpool.start(worker)

    @Slot(tuple)
    def handle_image_download(self, image_data):
        pixmap = QPixmap()
        pixmap.loadFromData(image_data)

        # Define the fixed size for the image
        target_size = QSize(400, 200)

        # Scale the pixmap to fit within the target size, keeping aspect ratio
        scaled_pixmap = pixmap.scaled(target_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)

        # Calculate offsets to crop the image to the fixed size
        x_offset = (scaled_pixmap.width() - target_size.width()) // 2
        y_offset = (scaled_pixmap.height() - target_size.height()) // 2
        cropped_pixmap = scaled_pixmap.copy(x_offset, y_offset, target_size.width(), target_size.height())

        self.image_label.setPixmap(cropped_pixmap)
        self.image_cache[self.news_data["image_url"]] = image_data  # Cache the image data

    @Slot(str)
    def handle_error(self, error):
        print(error)


class BMEDataWidget(QWidget):
    def __init__(self):
        super().__init__()
        db_obj = DBOperations()
        conn = sqlite3.connect("sensor_setup.db")
        db_obj.db_config("sensor_setup.db", conn)
        db_obj.setup_db()
        conn.close()

        self.test1 = QLabel()
        self.test2 = QLabel()

        self.bme_var_timer = QTimer(self)
        self.bme_var_timer.timeout.connect(self.collect_bme_worker)
        self.bme_var_timer.start(60000)

        self.bme_hour_timer = QTimer(self)
        self.bme_hour_timer.timeout.connect(self.hour_max_worker)
        self.bme_hour_timer.start(3600000)

        self.bme_day_timer = QTimer(self)
        self.bme_day_timer.timeout.connect(self.day_max_worker)
        self.bme_day_timer.start(86400000)

        self.threadpool = QThreadPool()
        self.setup_widget()

    def setup_widget(self):
        pass

    def collect_bme_worker(self):
        worker = CollectBMEWorker()
        worker.signals.result.connect(self.null_method)
        worker.signals.error.connect(self.handle_error)
        self.threadpool.start(worker)

    def hour_max_worker(self):
        worker = BMEHourMaxWorker()
        worker.signals.result.connect(self.plot_hour_max)
        worker.signals.error.connect(self.handle_error)
        self.threadpool.start(worker)

    def day_max_worker(self):
        worker = BMEDayMaxWorker()
        worker.signals.result.connect(self.plot_hour_day)
        worker.signals.error.connect(self.handle_error)
        self.threadpool.start(worker)

    @Slot(object)
    def null_method():
        pass

    @Slot(str)
    def handle_error(self, error):  
        print(error)

    @Slot(object)
    def plot_hour_max(self):
        self.test1.setText("test1")

    @Slot(object)
    def plot_day_max(self):
        self.test2.setText("test2")