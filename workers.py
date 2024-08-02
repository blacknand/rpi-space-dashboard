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


# TODO: Replace all instances with APIWorker instead of current name
class APIWorker(QRunnable):
    def __init__(self, url):
        super().__init__()
        self.url = url
        self.signals = WorkerSignals()

    @Slot()
    def run(self):
        try:
            print(f"APIWorker thread started @ [{self.url}]")
            response = requests.get(self.url)
            response.raise_for_status()
            self.signals.result.emit(response.json()) 
        except requests.RequestException as e:
            self.signals.error.emit(f"APIWorker encountered error [{e}] while querying [{self.url}]")
        finally:
            self.signals.finished.emit()
            print(f"APIWorker thread finished @ [{self.url}]")
            if response:
                response.close()


class ImageDownloadWorker(QRunnable):
    def __init__(self, url):
        super().__init__()
        self.url = url
        self.signals = WorkerSignals()

    @Slot()
    def run(self):
        response = None
        try:
            print(f"ImageDownloadWorker thread started @ [{self.url}]")
            # Headers required for images from Wikimedia
            headers = {'User-Agent': 'RpiSpaceDashboard/0.0 (https://github.com/blacknand/rpi-space-dashboard; nblackburndeveloper@icloud.com)'}
            response = requests.get(self.url, headers=headers)
            response.raise_for_status()
            image_data = response.content
            self.signals.result.emit(image_data)
        except requests.RequestException as e:
            self.signals.error.emit(f"ImageDownloadWorker encountered error [{e}] while downloading [{self.url}]")
        finally:
            self.signals.finished.emit()
            if response:
                response.close()
            print(f"ImageDownloadWorker thread finished @ [{self.url}]")


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
            self.signals.error.emit(f"APODWorker error [{e}]")
        finally:
            self.signals.finished.emit()


# ---------- BME temperature and humidity workers ---------- #
class CollectBMEWorker(QRunnable):
    def __init__(self):
        super().__init__()
        self.signals = WorkerSignals()

    @Slot()
    def run(self):
        try:
            bme_data = bme280_results()
            temp = bme_data[0]
            humidity = bme_data[1]
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"temp, humidity type: {type(temp), type(humidity)}")
            if isinstance(temp, float) and isinstance(humidity, float):
                print("Collecting BME data and storing it in the database")
                conn = sqlite3.connect("sensor_data.db")
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO sensor_var (timestamp, temp, humidity)
                    VALUES (?, ?, ?)
                """, (timestamp, temp, humidity))
                conn.commit()
                cursor.close()
                conn.close()
                self.signals.result.emit("BME data collected and stored successfully")
            else:
                error_message = "BME sensor has returned either invalid or no data. Check to see if the sensor has falled off the breadboard."
                self.signals.error.emit(error_message)
        except Exception as e:
            self.signals.error.emit(str(e))
        finally:
            self.signals.finished.emit()


class BMEHourMaxWorker(QRunnable):
    def __init__(self):
        super().__init__()
        self.signals = WorkerSignals()

    @Slot()
    def run(self):
        try:
            conn = sqlite3.connect("sensor_data.db")
            df = pd.read_sql_query("""
                SELECT *
                FROM sensor_var
            """, conn, parse_dates=["timestamp"])
            last_hour = df[df["timestamp"] > (datetime.now() - timedelta(hours=1))]
            if not last_hour.empty:
                max_temp = last_hour["temp"].max()
                max_humidity = last_hour["humidity"].max()
                hour = datetime.now().strftime("%Y-%m-%d %H:00:00")
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO sensor_hour_max (hour, max_temp, max_humidity)
                    VALUES (?, ?, ?)
                """, (hour, max_temp, max_humidity))
                conn.commit()
                self.signals.result.emit("finished")
            conn.close()
        except Exception as e:
            self.signals.error.emit(e)
        finally:
            self.signals.finished.emit("finished max hour worker")


class BMEDayMaxWorker(QRunnable):
    def __init__(self):
        super().__init__()
        self.signals = WorkerSignals()

    @Slot()
    def run(self):
        try:
            conn = sqlite3.connect("sensor_data.db")
            df = pd.read_sql_query("""
                SELECT *
                FROM sensor_hour_max
            """, conn, parse_dates=["hour"])
            last_day = df[df["hour"] > (datetime.now() - timedelta(days=1))]
            if not last_day.empty:
                max_temp = last_day["max_temp"].max()
                max_humidity = last_day["max_humidity"].max()
                day = datetime.now().strftime("%Y-%m-%d")
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO sensor_day_max (day, max_temp, max_humidity)
                    VALUES (?, ?, ?)
                """, (day, max_temp, max_humidity))
                conn.commit()
                self.signals.result.emit("hour max worker complete")
            conn.close()
        except Exception as e:
            self.signals.erorr.emit(e)
        finally:
            self.signals.result.emit("day max worker finished")
# ---------- BME temperature and humidity workers ---------- #
    