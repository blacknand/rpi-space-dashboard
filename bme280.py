import time
import math
import board
from adafruit_bme280 import basic as adafruit_bme280

# I2C connection
i2c = board.I2C()
bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c)
bme280.sea_level_pressure = 1010                                    # Base calibration point

b = 17.62
c = 243.12
gamma = (b * bme280.temperature / (c + bme280.temperature)) + math.log(bme280.humidity / 100.0)
dewpoint = format((c * gamma) / (b * gamma), ".2f")

while True:
    print("\nTemperature: %0.1f C" % bme280.temperature)
    print("Humidity: %0.1f %%" % bme280.relative_humidity)
    print("Pressure: %0.1f hPa" % bme280.pressure)
    print("Altitude = %0.2f meters" % bme280.altitude)
    print(f"Dew point: {dewpoint}")
    time.sleep(1)
