from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from time_data import formatted_cur_date, current_time
from bme280 import bme280_results

class BME280App(App):
    def __init__(self, bme_results):
        self.bme280_results = bme_results
        self.bme_temp = bme280_results[0]
        self.bme_humidity = bme280_results[1]
        self.bme_pressure = bme280_results[2]
        self.bme_altitude = bme280_results[3]
        self.bme_dew_point = bme280_results[-1]

    def build(self):
        label = Label(text=self.bme_temp)

    
if __name__ == "__main__":
    BuildApp(bme280_results()).run()
