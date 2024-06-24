from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.properties import Builder
from bme280 import bme280_results

class BME280App(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        bme_results = bme280_results()
        self.bme_temp = bme_results[0]
        self.bme_humidity = bme_results[1]
        self.bme_pressure = bme_results[2]
        self.bme_altitude = bme_results[3]
        self.bme_dew_point = bme_results[-1]

    def build(self):
        self.label = Label(text=str(self.bme_temp))
        Clock.schedule_interval(self.update_temp, 1)
        return self.label
    
    def update_temp(self, dt):
        bme_results = bme280_results()
        self.bme_temp = bme_results[0]
        self.label.text = str(self.bme_temp)

    
if __name__ == "__main__":
    BME280App().run()