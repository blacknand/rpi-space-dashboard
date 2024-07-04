from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from bme280 import bme280_results
from kivy.core.window import Window
from time_data import current_time, formatted_cur_date

# TODO: Just the GUI