import os
# Only keep on during testing
# os.environ["PYSDL2_DLL_PATH"] = os.path.join(os.getcwd(), "env/lib/python3.12/site-packages/kivy/.dylibs")
# os.environ["KIVY_NO_CONSOLELOG"] = "1"
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.stacklayout import StackLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from bme280 import bme280_results                           # Comment during testing
from kivy.core.window import Window
from rocket_launches import RocketLaunchesData

# Config
Window.fullscreen = "auto"
launch_api_url = "https://lldev.thespacedevs.com/2.2.0/launch/upcoming/"
api_url_filters = "limit=10&include_suborbital=true&hide_recent_previous=true&ordering=net&mode=list&tbd=true"
api_url = f"{launch_api_url}?{api_url_filters}"
rocket_launch_obj = RocketLaunchesData(api_url)

# For testing purposes (BME data only available on R pi) - comment out during deployment
# def bme280_results():
#     temp = "28°C"
#     pressure = "1250 hPa"
#     humidity = "40 %"
#     dew_point = "10°C"
#     return [temp, pressure, humidity, dew_point]

class MainScreen(BoxLayout):
    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)

        header_layout = BoxLayout(spacing=2, orientation="horizontal", padding=5)
        temp_layout = BoxLayout(orientation="vertical", spacing=0, padding=(0, 2))
        pressure_layout = BoxLayout(orientation="vertical", spacing=0, padding=(0, 2))
        humidity_layout = BoxLayout(orientation="vertical", spacing=0, padding=(0, 2))
        dew_point_layout = BoxLayout(orientation="vertical", spacing=0, padding=(0, 2))

        self.current_date = Label(text=rocket_launch_obj.current_time()[0])
        self.current_time = Label(text=rocket_launch_obj.current_time()[1])
        self.bme_temp = Label(text=bme280_results()[0])
        self.bme_pressure = Label(text=bme280_results()[1])
        self.bme_humidity = Label(text=bme280_results()[2])
        self.bme_dew_point = Label(text=bme280_results()[3])

        # Add labels above BME data inside of respective widgets
        temp_layout.add_widget(Label(text="Temp", font_size="10sp", halign="left"))
        temp_layout.add_widget(self.bme_temp)
        humidity_layout.add_widget(Label(text="Humidity", font_size="10sp"))
        humidity_layout.add_widget(self.bme_humidity)
        pressure_layout.add_widget(Label(text="Pressure", font_size="10sp"))
        pressure_layout.add_widget(self.bme_pressure)
        dew_point_layout.add_widget(Label(text="Dew point", font_size="10sp"))
        dew_point_layout.add_widget(self.bme_dew_point)

        # Add all data to header widget
        header_layout.add_widget(self.current_date)
        header_layout.add_widget(self.current_time)
        header_layout.add_widget(temp_layout)
        header_layout.add_widget(humidity_layout)
        header_layout.add_widget(pressure_layout)
        header_layout.add_widget(dew_point_layout)

        self.add_widget(header_layout)

        Clock.schedule_interval(self.update_data, 1)    # Update every second

    def update_data(self, *args):
        # Update time + BME data every second
        self.current_date.text = rocket_launch_obj.current_time()[0]
        self.current_time.text = rocket_launch_obj.current_time()[1]
        self.bme_temp.text = bme280_results()[0]
        self.bme_pressure.text = bme280_results()[1]
        self.bme_humidity.text = bme280_results()[2]
        self.bme_dew_point.text = bme280_results()[3]

class KivyApp(App):
    def build(self):
        return MainScreen()


if __name__ == "__main__":
    KivyApp().run()
