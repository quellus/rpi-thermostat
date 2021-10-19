import adafruit_dht
import board
import RPi.GPIO as GPIO

PUMP_PIN = 5
FAN_L_PIN = 6
FAN_H_PIN = 12
FURNACE_PIN = 13

PINS = {
  "pump": PUMP_PIN,
  "fan_low": FAN_L_PIN,
  "fan_high": FAN_H_PIN,
  "furnace": FURNACE_PIN
}

ON = GPIO.LOW
OFF = GPIO.HIGH

class Controller:
  def __init__(self):
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(PUMP_PIN, GPIO.OUT, initial=OFF)
    GPIO.setup(FAN_L_PIN, GPIO.OUT, initial=OFF)
    GPIO.setup(FAN_H_PIN, GPIO.OUT, initial=OFF)
    GPIO.setup(FURNACE_PIN, GPIO.OUT, initial=OFF)

    self._dht = adafruit_dht.DHT11(board.D4, use_pulseio=False)
    self.target_temp = 72


  def get_status(self):
    status = {}
    for key in PINS.keys():
      pin_stat = GPIO.input(PINS[key])
      if pin_stat == 1:
        status[key] = False
      else:
        status[key] = True
    status["temp"] = self.get_temperature()
    status["humidity"] = self.get_humidity()
    return status


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
    self.target_temp = temp


  def drive_status(self):
    try:
      self.get_humidity()
      temp_diff = self.get_temperature() - self.target_temp
      print("temperature difference is {}".format(round(temp_diff)))
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
    self.set_pins(True, True, False, False)


  def fan_hi_on(self):
    print("Turning on cooler to high")
    self.set_pins(True, False, True, False)


  def furnace_on(self):
    print("Turning on furnace")
    self.set_pins(False, False, False, True)


  def all_off(self):
    print("Turning cooler and furnace off")
    self.set_pins(False, False, False, False)


  def set_pins(self, pump: bool, fan_low: bool, fan_high: bool, furnace: bool):
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
    GPIO.output(FAN_L_PIN, fan_low_pin)
    GPIO.output(FAN_H_PIN, fan_high_pin)
    GPIO.output(FURNACE_PIN, furnace_pin)

   

