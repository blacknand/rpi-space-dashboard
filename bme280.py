import time
import math
# import board
# from adafruit_bme280 import basic as adafruit_bme280
from PySide6.QtCore import Qt, QTimer, QRectF, QPointF
from PySide6.QtGui import QKeyEvent, QPainter, QPen, QColor, QFont, QPainterPath
from PySide6.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget, QMainWindow

# I2C connection
# i2c = board.I2C()
# bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c)
# bme280.sea_level_pressure = 1010                                    # Base calibration point

# b = 17.62
# c = 243.12
# gamma = (b * bme280.temperature / (c + bme280.temperature)) + math.log(bme280.humidity / 100.0)
# dewpoint = format((c * gamma) / (b * gamma), ".2f")

# def bme280_results():
#     temp = ("%0.1f" % bme280.temperature)
#     humidity = ("%0.1f %%" % bme280.relative_humidity)
#     pressure = ("%0.1f" % bme280.pressure)
#     dew_point = f"{dewpoint}"
#     return [temp, humidity, pressure, dew_point]

# For testing purposes (BME data only available on R pi) - comment out during deployment
# def bme280_results():
#     temp = "28"
#     pressure = "1250"
#     humidity = "40"
#     dew_point = "10"
#     return [temp, pressure, humidity, dew_point]


# QT Widgets for BME data
class TempWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.value = 0
        self.max_value = 50         # Most is 50 °C
        self.min_value = -10        # Least is -10 °C
        self.unit = "°C"
        self.label = "CABIN TEMP"
        self.start_color = QColor(0, 0, 255)        # Blue
        self.end_color = QColor(255, 0, 0)          # Red
        self.font = QFont("Arial", 15)
        self.setFixedSize(300, 300) 


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
        total_degrees = 295  # Total arc span
        pd = percentage * total_degrees
        rd = total_degrees - pd

        # Draw progress arc
        path, path2 = QPainterPath(), QPainterPath()
        circle_rect = QRectF(center.x() - radius, center.y() - radius, 2 * radius, 2 * radius)

        # Beginning of arc
        start_angle = 50  
        path.arcMoveTo(circle_rect, start_angle)
        path.arcTo(circle_rect, start_angle, pd) 
        pen, pen2 = QPen(), QPen()
        pen.setCapStyle(Qt.FlatCap)
        pen.setColor(self.get_gradient_color())
        pen_width = self.width() / 40
        pen.setWidth(pen_width)
        painter.strokePath(path, pen)

        # End of arc
        path2.arcMoveTo(circle_rect, start_angle)
        path2.arcTo(circle_rect, start_angle, -rd)
        pen2.setWidth(pen_width / 2)
        pen2.setColor(QColor("#d7d7d7"))
        pen2.setCapStyle(Qt.FlatCap)
        pen2.setDashPattern([0.2, 0.8])
        pen2.setDashOffset(2.2)
        painter.strokePath(path2, pen2)

        # Draw description label at the top
        painter.setFont(QFont("Arial", 15))
        painter.setPen(Qt.white)
        painter.drawText(QRectF(center.x() - radius, center.y() - radius * 0.6, 2 * radius, radius / 2), Qt.AlignCenter, self.label)

        # Draw temperature label in the middle
        painter.setFont(QFont("Arial", 40, QFont.Bold))
        painter.setPen(Qt.white)
        painter.drawText(QRectF(center.x() - radius, center.y() - radius / 4, 2 * radius, radius / 2), Qt.AlignCenter, f"{self.value:.2f}")

        # Draw unit label at the bottom
        painter.setFont(QFont("Arial", 20))
        painter.setPen(Qt.white)
        painter.drawText(QRectF(center.x() - radius, center.y() + radius / 6, 2 * radius, radius / 2), Qt.AlignCenter, self.unit)

    def get_gradient_color(self):
        # Determine color based on temperature value
        if self.value < 10:
            return QColor(225, 8, 33)
        elif 10 <= self.value <= 18:
            return QColor(123, 225, 8) 
        elif 19 <= self.value <= 30:
            return QColor(105, 174, 255)
        elif 31 <= self.value <= 50:
            return QColor(255, 0, 0)
        else:
            return QColor(255, 255, 255)
        

class HumidityWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.value = 0
        self.max_value = 100    
        self.min_value = 0       
        self.unit = "%"
        self.label = "CABIN HUMIDITY"
        self.start_color = QColor(0, 0, 255)        # Blue
        self.end_color = QColor(255, 0, 0)          # Red
        self.font = QFont("Arial", 15)
        self.setFixedSize(300, 300) 


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
        total_degrees = 295  # Total arc span
        pd = percentage * total_degrees
        rd = total_degrees - pd

        # Draw progress arc
        path, path2 = QPainterPath(), QPainterPath()
        circle_rect = QRectF(center.x() - radius, center.y() - radius, 2 * radius, 2 * radius)

        # Beginning of arc
        start_angle = 240
        path.arcMoveTo(circle_rect, start_angle)
        path.arcTo(circle_rect, start_angle, pd) 
        pen, pen2 = QPen(), QPen()
        pen.setCapStyle(Qt.FlatCap)
        pen.setColor(self.get_gradient_color())
        pen_width = self.width() / 40
        pen.setWidth(pen_width)
        painter.strokePath(path, pen)

        # End of arc
        path2.arcMoveTo(circle_rect, start_angle)
        path2.arcTo(circle_rect, start_angle, -rd)
        pen2.setWidth(pen_width / 2)
        pen2.setColor(QColor("#d7d7d7"))
        pen2.setCapStyle(Qt.FlatCap)
        pen2.setDashPattern([0.2, 0.8])
        pen2.setDashOffset(2.2)
        painter.strokePath(path2, pen2)

        # Draw description label at the top
        painter.setFont(QFont("Arial", 15))
        painter.setPen(Qt.white)
        painter.drawText(QRectF(center.x() - radius, center.y() - radius * 0.6, 2 * radius, radius / 2), Qt.AlignCenter, self.label)

        # Draw temperature label in the middle
        painter.setFont(QFont("Arial", 40, QFont.Bold))
        painter.setPen(Qt.white)
        painter.drawText(QRectF(center.x() - radius, center.y() - radius / 4, 2 * radius, radius / 2), Qt.AlignCenter, f"{self.value:.2f}")

        # Draw unit label at the bottom
        painter.setFont(QFont("Arial", 20))
        painter.setPen(Qt.white)
        painter.drawText(QRectF(center.x() - radius, center.y() + radius / 6, 2 * radius, radius / 2), Qt.AlignCenter, self.unit)

    def get_gradient_color(self):
        # Determine color based on temperature value
        if self.value < 20:
            return QColor(225, 8, 33)
        elif 20 <= self.value <= 60:
            return QColor(123, 225, 8) 
        elif 61 <= self.value <= 100:
            return QColor(105, 174, 255)
        else:
            return QColor(255, 255, 255)
        

class PressureWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.value = 0
        self.max_value = 9999    
        self.min_value = 0       
        self.unit = "%"
        self.label = "ATMOS PRESSURE"
        self.start_color = QColor(0, 0, 255)        # Blue
        self.end_color = QColor(255, 0, 0)          # Red
        self.font = QFont("Arial", 15)
        self.setFixedSize(300, 300) 


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
        total_degrees = 295  # Total arc span
        pd = percentage * total_degrees
        rd = total_degrees - pd

        # Draw progress arc
        path, path2 = QPainterPath(), QPainterPath()
        circle_rect = QRectF(center.x() - radius, center.y() - radius, 2 * radius, 2 * radius)

        # Beginning of arc
        start_angle = 240
        path.arcMoveTo(circle_rect, start_angle)
        path.arcTo(circle_rect, start_angle, pd) 
        pen, pen2 = QPen(), QPen()
        pen.setCapStyle(Qt.FlatCap)
        pen.setColor(self.get_gradient_color())
        pen_width = self.width() / 40
        pen.setWidth(pen_width)
        painter.strokePath(path, pen)

        # End of arc
        path2.arcMoveTo(circle_rect, start_angle)
        path2.arcTo(circle_rect, start_angle, -rd)
        pen2.setWidth(pen_width / 2)
        pen2.setColor(QColor("#d7d7d7"))
        pen2.setCapStyle(Qt.FlatCap)
        pen2.setDashPattern([0.2, 0.8])
        pen2.setDashOffset(2.2)
        painter.strokePath(path2, pen2)

        # Draw description label at the top
        painter.setFont(QFont("Arial", 15))
        painter.setPen(Qt.white)
        painter.drawText(QRectF(center.x() - radius, center.y() - radius * 0.6, 2 * radius, radius / 2), Qt.AlignCenter, self.label)

        # Draw temperature label in the middle
        painter.setFont(QFont("Arial", 40, QFont.Bold))
        painter.setPen(Qt.white)
        painter.drawText(QRectF(center.x() - radius, center.y() - radius / 4, 2 * radius, radius / 2), Qt.AlignCenter, f"{self.value:.2f}")

        # Draw unit label at the bottom
        painter.setFont(QFont("Arial", 20))
        painter.setPen(Qt.white)
        painter.drawText(QRectF(center.x() - radius, center.y() + radius / 6, 2 * radius, radius / 2), Qt.AlignCenter, self.unit)

    def get_gradient_color(self):
        # Determine color based on temperature value
        if self.value < 1000:
            return QColor(225, 8, 33)
        elif 1001 <= self.value <= 1500:
            return QColor(123, 225, 8) 
        elif 1501 <= self.value <= 9999:
            return QColor(105, 174, 255)
        else:
            return QColor(255, 255, 255)
        

class DewPointWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.value = 0
        self.max_value = 0   
        self.min_value = 100  
        self.unit = "°C"
        self.label = "DEW POINT"
        self.start_color = QColor(0, 0, 255)        # Blue
        self.end_color = QColor(255, 0, 0)          # Red
        self.font = QFont("Arial", 15)
        self.setFixedSize(300, 300) 


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
        total_degrees = 295  # Total arc span
        pd = percentage * total_degrees
        rd = total_degrees - pd

        # Draw progress arc
        path, path2 = QPainterPath(), QPainterPath()
        circle_rect = QRectF(center.x() - radius, center.y() - radius, 2 * radius, 2 * radius)

        # Beginning of arc
        start_angle = 302.5
        path.arcMoveTo(circle_rect, start_angle)
        path.arcTo(circle_rect, start_angle, pd) 
        pen, pen2 = QPen(), QPen()
        pen.setCapStyle(Qt.FlatCap)
        pen.setColor(self.get_gradient_color())
        pen_width = self.width() / 40
        pen.setWidth(pen_width)
        painter.strokePath(path, pen)

        # End of arc
        path2.arcMoveTo(circle_rect, start_angle)
        path2.arcTo(circle_rect, start_angle, -rd)
        pen2.setWidth(pen_width / 2)
        pen2.setColor(QColor("#d7d7d7"))
        pen2.setCapStyle(Qt.FlatCap)
        pen2.setDashPattern([0.2, 0.8])
        pen2.setDashOffset(2.2)
        painter.strokePath(path2, pen2)

        # Draw description label at the top
        painter.setFont(QFont("Arial", 15))
        painter.setPen(Qt.white)
        painter.drawText(QRectF(center.x() - radius, center.y() - radius * 0.6, 2 * radius, radius / 2), Qt.AlignCenter, self.label)

        # Draw temperature label in the middle
        painter.setFont(QFont("Arial", 40, QFont.Bold))
        painter.setPen(Qt.white)
        painter.drawText(QRectF(center.x() - radius, center.y() - radius / 4, 2 * radius, radius / 2), Qt.AlignCenter, f"{self.value:.2f}")

        # Draw unit label at the bottom
        painter.setFont(QFont("Arial", 20))
        painter.setPen(Qt.white)
        painter.drawText(QRectF(center.x() - radius, center.y() + radius / 6, 2 * radius, radius / 2), Qt.AlignCenter, self.unit)

    def get_gradient_color(self):
        # Determine color based on temperature value
        if self.value < 50:
            return QColor(225, 8, 33)
        elif 51 <= self.value <= 60:
            return QColor(123, 225, 8) 
        elif 61 <= self.value <= 70:
            return QColor(105, 174, 255)
        elif 71 <= self.value <= 100:
            return QColor(255, 0, 0)
        else:
            return QColor(255, 255, 255)