# Rasberry Pi room conditions and space dashboard
A space themed dashboard designed for the Rasberry Pi 7 inch touchscreen, with the enviromental conditions of the room as well as displays with upcoming rocket launches, APOD, dynamic graphing of conditions and space news articles. The dashboard is designed to be run 24/7, with the dashboard turning the screen off at 11 PM and turining itself back on at 6 AM.
## Features
- Main dashboard: has the same theme as the real dashboard inside of Dragon, showing the temperature, humidity, barometric pressure and dew point of the room. Also displays current date and time
- Upcoming rocket launches: displays a list of 10 upcoming rocket launches including the rocket launch time to T+ 15 minutes, the mission, the LSP and launch site
- NASA APOD: displays the Astronomoy Picture of the Day from NASA with current time
- Enviromental conditions dynamic graph: has 2 graphs, one for the highest temperature and humidity percentage for each hour, for 12 hours on the current day from 8 AM to 8 PM. Other graph is the highest temperature and humidity percentage for each day, for the last 7 days. The hourly graph is updated every hour for the mentioned hours on the hour and the daily is updated every 24 hours
- Featured space news articles: displays a list of 10 featured space articles with the title, publisher, date of publishing, a brief summary and a image which you can touch to bring up the article
## Main display
![dashboard-img](https://github.com/user-attachments/assets/45a48608-d647-4c10-94b5-a6ead63350a5)
## Upcoming rocket launches display
![rockets-img](https://github.com/user-attachments/assets/2580a81f-7ad7-4794-b00a-b7dc30ab30b8)
## NASA APOD display
![apod-image](https://github.com/user-attachments/assets/780aeac3-6f9a-4199-87f9-d34a96c52156)
![apod-explanation](https://github.com/user-attachments/assets/2ebfff22-c123-4918-83db-ec75327ec166)
## Enviromental conditions graph display
**- TODO: Add image with data on both graphs**
![graph-image](https://github.com/user-attachments/assets/5462de5b-c68c-4b56-8535-3a34b6e86c67)
## Featured space news articles
![space-news-image](https://github.com/user-attachments/assets/0ddd3ad8-b999-46dd-86d7-e146a4371540)
![article-image](https://github.com/user-attachments/assets/deb35208-fb63-419f-8daf-1232d53e22eb)
## Hardware used
- [BME280 I2C/SPI](https://learn.adafruit.com/adafruit-bme280-humidity-barometric-pressure-temperature-sensor-breakout/downloads)
- [Rasberry Pi 4b](https://www.raspberrypi.com/products/raspberry-pi-4-model-b/)
- [Rasberry Pi 7 inch touchscreen display](https://www.raspberrypi.com/products/raspberry-pi-touch-display/)
