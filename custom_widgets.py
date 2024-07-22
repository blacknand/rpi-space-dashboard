from PySide6.QtGui import QPixmap, QAction, QIcon, QColor
from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout, QStatusBar, QToolBar, QPushButton, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QGraphicsDropShadowEffect, QVBoxLayout, QFrame
from PySide6.QtCore import Qt, QTimer, QRectF, QSize
from datetime import datetime, date


class DragonImageWidget(QWidget):
    def __init__(self, width=None, height=None):
        super().__init__()

        image = QPixmap("images/spacex_images/file.png")

        if width is not None and height is not None:
            image = image.scaled(width, height, Qt.KeepAspectRatio)

        # Create a QGraphicsScene
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene, self)

        # Create a QGraphicsPixmapItem with the image
        capsule_item = QGraphicsPixmapItem(image)

        # Create the shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(50)
        shadow.setColor(QColor(255, 255, 255, 160))  # White glow
        shadow.setOffset(0, 0)

        # Apply the shadow effect to the pixmap item
        capsule_item.setGraphicsEffect(shadow)

        # Add the pixmap item to the scene
        self.scene.addItem(capsule_item)

        # Set the scene rectangle to fit the pixmap item
        self.scene.setSceneRect(QRectF(image.rect()))

        # Set up the layout
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.view)

        # Resize the view to fit the scene
        self.view.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)

        # Resize the widget to fit the view
        self.resize(image.width(), image.height())


class HeaderWidget(QWidget):
    # Header widget with title, date and time
    def __init__(self):
        super().__init__()

        self.layout = QHBoxLayout(self)

        self.header_title = QLabel("CABIN OVERVIEW")
        today = date.today()
        self.formatted_cur_date = f'{today.strftime("%a")}, {today.strftime("%b")} {today.strftime("%d")}'
        self.current_time = datetime.now().strftime("%H:%M:%S")
        self.date_label = QLabel(self.formatted_cur_date)
        self.time_label = QLabel(self.current_time)

        self.layout.addWidget(self.date_label)
        self.layout.addWidget(self.header_title)
        self.layout.addWidget(self.time_label)

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

        self.setMinimumHeight(100)

        self.setStyleSheet("""
            QWidget#footerButtonsWidget {
                border-top: 2px solid white;
                border-right: 2px solid white;
                border-left: 2px solid white;
            }
        """)

    def create_icon_button(self, icon_path):
        button = QPushButton()
        button.setIcon(QIcon(icon_path))
        button.setIconSize(QSize(64, 64))
        button.setFixedSize(80, 80)
        button.setStyleSheet("QPushButton { background-color: transparent; border: none; }")
        return button