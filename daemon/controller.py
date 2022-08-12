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
FAN_LOW_PIN = 6
FAN_HIGH_PIN = 12
FURNACE_PIN = 13

PINS = {
  "pump": PUMP_PIN,
  "fan_low": FAN_LOW_PIN,
  "fan_high": FAN_HIGH_PIN,
  "furnace": FURNACE_PIN
}

ON = GPIO.LOW
OFF = GPIO.HIGH

CYCLE_TIME = 2 * 60 # minutes converted to seconds

class Controller:
  def __init__(self):
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(PUMP_PIN, GPIO.OUT, initial=OFF)
    GPIO.setup(FAN_LOW_PIN, GPIO.OUT, initial=OFF)
    GPIO.setup(FAN_HIGH_PIN, GPIO.OUT, initial=OFF)
    GPIO.setup(FURNACE_PIN, GPIO.OUT, initial=OFF)

    self._dht = adafruit_dht.DHT22(board.D4, use_pulseio=False)
    self.last_update_time = None

    try:
      f = open("status.json", "r")
      self.status = models.Status.parse_raw(f.read())
    except Exception:
      pins = models.Pins(pump = False, fan_low = False, fan_high = False, furnace = False)
      usable = models.Usable(cooler = True, furnace = True)
      self.status = models.Status(pins = pins, usable = usable, target_temp = 72, temp = 72, humidity = 30, manual_override = False)


  def get_status(self):
    return self.status


  def get_temperature(self):
    try:
      temperature_c = self._dht.temperature
      temperature_f = temperature_c * (9 / 5) + 32
      log.info("temperature: {}".format(temperature_f))
      print("temperature: {}".format(temperature_f))
      return round(temperature_f, 3)
    except RuntimeError as e:
      log.error("Temperature didn't read, trying again")
      print("Temperature didn't read, trying again")
      return self.get_temperature()


  def get_humidity(self):
    try:
      humidity = self._dht.humidity
      log.info("humidity: {}".format(humidity))
      print("humidity: {}".format(humidity))
      return humidity
    except RuntimeError as e:
      log.error("Humidity didn't read, trying again")
      print("Humidity didn't read, trying again")
      return self.get_humidity()

  
  def set_target_temp(self, temp: int):
    log.info("target temp set to {}".format(temp))
    print("target temp set to {}".format(temp))
    self.status.target_temp = temp


  def set_usable(self, cooler: bool, furnace: bool):
    usable = models.Usable(cooler = cooler, furnace = furnace)
    self.status.usable = usable


  def set_manual_override(self, override: bool, pins: models.Pins):
    self.status.manual_override = override
    self.set_pins(pins.pump, pins.fan_low, pins.fan_high, pins.furnace)


  def drive_status(self):
    try:
      self.status.humidity = self.get_humidity()
      self.status.temp = self.get_temperature()
      if (not self.status.manual_override):
        if (self.last_update_time == None or time.time() - self.last_update_time >= CYCLE_TIME):
          temp_diff = self.status.temp - self.status.target_temp
          if (temp_diff <= -2):
            self.furnace_on()
          elif temp_diff >= 5:
            self.fan_hi_on()
          elif temp_diff >= 2:
            self.fan_low_on()
          else:
            self.all_off()
          self.last_update_time = time.time()
      self.write_status()
    except Exception as e:
      log.critical(e)
      print(e)


  def fan_low_on(self):
    log.info("Turning on cooler to low")
    print("Turning on cooler to low")
    if self.status.usable.cooler:
      self.set_pins(True, True, False, False)
    else:
      self.all_off()


  def fan_hi_on(self):
    log.info("Turning on cooler to high")
    print("Turning on cooler to high")
    if self.status.usable.cooler:
      self.set_pins(True, False, True, False)
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


  def set_pins(self, pump: bool, fan_low: bool, fan_high: bool, furnace: bool):
    pins_status = models.Pins(pump = pump, fan_low = fan_low, fan_high = fan_high, furnace = furnace)
    self.status.pins = pins_status
    pump_pin = OFF
    fan_low_pin = OFF
    fan_high_pin = OFF
    furnace_pin = OFF
    if pump:
      pump_pin = ON
    if fan_low:
      fan_low_pin = ON
    if fan_high:
      fan_high_pin = ON
    if furnace:
      furnace_pin = ON
    GPIO.output(PUMP_PIN, pump_pin)
    GPIO.output(FAN_LOW_PIN, fan_low_pin)
    GPIO.output(FAN_HIGH_PIN, fan_high_pin)
    GPIO.output(FURNACE_PIN, furnace_pin)

  def write_status(self):
    f = open("status.json", "w")
    f.write(self.status.json())
    f.close()

