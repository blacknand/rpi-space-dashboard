import sqlite3

class DBOperations:
    def db_config(self, filename, conn):
        with open(filename, 'r') as f:
            sql_script = f.read()

        cursor = conn.cursor()
        cursor.executescript(sql_script)
        conn.commit()

    def setup_db(self):
        conn = sqlite3.connect("sensor_data.db")
        self.db_config("sensor_setup.sql", conn)
        conn.close()