import adafruit_dht
import board
import RPi.GPIO as GPIO
import models

PUMP_PIN = 5
FAN_ON_PIN = 6
FAN_SPEED_PIN = 12
FURNACE_PIN = 13

PINS = {
  "pump": PUMP_PIN,
  "fan_on": FAN_ON_PIN,
  "fan_speed": FAN_SPEED_PIN,
  "furnace": FURNACE_PIN
}

ON = GPIO.LOW
OFF = GPIO.HIGH

class Controller:
  def __init__(self):
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(PUMP_PIN, GPIO.OUT, initial=OFF)
    GPIO.setup(FAN_ON_PIN, GPIO.OUT, initial=OFF)
    GPIO.setup(FAN_SPEED_PIN, GPIO.OUT, initial=OFF)
    GPIO.setup(FURNACE_PIN, GPIO.OUT, initial=OFF)

    self._dht = adafruit_dht.DHT22(board.D4, use_pulseio=False)

    pins = models.Pins(pump = False, fan_on = False, fan_speed = False, furnace = False)
    usable = models.Usable(cooler = True, furnace = True)
    self.status = models.Status(pins = pins, usable = usable, target_temp = 72, temp = 72, humidity = 30)


  def get_status(self):
    return self.status


  def get_temperature(self):
    try:
      temperature_c = self._dht.temperature
      temperature_f = temperature_c * (9 / 5) + 32
      print("temperature:", temperature_f)
      return temperature_f
    except RuntimeError as e:
      print("Temperature didn't read, trying again")
      return self.get_temperature()


  def get_humidity(self):
    try:
      humidity = self._dht.humidity
      print("humidity:", humidity)
      return humidity
    except RuntimeError as e:
      print("Humidity didn't read, trying again")
      return self.get_humidity()

  
  def set_target_temp(self, temp: int):
    print("target temp set to {}".format(temp))
    self.status.target_temp = temp


  def set_usable(self, cooler: bool, furnace: bool):
      usable = models.Usable(cooler = cooler, furnace = furnace)
      self.status.usable = usable


  def drive_status(self):
    try:
      self.status.humidity = self.get_humidity()
      self.status.temp = self.get_temperature()
      temp_diff = self.status.temp - self.status.target_temp
      print("temperature difference is {}".format(round(temp_diff, 3)))
      if (temp_diff <= -2):
        self.furnace_on()
      elif temp_diff >= 5:
        self.fan_hi_on()
      elif temp_diff >= 2:
        self.fan_low_on()
      else:
        self.all_off()
    except Exception as e:
      print(e)


  def fan_low_on(self):
    print("Turning on cooler to low")
    if self.status.usable.cooler:
      self.set_pins(True, True, False, False)
    else:
      self.all_off()


  def fan_hi_on(self):
    print("Turning on cooler to high")
    if self.status.usable.cooler:
      self.set_pins(True, True, True, False)
    else:
      self.all_off()


  def furnace_on(self):
    print("Turning on furnace")
    if self.status.usable.furnace:
      self.set_pins(False, False, False, True)
    else:
      self.all_off()


  def all_off(self):
    print("Turning cooler and furnace off")
    self.set_pins(False, False, False, False)


  def set_pins(self, pump: bool, fan_on: bool, fan_speed: bool, furnace: bool):
    pins_status = models.Pins(pump = pump, fan_on = fan_on, fan_speed = fan_speed, furnace = furnace)
    self.status.pins = pins_status
    pump_pin = OFF
    fan_on_pin = OFF
    fan_speed_pin = OFF
    furnace_pin = OFF
    if pump:
      pump_pin = ON
    if fan_on:
      fan_on_pin = ON
    if fan_speed:
      fan_speed_pin = ON
    if furnace:
      furnace_pin = ON
    GPIO.output(PUMP_PIN, pump_pin)
    GPIO.output(FAN_ON_PIN, fan_on_pin)
    GPIO.output(FAN_SPEED_PIN, fan_speed_pin)
    GPIO.output(FURNACE_PIN, furnace_pin)

