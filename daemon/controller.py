import adafruit_dht
import board
import RPi.GPIO as GPIO
import models
import logging
import time
from systemd.journal import JournalHandler

log = logging.getLogger("thermostat")
log.addHandler(JournalHandler())
log.setLevel(logging.INFO)

PUMP_PIN = 5
FAN_ON_PIN = 6
AC_PIN = 12
FURNACE_PIN = 13

PINS = {
  "pump": PUMP_PIN,
  "fan_on": FAN_ON_PIN,
  "ac": AC_PIN,
  "furnace": FURNACE_PIN
}

ON = GPIO.LOW
OFF = GPIO.HIGH

CYCLE_TIME = 2 * 60 # minutes converted to seconds
SENSOR_STALE_TIMEOUT = 1 * 60 # minutes converted to seconds

class Controller:
  def __init__(self):
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(PUMP_PIN, GPIO.OUT, initial=OFF)
    GPIO.setup(FAN_ON_PIN, GPIO.OUT, initial=OFF)
    GPIO.setup(AC_PIN, GPIO.OUT, initial=OFF)
    GPIO.setup(FURNACE_PIN, GPIO.OUT, initial=OFF)

    self._dht = adafruit_dht.DHT22(board.D4, use_pulseio=False)
    self.last_update_time = None

    try:
      f = open("status.json", "r")
      self.status = models.Status.parse_raw(f.read())
    except Exception:
      pins = models.Pins(pump = False, fan_on = False, ac = False, furnace = False)
      usable = models.Usable(ac = True, cooler = True, furnace = True)
      self.status = models.Status(pins = pins, usable = usable, target_temp = 72, average_temp = 72, humidity = 30, manual_override = False, sensors = {})


  def get_status(self):
    return self.status
  

  def get_temperature(self):
    for i in range(3):
      try:
        temperature_c = self._dht.temperature
        if temperature_c:
          temperature_f = temperature_c * (9 / 5) + 32
          log.info("temperature: {}".format(temperature_f))
          print("temperature: {}".format(temperature_f))
          return round(temperature_f, 3)
      except:
        log.error("Temperature didn't read, trying again")
        print("Temperature didn't read, trying again")
        continue
    return None


  def get_humidity(self):
    for i in range(3):
      try:
        humidity = self._dht.humidity
        if humidity:
          log.info("humidity: {}".format(humidity))
          print("humidity: {}".format(humidity))
          return humidity
      except:
        log.error("Humidity didn't read, trying again")
        print("Humidity didn't read, trying again")
        continue
    return None

  
  def set_target_temp(self, temp: int):
    log.info("target temp set to {}".format(temp))
    print("target temp set to {}".format(temp))
    self.status.target_temp = temp


  def set_usable(self, ac: bool, cooler: bool, furnace: bool):
    usable = models.Usable(ac = ac, cooler = cooler, furnace = furnace)
    self.status.usable = usable


  def set_manual_override(self, override: bool, pins: models.Pins):
    self.status.manual_override = override
    self.set_pins(pins.pump, pins.fan_on, pins.ac, pins.furnace)


  def update_sensor_status(self, name: str, temp: float, humidity: float):
    self.status.sensors[name] = {"humidity": humidity, "temperature": temp, "timestamp": time.time()}


  def update_local_sensor(self):
    temperature = self.get_temperature()
    humidity = self.get_humidity()
    log.info("{} {}".format(temperature, humidity))
    if humidity and temperature:
      self.status.sensors["Closet"] = {"humidity": humidity, "temperature": temperature, "timestamp": time.time()}


  def drive_status(self):
    try:
      self.remove_stale_sensors()
      self.status.average_temp = self.get_average_temp()
      if not self.status.manual_override:
        if (self.last_update_time == None or time.time() - self.last_update_time >= CYCLE_TIME):
          temp_diff = self.status.average_temp - self.status.target_temp
          if self.status.pins.ac == True and self.status.usable.ac:
            if temp_diff <= 1:
              self.all_off()
              self.last_update_time = time.time()
            elif temp_diff <= 2:
              self.fan_low_on()
              self.last_update_time = time.time()
            else:
              self.ac_on()
          elif self.status.pins.fan_on == True:
            if temp_diff >= 3 and self.status.usable.ac:
              self.ac_on()
              self.last_update_time = time.time()
            elif temp_diff <= 1:
              self.all_off()
              self.last_update_time = time.time()
            else:
              self.fan_low_on()
          elif self.status.pins.furnace == True:
            if temp_diff >= -1:
              self.all_off()
              self.last_update_time = time.time()
            else:
              self.furnace_on()
          else:
            if temp_diff <= -2:
              self.furnace_on()
              self.last_update_time = time.time()
            elif temp_diff >= 2:
              self.fan_low_on()
              self.last_update_time = time.time()
            else:
              self.all_off()

      self.write_status()
    except Exception as e:
      log.critical(e)
      print(e)


  def remove_stale_sensors(self):
    sensor_keys = self.status.sensors.keys()
    sensors_to_remove = []
    for key in sensor_keys:
      if self.status.sensors[key]["timestamp"] + SENSOR_STALE_TIMEOUT <= time.time():
        sensors_to_remove.append(key)
    for key in sensors_to_remove:
        self.status.sensors.pop(key)


  def get_average_temp(self):
    temp_sum = 0
    sensor_keys = self.status.sensors.keys()
    for key in sensor_keys:
      temp_sum += self.status.sensors[key]["temperature"]
    return temp_sum / len(sensor_keys)


  def fan_low_on(self):
    log.info("Turning on cooler to low")
    print("Turning on cooler to low")
    if self.status.usable.cooler:
      self.set_pins(True, True, False, False)
    else:
      self.all_off()


  def ac_on(self):
    log.info("Turning on ac")
    print("Turning on ac")
    if self.status.usable.ac:
      self.set_pins(False, False, True, False)
    else:
      self.all_off()


  def furnace_on(self):
    log.info("Turning on furnace")
    print("Turning on furnace")
    if self.status.usable.furnace:
      self.set_pins(False, False, False, True)
    else:
      self.all_off()


  def all_off(self):
    log.info("Turning cooler and furnace off")
    print("Turning cooler and furnace off")
    self.set_pins(False, False, False, False)


  def set_pins(self, pump: bool, fan_on: bool, ac: bool, furnace: bool):
    pins_status = models.Pins(pump = pump, fan_on = fan_on, ac = ac, furnace = furnace)
    self.status.pins = pins_status
    pump_pin = OFF
    fan_on_pin = OFF
    ac_pin = OFF
    furnace_pin = OFF
    if pump:
      pump_pin = ON
    if fan_on:
      fan_on_pin = ON
    if ac:
      ac_pin = ON
    if furnace:
      furnace_pin = ON
    GPIO.output(PUMP_PIN, pump_pin)
    GPIO.output(FAN_ON_PIN, fan_on_pin)
    GPIO.output(AC_PIN, ac_pin)
    GPIO.output(FURNACE_PIN, furnace_pin)

  def write_status(self):
    f = open("status.json", "w")
    f.write(self.status.json())
    f.close()

