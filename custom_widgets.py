from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout
from PySide6.QtCore import Qt


class DragonImageWidget(QWidget):
    def __init__(self, width=None, height=None):
        super().__init__()
        self.label = QLabel(self)
        image = QPixmap("images/spacex_images/file.png")

        if width is not None and height is not None:
            image = image.scaled(width, height, Qt.KeepAspectRatio)

        self.label.setPixmap(image)
        self.layout = QHBoxLayout(self)
        self.layout.addWidget(self.label)
        self.resize(image.width(), image.height())