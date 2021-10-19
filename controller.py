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


  def fan_low_on(self):
    print("Turning on cooler to low")
    GPIO.output(PUMP_PIN, ON)
    GPIO.output(FAN_L_PIN, ON)
    GPIO.output(FAN_H_PIN, OFF)
    GPIO.output(FURNACE_PIN, OFF)


  def fan_hi_on(self):
    print("Turning on cooler to high")
    GPIO.output(PUMP_PIN, ON)
    GPIO.output(FAN_L_PIN, OFF)
    GPIO.output(FAN_H_PIN, ON)
    GPIO.output(FURNACE_PIN, OFF)


  def furnace_on(self):
    print("Turning on furnace")
    GPIO.output(PUMP_PIN, OFF)
    GPIO.output(FAN_L_PIN, OFF)
    GPIO.output(FAN_H_PIN, OFF)
    GPIO.output(FURNACE_PIN, ON)


  def all_off(self):
    print("Turning cooler and furnace off")
    GPIO.output(PUMP_PIN, OFF)
    GPIO.output(FAN_L_PIN, OFF)
    GPIO.output(FAN_H_PIN, OFF)
    GPIO.output(FURNACE_PIN, OFF)


  # DO NOT USE IN PRODUCTION
  def all_on(self):
    print("Turning cooler and furnace on")
    GPIO.output(PUMP_PIN, ON)
    GPIO.output(FAN_L_PIN, ON)
    GPIO.output(FAN_H_PIN, ON)
    GPIO.output(FURNACE_PIN, ON)


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

