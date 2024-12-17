# rpi-thermostat

A cooler and furnace controller run by a Raspberry Pi

apt requirements:  
build-essential python-dev git libgpiod2 python3-rpi.gpio python3-systemd apache2

pip requirements:  
adafruit-circuitpython-dht fastapi-restful uvicorn[standard] 

### Daemon setup:

#### Development

`python -m uvicorn --host 0.0.0.0 main:app`--reload

#### Production

- Copy `thermostat.service` to `/etc/systemd/system`
- Run `sudo systemctl daemon-reload` or reboot
- Run `sudo systemctl enable thermostat` to enable the service

The service will start on boot and automatically restart if anything goes wrong

### Arduino setup:

1. Add and install [ESP8266](https://github.com/esp8266/Arduino)
2. Install [DHT Sensor Library](https://github.com/adafruit/DHT-sensor-library) (in the Library Manager)
3. Install [Adafruit AHTX0](https://github.com/adafruit/Adafruit_AHTX0) (in the Library Manager)

### Webapp setup:

install apache2 and make sure it is running

copy the contents of the webapp directory to `/var/www/html/`

run `sudo systemctl restart apache2`
