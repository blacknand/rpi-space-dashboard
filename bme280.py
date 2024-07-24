# import board
# import math
# from adafruit_bme280 import basic as adafruit_bme280
from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QPainter, QPen, QColor, QFont, QPainterPath
from PySide6.QtWidgets import QWidget

# I2C connection
# i2c = board.I2C()
# bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c)
# bme280.sea_level_pressure = 1010                                    # Base calibration point

# b = 17.62
# c = 243.12
# gamma = (b * bme280.temperature / (c + bme280.temperature)) + math.log(bme280.humidity / 100.0)
# dewpoint = format((c * gamma) / (b * gamma), ".2f")

# def bme280_results():
#     temp = bme280.temperature
#     humidity = bme280.relative_humidity
#     pressure = bme280.pressure
#     dew_point = float(dewpoint)
#     return [temp, humidity, pressure, dew_point]


# For testing purposes (BME data only available on R pi) - comment out during deployment
def bme280_results():
    temp = "28"
    pressure = "1250"
    humidity = "40"
    dew_point = "10"
    return [temp, humidity, pressure, dew_point]


# QT Widgets for BME data
class BMEDataWidget(QWidget):
    def __init__(self, label, unit, min_value, max_value, color, start_angle, parent=None):
        super().__init__(parent)
        self.value = 0
        self.label = label
        self.unit = unit
        self.min_value = min_value
        self.max_value = max_value
        self.color = color
        self.start_angle = start_angle
        self.font = QFont("Arial", 12)
        self.setFixedSize(180, 180)
            

    def setValue(self, value):
        self.value = value
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Calculate the dimensions
        rect = QRectF(0, 0, self.width(), self.height())
        center = rect.center()
        radius = min(self.width(), self.height()) / 2 - 20  # Adjust for padding

        # Calculate the percentage
        percentage = (self.value - self.min_value) / (self.max_value - self.min_value)
        total_degrees = 295                                 # Total arc span
        pd = percentage * total_degrees
        rd = total_degrees - pd

        # Draw progress arc
        path, path2 = QPainterPath(), QPainterPath()
        circle_rect = QRectF(center.x() - radius, center.y() - radius, 2 * radius, 2 * radius)

        path.arcMoveTo(circle_rect, self.start_angle)
        path.arcTo(circle_rect, self.start_angle, pd)       # Draw progress in correct direction

        pen, pen2 = QPen(), QPen()
        pen.setCapStyle(Qt.FlatCap)
        pen.setColor(self.get_gradient_color())
        pen_width = self.width() / 25                       # Adjust this value to change the progress bar thickness
        pen.setWidth(pen_width)
        painter.strokePath(path, pen)

        path2.arcMoveTo(circle_rect, self.start_angle)
        path2.arcTo(circle_rect, self.start_angle, -rd)     # Draw remaining arc

        pen2.setWidth(pen_width / 2)                        # Reduced pen width for smaller dashes
        pen2.setColor(QColor("#d7d7d7"))
        pen2.setCapStyle(Qt.FlatCap)
        pen2.setDashPattern([0.2, 0.8])                     # Reduced dash size
        pen2.setDashOffset(2.2)
        painter.strokePath(path2, pen2)

        # Draw description label at the top
        painter.setFont(QFont("Arial", 8))
        painter.setPen(Qt.white)
        painter.drawText(QRectF(center.x() - radius, center.y() - radius * 0.6, 2 * radius, radius / 2), Qt.AlignCenter, self.label)

        # Draw value label in the middle
        painter.setFont(QFont("Arial", 22, QFont.Bold))
        painter.setPen(Qt.white)
        painter.drawText(QRectF(center.x() - radius, center.y() - radius / 4.5, 2 * radius, radius / 2), Qt.AlignCenter, f"{self.value:.2f}")

        # Draw unit label at the bottom
        painter.setFont(QFont("Arial", 12))
        painter.setPen(Qt.white)
        painter.drawText(QRectF(center.x() - radius, center.y() + radius / 5, 2 * radius, radius / 2), Qt.AlignCenter, self.unit)


class TempWidget(BMEDataWidget):
    def __init__(self, parent=None):
        super().__init__(
            label="CABIN TEMP",
            unit="°C",
            min_value=-10,
            max_value=50,
            color=QColor(255, 0, 0),
            start_angle=47.5,
            parent=parent
        )

    def get_gradient_color(self):
        if self.value < 8:
            return QColor(255, 0, 0)        # Red
        elif 8 <= self.value <= 15:
            return QColor(0, 255, 0)        # Green
        elif 16 <= self.value <= 30:
            return QColor(0, 0, 255)        # Blue
        elif 31 <= self.value <= 50:
            return QColor(255, 69, 0)       # Bright Red
        else:
            return QColor(255, 255, 255)    # White for undefined ranges


class HumidityWidget(BMEDataWidget):
    def __init__(self, parent=None):
        super().__init__(
            label="CABIN HUMIDITY",
            unit="%",
            min_value=0,
            max_value=100,
            color=QColor(255, 0, 0),
            start_angle=95,
            parent=parent
        )

    def get_gradient_color(self):
        if self.value < 20:
            return QColor(225, 8, 33)
        elif 20 <= self.value <= 60:
            return QColor(123, 225, 8) 
        elif 61 <= self.value <= 100:
            return QColor(105, 174, 255)
        else:
            return QColor(255, 255, 255)    
        

class PressureWidget(BMEDataWidget):
    def __init__(self, parent=None):
        super().__init__(
            label="ATMOS PRESSURE",
            unit="hPa %",
            min_value=0,
            max_value=5000,
            color=QColor(255, 0, 0),
            start_angle=177.5,
            parent=parent
        )

    def get_gradient_color(self):
        if self.value < 1000:
            return QColor(225, 8, 33)
        elif 1001 <= self.value <= 1500:
            return QColor(123, 225, 8) 
        elif 1501 <= self.value <= 5000:
            return QColor(105, 174, 255)
        else:
            return QColor(255, 255, 255)
        

class DewPointWidget(BMEDataWidget):
    def __init__(self, parent=None):
        super().__init__(
            label="DEW POINT",
            unit="°C",
            min_value=0,
            max_value=100,
            color=QColor(255, 0, 0),
            start_angle=197.5,
            parent=parent
        )

    def get_gradient_color(self):
        if self.value < 50:
            return QColor(123, 225, 8)
        elif 51 <= self.value <= 60:
            return QColor(123, 225, 8) 
        elif 61 <= self.value <= 70:
            return QColor(105, 174, 255)
        elif 71 <= self.value <= 100:
            return QColor(255, 0, 0)
        else:
            return QColor(255, 255, 255)    