"""Handles GPIO pin control."""
# pylint: disable=E1101
# from RPi import GPIO
import RPi.GPIO as GPIO

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
    
    def set_pins(self, pump: bool, fan_on: bool, ac: bool, furnace: bool):
        pins_status = models.Pins(
            pump=pump, fan_on=fan_on, ac=ac, furnace=furnace)
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