from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from time_data import formatted_cur_date, current_time

class InitialFrame(App):
    def build(self):
        return Label(text=formatted_cur_date)
    
if __name__ == "__main__":
    InitialFrame().run()
