# rpi-thermostat

A cooler and furnace controller run by a Raspberry Pi

apt requirements:  
build-essential python-dev python-openssl git libgpiod2 python3-rpi.gpio python-systemd python3-systemd

pip requirements:  
adafruit-circuitpython-dht fastapi-restful uvicorn[standard] 

Running:

`python -m uvicorn --host 0.0.0.0 main:app`
