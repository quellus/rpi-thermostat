"""Handles GPIO pin control."""
# pylint: disable=E1101

try:
    import RPi.GPIO as GPIO
except:
    import Mock.GPIO as GPIO

import models

ON = GPIO.LOW
OFF = GPIO.HIGH

PUMP_PIN = 5
FAN_ON_PIN = 6
AC_PIN = 12
FURNACE_PIN = 13

class GpioController():
    """Encapsulates control of GPIO pins and creates aliases for each pin"""
    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(PUMP_PIN, GPIO.OUT, initial=OFF)
        GPIO.setup(FAN_ON_PIN, GPIO.OUT, initial=OFF)
        GPIO.setup(AC_PIN, GPIO.OUT, initial=OFF)
        GPIO.setup(FURNACE_PIN, GPIO.OUT, initial=OFF)

        self.pins_status = models.Pins(
            pump=False, fan_on=False, ac=False, furnace=False)


    def fan_low_on(self):
        self.log.info("Turning on cooler to low")
        print("Turning on cooler to low")
        if self.status.usable.cooler:
            self._set_pins(True, True, False, False)
        else:
            self._all_off()


    def ac_on(self):
        self.log.info("Turning on ac")
        print("Turning on ac")
        if self.status.usable.ac:
            self._set_pins(False, False, True, False)
        else:
            self._all_off()


    def furnace_on(self):
        self.log.info("Turning on furnace")
        print("Turning on furnace")
        if self.status.usable.furnace:
            self._set_pins(False, False, False, True)
        else:
            self._all_off()


    def all_off(self):
        self.log.info("Turning cooler and furnace off")
        print("Turning cooler and furnace off")
        self._set_pins(False, False, False, False)


    def set_pins(self, pump: bool, fan_on: bool, ac: bool, furnace: bool):
        """Sets state of each system. True turns the system ON, False turns it OFF"""
        self.pins_status = models.Pins(
            pump=pump, fan_on=fan_on, ac=ac, furnace=furnace)
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