import requests
import sqlite3
import json
import os
import pandas as pd
from PySide6.QtCore import QRunnable, Signal, QObject, Slot
from datetime import datetime, timedelta
from bme280 import bme280_results

class WorkerSignals(QObject):
    result = Signal(object)
    error = Signal(str)
    finished = Signal()

    def __init__(self):
        super().__init__()


class RocketLaunchAPIWorker(QRunnable):
    # Handles LL2 API request in seperate thread
    def __init__(self, url):
        super().__init__()
        self.url = url
        self.signals = WorkerSignals()

    @Slot()
    def run(self):
        try:
            response = requests.get(self.url)
            response.raise_for_status()
            self.signals.result.emit(response.json())  # Emit API response
        except requests.RequestException as e:
            self.signals.error.emit(f"Error: {e}\nError querying {self.url}")
        finally:
            self.signals.finished.emit()
            if response:
                response.close()


class ImageDownloadWorker(QRunnable):
    def __init__(self, url):
        super().__init__()
        self.url = url
        self.signals = WorkerSignals()

    @Slot()
    def run(self):
        try:
            # Headers required for images from Wikimedia
            headers = {'User-Agent': 'RpiSpaceDashboard/0.0 (https://github.com/blacknand/rpi-space-dashboard; nblackburndeveloper@icloud.com)'}
            response = requests.get(self.url, headers=headers)
            response.raise_for_status()
            image_data = response.content
            self.signals.result.emit(image_data)
        except requests.RequestException as e:
            self.signals.error.emit(f"Error: {e}\nError downloading {self.url}")
        finally:
            self.signals.finished.emit()
            if response:
                response.close()


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


# ---------- BME temperature and humidity workers ---------- #
class CollectBMEWorker(QRunnable):
    def __init__(self):
        super().__init__()
        self.signals = WorkerSignals()

    @Slot()
    def collect_bme_data(self):
        bme_data = bme280_results()
        temp = bme_data[0]
        humidity = bme_data[1]
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if isinstance(temp, float) and isinstance(humidity, float):
            conn = sqlite3.connect("sensor_data.db")
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO sensor.var (timestamp, temp, humidity)
                VALUES (?, ?, ?)
            """, (timestamp, temp, humidity))
            conn.commit()
            cursor.close()
        else:
            print("BME sensor has fallen off breadboard")


class BMEHourMaxWorker(QRunnable):
    def __init__(self):
        super().__init__()
        self.signals = WorkerSignals()

    @Slot()
    def calculate_hour_max(self):
        conn = sqlite3.connect("sensor_data.db")
        df = pd.read_sql_query("""
            SELECT *
            FROM sensor.var
        """, conn, parse_dates=["timestamp"])
        last_hour = df[df["timestamp"] > (datetime.now() - timedelta(hours=1))]
        if not last_hour.empty:
            max_temp = last_hour["temp"].max()
            max_humidity = last_hour["humidity"].max()
            hour = datetime.now().strftime("%Y-%m-%d %H:00:00")
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO sensor.hour_max (hour, max_temp, max_humidity)
                VALUES (?, ?, ?)
            """, (hour, max_temp, max_humidity))
            conn.commit()
        conn.close()


class BMEDayMaxWorker(QRunnable):
    def __init__(self):
        super().__init__()
        self.signals = WorkerSignals()

    @Slot()
    def calculate_day_max(self):
        conn = sqlite3.connect("sensor_data.db")
        df = pd.read_sql_query("""
            SELECT *
            FROM sensor.hour_max
        """, conn, parse_dates=["hour"])
        last_day = df[df["hour"] > (datetime.now() - timedelta(days=1))]
        if not last_day.empty:
            max_temp = last_day["max_temp"].max()
            max_humidity = last_day["max_humidity"].max()
            day = datetime.now().strftime("%Y-%m-%d")
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO sensor.day_max (day, max_temp, max_humidity)
                VALUES (?, ?, ?)
            """, (day, max_temp, max_humidity))
            conn.commit()
        conn.close()
# ---------- BME temperature and humidity workers ---------- #
    