-- Database stores temperature and humidity every minute, to display the highest temperature
-- and humidity for each hour of a day and each day for the last 7 days

-- Save temperature and humidity every minute
CREATE TABLE IF NOT EXISTS sensor_var (
    timestamp TEXT PRIMARY KEY NOT NULL,
    temp REAL NOT NULL,
    humidity REAL NOT NULL
);

-- Save the max temperature and humidity % per hour
CREATE TABLE IF NOT EXISTS sensor_hour_max (
    hour TEXT PRIMARY KEY NOT NULL,
    max_temp REAL NOT NULL,
    max_humidity REAL NOT NULL
);


-- Save the max temperature and humidity % per day
CREATE TABLE IF NOT EXISTS sensor_day_max (
    day TEXT PRIMARY KEY NOT NULL,
    max_temp REAL NOT NULL,
    max_humidity REAL NOT NULL
);
