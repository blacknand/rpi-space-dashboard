import sqlite3

class DBOperations:
    def db_config(self, filename, conn):
        try:
            with open(filename, 'r') as f:
                sql_script = f.read()
            
            cursor = conn.cursor()
            cursor.executescript(sql_script)
            conn.commit()
        except Exception as e:
            print(f"An error occurred while executing the SQL script: {e}")
            raise

    def setup_db(self, filename="sensor_setup.sql"):
        try:
            conn = sqlite3.connect("sensor_data.db")
            self.db_config(filename, conn)
            conn.close()
        except Exception as e:
            print(f"An error occurred while setting up the database: {e}")
            raise
