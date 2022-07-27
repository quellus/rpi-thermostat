# rpi-thermostat

A cooler and furnace controller run by a Raspberry Pi

apt requirements:  
build-essential python-dev python-openssl git libgpiod2 python3-rpi.gpio python-systemd python3-systemd apache2

pip requirements:  
adafruit-circuitpython-dht fastapi-restful uvicorn[standard] 

### Daemon setup:

`python -m uvicorn --host 0.0.0.0 main:app`

### Webapp setup:

install apache2 and make sure it is running

copy the contents of the webapp directory to `/var/www/html/`

