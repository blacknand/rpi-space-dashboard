CREATE TABLE IF NOT EXISTS sensor_var (
    timestamp TEXT PRIMARY KEY NOT NULL,
    temp REAL NOT NULL,
    humidity REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS sensor_hour_max (
    hour TEXT PRIMARY KEY NOT NULL,
    max_temp REAL NOT NULL,
    max_humidity REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS sensor_day_max (
    day TEXT PRIMARY KEY NOT NULL,
    max_temp REAL NOT NULL,
    max_humidity REAL NOT NULL
);
