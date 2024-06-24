from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from bme280 import bme280_results
from kivy.core.window import Window

class BME280App(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        bme_results = bme280_results()
        self.bme_temp = f"TMP: {bme_results[0]}"
        self.bme_humidity = f"RM: {bme_results[1]}"
        self.bme_pressure = f"Pb: {bme_results[2]}"
        self.bme_altitude = f"ALT: {bme_results[3]}"
        self.bme_dew_point = f"DWPNT: {bme_results[-1]}"
        self.bme_temp_label = Label(text=str(self.bme_temp))
        self.bme_humidity_label = Label(text=str(self.bme_humidity))
        self.bme_pressure_label = Label(text=str(self.bme_pressure))
        self.bme_altitude_label = Label(text=str(self.bme_altitude))
        self.bme_dewpoint_label = Label(text=str(self.bme_dew_point))

    def build(self):
        Window.show_cursor = False
        layout = BoxLayout(orientation='horizontal')
        layout.add_widget(self.bme_temp_label)
        layout.add_widget(self.bme_humidity_label)
        layout.add_widget(self.bme_pressure_label)
        layout.add_widget(self.bme_altitude_label)
        layout.add_widget(self.bme_dewpoint_label)
        Clock.schedule_interval(self.update_bme_data, 1)
        return layout
    
    def update_bme_data(self, dt):
        bme_results = bme280_results()
        self.bme_temp = f"TMP: {bme_results[0]}"
        self.bme_humidity = f"RM: {bme_results[1]}"
        self.bme_pressure = f"Pb: {bme_results[2]}"
        self.bme_altitude = f"ALT: {bme_results[3]}"
        self.bme_dew_point = f"DWPNT: {bme_results[-1]}"
        self.bme_temp_label.text = str(self.bme_temp)
        self.bme_humidity_label = str(self.bme_humidity)
        self.bme_pressure_label = str(self.bme_pressure)
        self.bme_altitude_label = str(self.bme_altitude)
        self.bme_dewpoint_label = str(self.bme_dew_point)

    
if __name__ == "__main__":
    BME280App().run()
