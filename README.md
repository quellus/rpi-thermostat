# rpi-thermostat

A cooler and furnace controller run by a RaspberryPi with wireless arduino-based temperature sensors.

![image](https://github.com/user-attachments/assets/b730898e-81bf-48fd-b9f2-f95659548468)

## About
This project was created to solve two problems:

1. There does not seem to be a consumer-available thermostat for controlling both a furnace and evaporative cooler. This requires two separate thermostats which can be difficult to control and requires the user to remember to turn one off when turning the other off.

2. Most thermostats have one temperature sensor integrated into the thermostat. This means if the wiring is located an inoptimal location such as near a vent, the thermostat will never have an accurate reading of the temperature of the residence.

This thermostat aims to solve these problems. It uses a Raspberry Pi to control the appliances and is fairly unconcerned about what they are making only the distinction between whether they cool or heat allowing it to control a furnace, evaporative cooler, and air conditioner. It also utilizes ESP8266 flashed with Arduino firmware as temperature sensors to monitor the temperature in multiple rooms simultaneously or a single, more optimal location.

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
nginx libsystemd-dev libasio-dev

 - `cd rpi-thermostat/daemon`
 - Setup a virtual environment `python -m venv .venv`
 - Activate the virtual environment `source ~/.venv/bin/activate`
 - Install dependencies `pip install -r requirements.txt`

#### Daemon setup:

##### Development

1. cd into the `daemon` directory of the project
2. Ensure you've activated the virtual environment
2. run `fastapi dev --port 8001 --host 127.0.0.1 main.py`

##### Production

- Copy `thermostat.service` to `/etc/systemd/system`
- Edit the `thermostat.service` file 
    - Replace user and group with the appropriate user and group. Ideally a user that is not a sudoer
    - Replace the two paths with a path to the daemon directory on the machine
- Run `sudo systemctl daemon-reload` or reboot
- Run `sudo systemctl enable thermostat` to enable the service

The service will start on boot and automatically restart if anything goes wrong

#### Webapp and SSL proxy setup:

1. Ensure nginx is running `sudo systemctl status nginx`
2. Copy the contents of the webapp directory to `/var/www/html`
3. Generate the SSL Certificate
    1. `sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /etc/ssl/private/nginx-selfsigned.key -out /etc/ssl/certs/nginx-selfsigned.crt -subj '/CN=localhost'`
    2. Make sure to replace "localhost" in the command with the address/domain name used to access the webapp.
4. Configure Nginx
    1. Edit the nginx.conf file
        1. Replace `<server domain>` with the server's IP address or domain.
        2. Replace `<fastapi-port>` with the port set in `thermostat.service`
    2. Copy the file to `/etc/nginx/sites-available/<server.ip>`
    3. Create symbolic link `sudo ln -s /etc/nginx/sites-available/<server.ip> /etc/nginx/sites-enabled/`
  
#### Postgres database and Grafana graphs (Optional)

The webapp's default ChartJS graph only shows the data stored in the RaspberryPi's memory. This was done not to limit the amount of data and writes the SD card will be subject to.
An alternative is to setup a Postgres database on a different machine and embed a Grafana graph using the data from the database.
![image](https://github.com/user-attachments/assets/e85a4ecc-1ca1-4be0-a681-6a88151ee28a)

##### Postgres

The daemon only requires a Postgres instance with a database. On first run, it will send queries to generate the necessary tables. Config for connecting to the Postgres instance must be added to `daemon/config.ini`.

1. Configure postgres with a username and password
2. Create an empty database
3. Run the daemon once to generate the default config file `daemon/config.ini`
4. Edit the file `daemon/config.ini`
  1. `db_enabled` set to "True"
  2. `db_user` username with access to database
  3. `db_password` password for `db_user`
  4. `db_database` name of database on the postgres server
  5. `db_host` hostname/ip address for postgres server

##### Grafana

Grafana is used to generate a pretty line graph showing temperature changes over the last 12 hours. The webapp, however, will embed any url in the config.

1. Create a new dashboard
2. Add visualization
3. Create the graph with the following query `SELECT time, average_temp, target_temp FROM averages as value`
4. Get embed link
    1. Click the 3 dots botton in the top right of the grpah
    2. Select `Share`
    3. Select the `Embed` tab
    4. Disable `Lock time range`
    5. Copy only the `src` url
5. Edit `webapp/config.json`
    1.  Change `use_grafana` to `true`
    2.  Change `grafana_embed_url` to the url copied in the previous step
