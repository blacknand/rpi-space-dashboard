# Rasberry Pi room conditions and space dashboard
A space themed dashboard designed for the Rasberry Pi 7 inch touchscreen, with the enviromental conditions of the room as well as displays with upcoming rocket launches, APOD, dynamic graphing of conditions and space news articles. The dashboard is designed to be run 24/7, with the dashboard turning the screen off at 11 PM and turining itself back on at 6 AM.
## Features
- Main dashboard: has the same theme as the real dashboard inside of Dragon, showing the temperature, humidity, barometric pressure and dew point of the room. Also displays current date and time
- Upcoming rocket launches: displays a list of 10 upcoming rocket launches including the rocket launch time to T+ 15 minutes, the mission, the LSP and launch site
- NASA APOD: displays the Astronomoy Picture of the Day from NASA
- Enviromental conditions dynamic graph: displays a graph for the highest temperature and humidity percentage for each hour, for 12 hours on the current day from 8 AM to 8 PM. The graph is updated dynamically every hour and then cleared at 12 AM
- Featured space news articles: displays a list of 10 featured space articles with the title, publisher, date of publishing, a brief summary and a image which you can touch to bring up the article
- Restarts dynamically: `interface.py` will end itself and then restart every monday at 12 AM so the app/Raspberry Pi can be left for truly 24/7 and it will never run out of memory
## Main display
![main-display-readme](https://github.com/user-attachments/assets/26ba2eb0-96d9-48ec-908c-a41ac638623c)
## Upcoming rocket launches display
![rocket-display-readme](https://github.com/user-attachments/assets/7134d208-6d69-4b9d-9fd5-c9d7605ba61f)
## NASA APOD display
![apod-display-readme](https://github.com/user-attachments/assets/b065e3b6-7c26-426f-a1fe-dca7ae76bcb1)
![apod-explanation-readme](https://github.com/user-attachments/assets/cfe526be-e197-42fb-a65c-68e80f6c4a03)
## Enviromental conditions graph display
![20240925_18h49m07s_grim](https://github.com/user-attachments/assets/0d28bc8c-19e9-4a9f-933d-213a14c325da)
## Featured space news articles
![news-article-readme](https://github.com/user-attachments/assets/6fcf1025-431d-4120-9550-8ffa588ff350)
![news-article-widget-readme](https://github.com/user-attachments/assets/c685dc97-a16c-488a-a2b4-28dccbe8f3da)
## Hardware used
- [BME280 I2C/SPI](https://learn.adafruit.com/adafruit-bme280-humidity-barometric-pressure-temperature-sensor-breakout/downloads)
- [Rasberry Pi 4b](https://www.raspberrypi.com/products/raspberry-pi-4-model-b/)
- [Rasberry Pi 7 inch touchscreen display](https://www.raspberrypi.com/products/raspberry-pi-touch-display/)
# To install
- SSH: `git clone git@github.com:blacknand/rpi-space-dashboard.git`     
- HTTP: `git clone https://github.com/blacknand/rpi-space-dashboard.git`    
Install all dependencies: ```pip install -r requirements.txt```      
**Run app**
- Linux/macOS: ```python3 interface.py```  
- Windows: ```python interface.py```
