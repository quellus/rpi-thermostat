# rpi-thermostat

A cooler and furnace controller run by a RaspberryPi with wireless arduino-based temperature sensors.

## About
This project was created to solve two problems. The first being that I wanted to be able to control my evaporative cooler and furnace with a single thermostat, and I was unable to find a commercially available thermostat that could do that. The second problem is the wiring for the thermostats in my residence were installed too close to the vents. As a result, the thermostats' temperature readings were terribly inaccurate.

### Hardware used
* RaspberryPi
* multiples ESP8266 modules
* multiple DHT22/AHT20 temperature and humidity sensors
* [4 channel relay module](https://www.amazon.com/gp/product/B00KTEN3TM)

The RaspberryPi plays the role of the thermostat. It communicates and receives intructions via a RESTful API created with FastAPI. It also hosts an Apache Webserver to act as the primary user interface, and controls the heating and cooling systems by switching the relays on the 4 channel relay module.

The thermostat gathers temperature data from multiple ESP8266 modules. The temperature sensors read the temperature and humidity from a DHT22/AHT20 and reports it by sending a PUT request to the FastAPI server. The intention is to have a temperature sensor in each room of the residence so the thermostat 

## Setup Instructions

### Arduino setup:

1. Add and install [ESP8266](https://github.com/esp8266/Arduino).
2. Install [DHT Sensor Library](https://github.com/adafruit/DHT-sensor-library) (in the Library Manager).
3. Install [Adafruit AHTX0](https://github.com/adafruit/Adafruit_AHTX0) (in the Library Manager).
4. Edit `Config.h`, enter the SSID and Password of the WiFi network and the IP and Port of the Thermostat server.

### Thermostat Installation

#### Dependencies
apt requirements:  
build-essential python-dev git libgpiod2 python3-rpi.gpio python3-systemd apache2

pip requirements:  
adafruit-circuitpython-dht fastapi-restful uvicorn[standard] 

#### Daemon setup:

##### Development

1. cd into the `daemon` directory of the project
2. run `python -m uvicorn --host 0.0.0.0 main:app --reload`
   - For HTTPS
       - Generate a key and crt file with OpenSSL
       - Instead, run `python -m uvicorn --host 0.0.0.0 main:app --ssl-keyfile ~/daemon-selfsigned.key --ssl-certfile ~/daemon-selfsigned.crt --reload` (adjust the file paths accordingly)

##### Production

- Copy `thermostat.service` to `/etc/systemd/system`
- For HTTPS, generate a key and crt file with OpenSSL. `thermostat.service` by default expects these files to be located in `/home/pi/daemon-selfsigned.*`.
- Edit the `thermostat.service` file with appropriate user, group, paths to key and cert files, and working directory path
- Run `sudo systemctl daemon-reload` or reboot
- Run `sudo systemctl enable thermostat` to enable the service

The service will start on boot and automatically restart if anything goes wrong

#### Webapp setup:

install apache2 and make sure it is running

copy the contents of the webapp directory to `/var/www/html/`

run `sudo systemctl restart apache2`

##### Setting up HTTPS with self-signed certificates:
This section is slightly modified from [this tutorial](https://www.digitalocean.com/community/tutorials/how-to-create-a-self-signed-ssl-certificate-for-apache-in-ubuntu-16-04)

1. Enable mode_ssl and restart apache server
    1. `sudo a2enmod ssl`
    2. `sudo systemctl restart apache2`
2. Generate the SSL Certificate
    1. `sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /etc/ssl/private/apache-selfsigned.key -out /etc/ssl/certs/apache-selfsigned.crt -subj '/CN=localhost'`
    2. Make sure to replace "localhost" in the command with the address/domain name used to access the webapp.
3. Configure Apache
    1. Create and edit the conf file `/etc/apache2/sites-available/your_domain_or_ip.conf`
    2. ```
        <VirtualHost *:443>
            ServerName your_domain_or_ip
            DocumentRoot /var/www/html

            SSLEngine on
            SSLCertificateFile /etc/ssl/certs/apache-selfsigned.crt
            SSLCertificateKeyFile /etc/ssl/private/apache-selfsigned.key
        </VirtualHost>```
    
    3. Enable the confuration file
      1. `sudo a2ensite /etc/apache2/sites-available/your_domain_or_ip.conf`
      2. `sudo systemctl reload apache2`
