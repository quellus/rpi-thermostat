"""Handles GPIO pin control."""
# pylint: disable=E1101,E0401

import sys

import models

if "unittest" in sys.modules:
    from Mock import GPIO
else:
    from RPi import GPIO


ON = GPIO.LOW
OFF = GPIO.HIGH

PUMP_PIN = 5
FAN_ON_PIN = 6
AC_PIN = 12
FURNACE_PIN = 13

class GpioController():
    """Encapsulates control of GPIO pins and creates aliases for each pin"""
    def __init__(self, log):
        self.log = log
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(PUMP_PIN, GPIO.OUT, initial=OFF)
        GPIO.setup(FAN_ON_PIN, GPIO.OUT, initial=OFF)
        GPIO.setup(AC_PIN, GPIO.OUT, initial=OFF)
        GPIO.setup(FURNACE_PIN, GPIO.OUT, initial=OFF)

        self.pins_status = models.Pins(pump=False, fan_on=False, ac=False, furnace=False)
        self.usable = models.Usable(ac = False, cooler = False, furnace = False)

    def cooling_on(self):
        """
        Turns on ac or cooler depending on which is "usable".
        If both are usable, it prioritizes the ac
        """
        if self.usable.ac:
            self.ac_on()
        elif self.usable.cooler:
            self.fan_low_on()


    def fan_low_on(self):
        """Turns the cooler pump and fan on"""
        self.log.info("Turning on fan low")
        print("Turning on fan low")
        self.set_pins(True, True, False, False)


    def ac_on(self):
        """Turns A/C on"""
        self.log.info("Turning on ac")
        print("Turning on ac")
        self.set_pins(False, False, True, False)


    def furnace_on(self):
        """Turns furnace on"""
        self.log.info("Turning on furnace")
        print("Turning on furnace")
        self.set_pins(False, False, False, True)


    def all_off(self):
        """Turns all pins off"""
        self.log.info("Turning on all systems off")
        print("Turning on all systems off")
        self.set_pins(False, False, False, False)


    def set_pins(self, pump: bool, fan_on: bool, ac: bool, furnace: bool):
        """Sets state of each system. True turns the system ON, False turns it OFF"""
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
        self.pins_status = models.Pins(
            pump=pump, fan_on=fan_on, ac=ac, furnace=furnace)
