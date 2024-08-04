import sqlite3
from datetime import datetime, timedelta

class DBOperations:
    def db_config(self, filename, conn, encoding='utf-8'):
        try:
            with open(filename, 'r', encoding=encoding) as f:
                sql_script = f.read()
            
            cursor = conn.cursor()
            cursor.executescript(sql_script)
            conn.commit()
        except Exception as e:
            print(f"An error occurred while executing the SQL script: {e}")
            raise

    def setup_db(self, filename="sensor_setup.sql", encoding='utf-8'):
        try:
            conn = sqlite3.connect("sensor_data.db")
            self.db_config(filename, conn, encoding)
            conn.close()
        except Exception as e:
            print(f"An error occurred while setting up the database: {e}")
            raise

    def delete_old_entries(self, conn):
        try:
            cursor = conn.cursor()
            two_weeks_ago = datetime.now() - timedelta(weeks=2)
            two_weeks_ago_str = two_weeks_ago.strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute("DELETE FROM sensor_var WHERE timestamp < ?", (two_weeks_ago_str,))
            cursor.execute("DELETE FROM sensor_hour_max WHERE hour < ?", (two_weeks_ago_str,))
            cursor.execute("DELETE FROM sensor_day_max WHERE day < ?", (two_weeks_ago_str,))
            conn.commit()
            print(f"Deleted entries older than {two_weeks_ago_str}.")
        except Exception as e:
            print(f"An error occurred while deleting old entries: {e}")
            raise

    def fetch_hourly_data(self):
        conn = sqlite3.connect("sensor_data.db")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT hour, max_temp, max_humidity 
            FROM sensor_hour_max 
            WHERE strftime('%H', hour) BETWEEN '08' AND '20'
        """)
        data = cursor.fetchall()
        conn.close()
        return data

    def fetch_daily_data(self):
        conn = sqlite3.connect("sensor_data.db")
        cursor = conn.cursor()
        cursor.execute("SELECT day, max_temp, max_humidity FROM sensor_day_max")
        data = cursor.fetchall()
        conn.close()
        return data

    def clear_database(self):
        conn = sqlite3.connect("sensor_data.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM sensor_var")
        cursor.execute("DELETE FROM sensor_hour_max")
        cursor.execute("DELETE FROM sensor_day_max")
        conn.commit()
        conn.close()
