from datetime import datetime, date
from PySide6.QtGui import QPixmap,QIcon, QColor, QPolygon, QPainter, QRegion
from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout, QPushButton, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QGraphicsDropShadowEffect, QVBoxLayout
from PySide6.QtCore import Qt, QTimer, QRectF, QSize, QPoint
from PySide6.QtWidgets import QWidget, QGraphicsScene, QGraphicsView, QGraphicsPixmapItem, QVBoxLayout, QGraphicsDropShadowEffect
from PySide6.QtGui import QPixmap, QColor, QFont
from PySide6.QtCore import Qt, QRectF


class DragonImageWidget(QWidget):
    def __init__(self, width=None, height=None):
        super().__init__()

        self.image_path = "images/spacex_images/file.png" 
        self.image = QPixmap(self.image_path)

        if width is None or height is None:
            width = self.image.width()
            height = self.image.height()

        self.desired_width = width
        self.desired_height = height

        # Create a QGraphicsScene
        self.scene = QGraphicsScene(self)
        self.view = QGraphicsView(self.scene, self)
        self.view.setStyleSheet("background: transparent; border: none;") 

        self.capsule_item = QGraphicsPixmapItem(self.image)

        # Create the shadow effect to simulate the bottom glow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(50)
        shadow.setColor(QColor(255, 255, 255, 160))             # White glow
        shadow.setOffset(0, 20)                                 # Set shadow offset for more emphasis on the bottom
        self.capsule_item.setGraphicsEffect(shadow)
        self.scene.addItem(self.capsule_item)

        # Set up the layout
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.view)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.resize_image(width, height)

    def resize_image(self, width, height):
        self.image = QPixmap(self.image_path).scaled(width, height, Qt.KeepAspectRatio)
        self.capsule_item.setPixmap(self.image)
        self.scene.setSceneRect(QRectF(self.image.rect()))
        self.view.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)
        self.resize(width, height)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.resize_image(self.width(), self.height())
        
    def sizeHint(self):
        return QSize(self.desired_width, self.desired_height)



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

        self.date_label.setFont(QFont("Arial", 18))
        self.time_label.setFont(QFont("Arial", 18))
        self.header_title.setFont(QFont("Arial", 14))

        self.layout.addStretch()
        self.layout.addWidget(self.date_label)
        self.layout.addStretch()
        self.layout.addWidget(self.header_title)
        self.layout.addStretch()
        self.layout.addWidget(self.time_label)
        self.layout.addStretch()

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
        self.rover_button = self.create_icon_button("images/nasa_images/rover-button-icon.png")
        self.spacex_button = self.create_icon_button("images/spacex_images/spacex-button-icon.png")

        layout.addWidget(self.dragon_button)
        layout.addWidget(self.fh_button)
        layout.addWidget(self.apod_button)
        layout.addWidget(self.rover_button)
        layout.addWidget(self.spacex_button)

        self.setMinimumHeight(60)
        self.setMinimumWidth(400)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)           # Required to apply style sheet on QWidget
        self.setStyleSheet("""
            QWidget#footerButtonsWidget {
                background-color: #000000;
            }
        """)

    def create_icon_button(self, icon_path):
        button = QPushButton()
        button.setIcon(QIcon(icon_path))
        button.setIconSize(QSize(40, 40))
        button.setFixedSize(40, 40)
        button.setStyleSheet("QPushButton { background-color: transparent; border: none; }")
        return button
    
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
        painter.setBrush(QColor("#000000"))
        painter.setPen(Qt.NoPen)                # Remove the border
        painter.drawPolygon(trapezoid)

        # Apply the shape to the widget
        region = QRegion(trapezoid)
        self.setMask(region)
        