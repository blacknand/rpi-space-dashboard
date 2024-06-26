from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from bme280 import bme280_results
from kivy.core.window import Window
from time_data import current_time, formatted_cur_date

class BME280App(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        bme_results = bme280_results()
        self.bme_temp = f"TMP: {bme_results[0]}"
        self.bme_humidity = f"RM: {bme_results[1]}"
        self.bme_pressure = f"Pb: {bme_results[2]}"
        self.bme_dew_point = f"DWPNT: {bme_results[-1]}"
        self.bme_temp_label = Label(text=str(self.bme_temp))
        self.bme_humidity_label = Label(text=str(self.bme_humidity))
        self.current_time_label = Label(text=str(current_time))
        self.formatted_cur_date_label = Label(text=str(formatted_cur_date))
        self.bme_pressure_label = Label(text=str(self.bme_pressure))
        self.bme_dewpoint_label = Label(text=str(self.bme_dew_point))

    def build(self):
        Window.show_cursor = False
        layout = BoxLayout(orientation='horizontal')
        layout.add_widget(self.bme_temp_label)
        layout.add_widget(self.bme_humidity_label)
        layout.add_widget(self.current_time_label)
        layout.add_widget(self.current_time_label)
        layout.add_widget(self.bme_pressure_label)
        layout.add_widget(self.bme_dewpoint_label)
        Clock.schedule_interval(self.update_bme_data, 1)
        return layout
    
    def update_bme_data(self, dt):
        bme_results = bme280_results()
        self.bme_temp = f"TMP: {bme_results[0]}"
        self.bme_humidity = f"RM: {bme_results[1]}"
        self.current_time_label = Label(text=str(current_time))
        self.formatted_cur_date_label = Label(text=str(formatted_cur_date))
        self.bme_pressure = f"Pb: {bme_results[2]}"
        self.bme_dew_point = f"DWPNT: {bme_results[-1]}"
        self.bme_temp_label.text = str(self.bme_temp)
        self.bme_humidity_label = str(self.bme_humidity)
        self.current_time_label = str(self.current_time_label)
        self.formatted_cur_date_label = str(self.formatted_cur_date_label)
        self.bme_pressure_label = str(self.bme_pressure)
        self.bme_dewpoint_label = str(self.bme_dew_point)

    
if __name__ == "__main__":
    BME280App().run()
