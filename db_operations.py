import sqlite3
from custom_widgets import WorkerSignals
from PySide6.QtCore import QRunnable, Slot
from bme280 import bme280_results
from datetime import datetime, timedelta
import pandas as pd

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

class DBOperations:
    def db_config(self, filename, conn):
        with open(filename, 'r') as f:
            sql_script = f.read()

        cursor = conn.cursor()
        cursor.executescript(sql_script)
        conn.commit()

    def setup_db(self):
        conn = sqlite3.connect("sensor_data.db")
        self.db_config("sensor_setup.sql")
        conn.close()