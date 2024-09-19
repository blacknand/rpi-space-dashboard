import sqlite3
import io
import subprocess
import webbrowser
import platform
import os
from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QGraphicsDropShadowEffect, QVBoxLayout, QSpacerItem, QSizePolicy, QPushButton
from PySide6.QtCore import Qt, QTimer, QRectF, QSize, Slot, QThreadPool, QPointF, QRect
from PySide6.QtWidgets import QWidget, QGraphicsScene, QGraphicsView, QGraphicsPixmapItem, QVBoxLayout, QGraphicsDropShadowEffect
from PySide6.QtGui import QPixmap, QColor, QFont, QPainterPath, QPolygon, QPainter, QIcon, QRegion
from datetime import datetime, date, timezone, timedelta
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PIL import Image
from workers import ImageDownloadWorker, CollectBMEWorker,BMEHourMaxWorker, BMEDayMaxWorker, ClickableLabel
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
        painter.setRenderHint(QPainter.Antialiasing)

        # Define the width, height, and radius for the top corners
        width = self.width()
        height = self.height()
        radius = 15  # Radius for the top corners only

        # Create a QPainterPath for the custom shape
        path = QPainterPath()

        # Start with a rounded top-left corner
        path.moveTo(radius, 0)
        path.quadTo(0, 0, 0, radius)  # Top-left curve

        # Left side going down straight
        path.lineTo(0, height)

        # Bottom side straight
        path.lineTo(width, height)

        # Right side going up straight
        path.lineTo(width, radius)

        # Top-right curve
        path.quadTo(width, 0, width - radius, 0)

        # Close the path
        path.closeSubpath()

        # Set the brush to the desired color and draw the custom shape
        painter.setBrush(QColor("#EAEAEA"))
        painter.setPen(Qt.NoPen)  # Remove the border
        painter.drawPath(path)

        # Apply the shape to the widget
        region = QRegion(path.toFillPolygon().toPolygon())
        self.setMask(region)

        # Draw the line under the active button
        if self.current_button:
            button_rect = self.current_button.geometry()
            line_y = button_rect.bottom() + 5  # Position the line just below the button
            painter.setPen(QColor("black"))
            painter.drawLine(button_rect.left(), line_y, button_rect.right(), line_y)

        # End the painting process
        painter.end()

            
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
        self.lsp.setFont(QFont("Arial", 14))
        self.lsp.setAlignment(Qt.AlignmentFlag.AlignCenter) 
        self.info_layout.addWidget(self.lsp)
        self.location = QLabel(launch_data['location'])
        self.location.setFont(QFont("Arial", 14))
        self.location.setAlignment(Qt.AlignmentFlag.AlignCenter) 
        self.info_layout.addWidget(self.location)
        self.pad = QLabel(launch_data['pad'])
        self.pad.setFont(QFont("Arial", 14))
        self.pad.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.info_layout.addWidget(self.pad)
        self.mission = QLabel(launch_data["mission_type"])
        self.mission.setFont(QFont("Arial", 14))
        self.mission.setAlignment(Qt.AlignmentFlag.AlignCenter) 
        self.info_layout.addWidget(self.mission)
        self.countdown_label = QLabel()
        self.countdown_label.setFont(QFont('Arial', 14))
        self.countdown_label.setAlignment(Qt.AlignmentFlag.AlignCenter) 
        self.info_layout.addWidget(self.countdown_label)
        self.time_data = QLabel(f"{launch_data['net']} | {launch_data['status']}")
        self.time_data.setFont(QFont("Arial", 14))
        self.time_data.setAlignment(Qt.AlignmentFlag.AlignCenter) 
        self.info_layout.addWidget(self.time_data)

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)
        self.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 5%;  
            }
            QLabel {
                color: black;
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
            # print(f"Active threads: {self.threadpool.activeThreadCount()}")

            worker.signals.result.connect(self.handle_image_download)
            worker.signals.error.connect(self.handle_error)
            self.threadpool.start(worker)

    @Slot(object)
    def handle_image_download(self, image_data):
        pixmap = QPixmap()

        # Check if the image data is in WebP format
        if image_data[:4] == b'RIFF' and image_data[8:12] == b'WEBP':
            image = Image.open(io.BytesIO(image_data))
            with io.BytesIO() as output:
                image.convert("RGB").save(output, format="JPEG")
                image_data = output.getvalue()

        if not pixmap.loadFromData(image_data):
            self.handle_error(f"LaunchEntryWidget::handle_image_download: Image download failed for [{image_data}], image file format most likely not suppoted")
            pixmap = QPixmap("images/nasa_images/saturn-v-default-image.jpg")
            
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
        
        launch_time = datetime.now(timezone.utc) + countdown_delta
        current_time = datetime.now(timezone.utc)
        
        # Calculate time difference
        time_diff = launch_time - current_time

        # Determine sign: T- before launch, T+ if it's within 15 minutes after launch
        if time_diff.total_seconds() > 0:
            sign = "T-"
        elif -time_diff.total_seconds() <= 15 * 60:
            sign = "T+"
        else:
            sign = "T+"

        # Calculate the absolute remaining time for display
        abs_time_diff = abs(time_diff)
        days = abs_time_diff.days
        hours, remainder = divmod(abs_time_diff.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        # Update the countdown display
        countdown_text = f"{sign} {days:02d} : {hours:02d} : {minutes:02d} : {seconds:02d}"
        self.countdown_label.setText(countdown_text)



class NewsEntryWidget(QWidget):
    def __init__(self, news_data, image_cache):
        super().__init__()
        self.news_data = news_data
        self.image_cache = image_cache

        self.setFixedSize(765, 200)
        self.setObjectName("newsEntryWidget")

        self.image_label = ClickableLabel(self)
        self.image_label.setGeometry(10, 10, 250, 180)
        self.image_label.setScaledContents(True)
        self.image_label.clicked.connect(self.open_url_in_browser)

        start_x = 270 + 10

        published_date = self.convert_iso(news_data["published"])
        self.published = QLabel(published_date, self)
        self.published.setGeometry(start_x, 10, 200, 20)  
        self.published.setStyleSheet("color: black; font-size: 12px;")

        self.news_site = QLabel(news_data["news_site"], self)
        self.news_site.setGeometry(540, 10, 200, 20)  
        self.news_site.setStyleSheet("color: black; font-size: 12px;")
        self.news_site.setAlignment(Qt.AlignRight)

        self.title = QLabel(news_data["title"], self)
        self.title.setGeometry(start_x, 40, 475, 40)  
        self.title.setStyleSheet("font-size: 16px; font-weight: bold; color: black;")
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setWordWrap(True)

        self.summary = QLabel(news_data["summary"], self)
        self.summary.setGeometry(start_x, 90, 475, 100)  
        self.summary.setStyleSheet("font-size: 14px; color: black;")
        self.summary.setWordWrap(True)

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)
        self.setStyleSheet("""
            QWidget#newsEntryWidget {
                background-color: #FFF; 
                border-radius: 5%;
            }
            QWidget {
                background-color: #FFF; 
            }
        """)

        self.threadpool = QThreadPool()
        self.setAttribute(Qt.WA_AcceptTouchEvents)
        self.start_image_download(news_data["image_url"])

    def convert_iso(self, iso_date):
        dt = datetime.fromisoformat(iso_date)
        return dt.strftime("%d/%m/%Y, %H:%M:%S")


    def start_image_download(self, image_url):
        if image_url in self.image_cache:
            self.handle_image_download(self.image_cache[image_url])
        else:
            worker = ImageDownloadWorker(image_url)
            # print(f"Active threads: {self.threadpool.activeThreadCount()}")
            worker.signals.result.connect(self.handle_image_download)
            worker.signals.error.connect(self.handle_error)
            self.threadpool.start(worker)

    @Slot(object)
    def handle_image_download(self, image_data):
        pixmap = QPixmap()

        # Check if the image data is in WebP format
        if image_data[:4] == b'RIFF' and image_data[8:12] == b'WEBP':
            image = Image.open(io.BytesIO(image_data))
            with io.BytesIO() as output:
                image.convert("RGB").save(output, format="JPEG")
                image_data = output.getvalue()

        if not pixmap.loadFromData(image_data):
            self.handle_error(f"NewsEntryWidget::handle_image_download: Image download failed for [{image_data[:20]}...{image_data[-5:]}], image file format most likely not supported")
            pixmap = QPixmap("images/nasa_images/lunar-module-eagle-default.jpg")

        target_size = QSize(400, 200)
        scaled_pixmap = pixmap.scaled(target_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)

        x_offset = (scaled_pixmap.width() - target_size.width()) // 2
        y_offset = (scaled_pixmap.height() - target_size.height()) // 2
        cropped_pixmap = scaled_pixmap.copy(x_offset, y_offset, target_size.width(), target_size.height())

        self.image_label.setPixmap(cropped_pixmap)
        self.image_cache[self.news_data["image_url"]] = image_data          # Cache the image data

    @Slot(str)
    def handle_error(self, error):
        print(error)

    def open_url_in_browser(self):
        try:
            if platform.system() == "Linux":
                chrome_path = "/usr/bin/chromium-browser"
                # Check if the chromium-browser path is correct and the URL is valid
                if os.path.isfile(chrome_path) and self.news_data["url"].startswith("http"):
                    subprocess.Popen([chrome_path, '--new-window', f'--window-size=600,380', self.news_data["url"]])
                else:
                    raise ValueError("Invalid URL")
            else:
                webbrowser.open(self.news_data["url"])
        except Exception as e:
            print(f"An error occurred: {e}")


class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=4, height=2, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super().__init__(fig)
        self.setParent(parent)
        FigureCanvas.setSizePolicy(self, QSizePolicy.Expanding, QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)


class BMEDataWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.db_obj = DBOperations()
        conn = sqlite3.connect("sensor_data.db")
        self.db_obj.setup_db(filename="sensor_setup.sql", encoding='utf-8')
        conn.close()

        # Clear the database initially to remove old data
        self.db_obj.clear_database()

        self.current_hour = datetime.now().hour
        self.current_day = date.today()

        main_layout = QVBoxLayout()

        # Center the clock and date at the top
        self.clock_label = QLabel()
        self.cur_date_label = QLabel()

        header_layout = QHBoxLayout()
        header_layout.setSpacing(10)  # Small gap between date and time
        header_layout.setContentsMargins(0, 0, 0, 0)  # Reduce spacing around the text

        header_layout.addStretch()  # Adds stretchable space before the content
        header_layout.addWidget(self.clock_label, alignment=Qt.AlignCenter)
        header_layout.addWidget(self.cur_date_label, alignment=Qt.AlignCenter)
        header_layout.addStretch()  # Adds stretchable space after the content

        header_widget = QWidget()
        header_widget.setLayout(header_layout)

        main_layout.addWidget(header_widget)

        # Create a horizontal layout for the graphs
        graph_layout = QHBoxLayout()

        # Create the first canvas for hourly data
        self.canvas_hourly = MplCanvas(self, width=4, height=2, dpi=100)
        graph_layout.addWidget(self.canvas_hourly)

        # Create the second canvas for daily data
        # self.canvas_daily = MplCanvas(self, width=4, height=2, dpi=100)
        # graph_layout.addWidget(self.canvas_daily)

        graph_widget = QWidget()
        graph_widget.setLayout(graph_layout)

        main_layout.addWidget(graph_widget)
        self.setLayout(main_layout)

        self.setFixedSize(800, 415)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)
        self.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 18px;
            }
            QWidget {
                background-color: transparent;
            }
        """)

        self.clock_timer = QTimer(self)
        self.clock_timer.timeout.connect(self.update_clock)
        self.clock_timer.start(1000)  # Update every second

        self.bme_var_timer = QTimer(self)
        self.bme_var_timer.timeout.connect(self.collect_bme_worker)
        self.bme_var_timer.start(60000)

        self.schedule_timers()

        self.threadpool = QThreadPool()

    def schedule_timers(self):
        now = datetime.now()

        # Calculate time until next hour on the hour
        next_hour = (now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1))
        time_until_next_hour = (next_hour - now).total_seconds() * 1000

        self.bme_hour_timer = QTimer(self)
        self.bme_hour_timer.timeout.connect(self.update_hourly_data)
        QTimer.singleShot(time_until_next_hour, lambda: self.bme_hour_timer.start(3600000))

        # Calculate time until midnight
        # next_midnight = (now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1))
        # time_until_midnight = (next_midnight - now).total_seconds() * 1000

        # self.bme_day_timer = QTimer(self)
        # self.bme_day_timer.timeout.connect(self.update_daily_data)
        # QTimer.singleShot(time_until_midnight, lambda: self.bme_day_timer.start(86400000))

    def update_clock(self):
        current_time = datetime.now()
        today = date.today()

        self.clock_label.setText(current_time.strftime("%H:%M:%S"))
        self.cur_date_label.setText(f'{today.strftime("%a")}, {today.strftime("%b")} {today.strftime("%d")}')

        # Check if a new hour has started
        if current_time.hour != self.current_hour:
            self.current_hour = current_time.hour
            self.plot_hour_max()

        # Check if a new day has started
        if today != self.current_day:
            self.current_day = today
            self.clear_db()                             # Clear database at end of day to keep db size as small as possible
            # self.plot_day_max()

    def collect_bme_worker(self):
        worker = CollectBMEWorker()
        worker.signals.result.connect(self.null_method)
        worker.signals.error.connect(self.handle_error)
        self.threadpool.start(worker)

    def update_hourly_data(self):
        worker = BMEHourMaxWorker()
        worker.signals.result.connect(self.null_method)
        worker.signals.error.connect(self.handle_error)
        worker.signals.finished.connect(self.plot_hour_max)
        self.threadpool.start(worker)

    # def update_daily_data(self):
    #     self.clear_hourly_data()  # Clear hourly data at midnight
    #     worker = BMEDayMaxWorker()
    #     worker.signals.result.connect(self.null_method)
    #     worker.signals.error.connect(self.handle_error)
    #     worker.signals.finished.connect(self.plot_day_max)
    #     self.threadpool.start(worker)

    def clear_hourly_data(self):
        conn = sqlite3.connect("sensor_data.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM sensor_hour_max")
        conn.commit()
        conn.close()

    def clear_db(self):
        conn = sqlite3.connect("sensor_data.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM sensor_var")
        cursor.execute("DELETE FROM sensor_hour_max")
        conn.commit()
        conn.close()

    @Slot(object)
    def null_method(self, result):
        print(result)

    @Slot()
    def finished_thread(self):
        print("thread finished")

    @Slot(str)
    def handle_error(self, error):  
        print(error)

    @Slot(object)
    def plot_hour_max(self):
        hourly_data = self.db_obj.fetch_hourly_data()
        if not hourly_data:
            print("No hourly data available.")
        else:
            self.plot_data(self.canvas_hourly, hourly_data, "Hourly Data", "Hour", "Max Temp & Humidity")

    # @Slot(object)
    # def plot_day_max(self):
    #     daily_data = self.db_obj.fetch_daily_data()
    #     if not daily_data:
    #         print("No daily data available.")
    #     else:
    #         self.plot_data(self.canvas_daily, daily_data, "Daily Data", "Day", "Max Temp & Humidity")

    def plot_data(self, canvas, data, title, x_label, y_label):
        # Extract times, temperatures, and humidity from data
        times = [datetime.strptime(entry[0], "%Y-%m-%d %H:%M:%S") for entry in data]
        temps = [entry[1] for entry in data]
        humidity = [entry[2] for entry in data]
        
        # Plot the data
        canvas.axes.clear()
        canvas.axes.plot(times, temps, label="Max Temperature", marker='o')
        canvas.axes.plot(times, humidity, label="Max Humidity", marker='o')
        canvas.axes.set_title(title)
        canvas.axes.set_xlabel(x_label)
        canvas.axes.set_ylabel(y_label)
        canvas.axes.legend()
        canvas.axes.grid(True)
        canvas.axes.tick_params(axis='x', rotation=15)

        if title == "Hourly Data":
            # Format the times to display only hours (e.g., 8 AM, 9 AM, ..., 8 PM)
            hour_labels = [time.strftime("%I %p") for time in times]
            # Set the X-axis to the range of hours
            canvas.axes.set_xticks(times)
            canvas.axes.set_xticklabels(hour_labels)

        canvas.draw()


