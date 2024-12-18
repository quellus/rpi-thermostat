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
- Edit the file with appropriate user, group, paths to key and cert files, and working directory path
- Run `sudo systemctl daemon-reload` or reboot
- Run `sudo systemctl enable thermostat` to enable the service

The service will start on boot and automatically restart if anything goes wrong

### Webapp setup:

install apache2 and make sure it is running

copy the contents of the webapp directory to `/var/www/html/`

run `sudo systemctl restart apache2`

#### Setting up HTTPS with self-signed certificates
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

