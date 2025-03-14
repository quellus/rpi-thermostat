# pylint: disable-all

import unittest
from unittest.mock import patch
import Mock.GPIO as GPIO

import gpio_controller
import models

pins = [
        gpio_controller.PUMP_PIN, 
        gpio_controller.FAN_ON_PIN, 
        gpio_controller.AC_PIN,
        gpio_controller.FURNACE_PIN
    ]

class TestGpioController(unittest.TestCase):
    def setUp(self):
        self.log = unittest.mock.MagicMock()
        self.controller = gpio_controller.GpioController(self.log)

    # def test_init__sets_pin_mode(self):
    #     self.assertTrue(GPIO.setModeDone)
    #     self.assertEqual(GPIO.getmode(), GPIO.BCM)


    def test_init__sets_pins_to_out(self):
        for pin in pins:
            self.assertEqual(GPIO.channel_config[pin].direction, GPIO.OUT)
            self.assertEqual(GPIO.channel_config[pin].initial, GPIO.HIGH)


    def test_initial_pins_status_off(self):
        self.assertFalse(self.controller.pins_status.pump)
        self.assertFalse(self.controller.pins_status.fan_on)
        self.assertFalse(self.controller.pins_status.ac)
        self.assertFalse(self.controller.pins_status.furnace)


    @patch("gpio_controller.GPIO")  # Mock the GPIO module
    def test_fan_low_on__turns_on_pump_and_fan(self, mock_gpio: unittest.mock.MagicMock):
        self.controller.fan_low_on()

        mock_gpio.output.assert_any_call(
            gpio_controller.PUMP_PIN, gpio_controller.ON)
        mock_gpio.output.assert_any_call(
            gpio_controller.FAN_ON_PIN, gpio_controller.ON)
        mock_gpio.output.assert_any_call(
            gpio_controller.AC_PIN, gpio_controller.OFF)
        mock_gpio.output.assert_any_call(
            gpio_controller.FURNACE_PIN, gpio_controller.OFF)
        
        self.assertTrue(self.controller.pins_status.pump)
        self.assertTrue(self.controller.pins_status.fan_on)
        self.assertFalse(self.controller.pins_status.ac)
        self.assertFalse(self.controller.pins_status.furnace)


    @patch("gpio_controller.GPIO")  # Mock the GPIO module
    def test_ac_on__turns_ac_on(self, mock_gpio: unittest.mock.MagicMock):
        self.controller.ac_on()
        mock_gpio.output.assert_any_call(
            gpio_controller.PUMP_PIN, gpio_controller.OFF)
        mock_gpio.output.assert_any_call(
            gpio_controller.FAN_ON_PIN, gpio_controller.OFF)
        mock_gpio.output.assert_any_call(
            gpio_controller.AC_PIN, gpio_controller.ON)
        mock_gpio.output.assert_any_call(
            gpio_controller.FURNACE_PIN, gpio_controller.OFF)
        
        self.assertFalse(self.controller.pins_status.pump)
        self.assertFalse(self.controller.pins_status.fan_on)
        self.assertTrue(self.controller.pins_status.ac)
        self.assertFalse(self.controller.pins_status.furnace)


    @patch("gpio_controller.GPIO")  # Mock the GPIO module
    def test_furnace_on__turns_furnace_on(self, mock_gpio: unittest.mock.MagicMock):
        self.controller.furnace_on()
        mock_gpio.output.assert_any_call(
            gpio_controller.PUMP_PIN, gpio_controller.OFF)
        mock_gpio.output.assert_any_call(
            gpio_controller.FAN_ON_PIN, gpio_controller.OFF)
        mock_gpio.output.assert_any_call(
            gpio_controller.AC_PIN, gpio_controller.OFF)
        mock_gpio.output.assert_any_call(
            gpio_controller.FURNACE_PIN, gpio_controller.ON)
        
        self.assertFalse(self.controller.pins_status.pump)
        self.assertFalse(self.controller.pins_status.fan_on)
        self.assertFalse(self.controller.pins_status.ac)
        self.assertTrue(self.controller.pins_status.furnace)


    @patch("gpio_controller.GPIO")  # Mock the GPIO module
    def test_all_off__turns_all_pins_off(self, mock_gpio: unittest.mock.MagicMock):
        self.controller.all_off()
        mock_gpio.output.assert_any_call(
            gpio_controller.PUMP_PIN, gpio_controller.OFF)
        mock_gpio.output.assert_any_call(
            gpio_controller.FAN_ON_PIN, gpio_controller.OFF)
        mock_gpio.output.assert_any_call(
            gpio_controller.AC_PIN, gpio_controller.OFF)
        mock_gpio.output.assert_any_call(
            gpio_controller.FURNACE_PIN, gpio_controller.OFF)
        
        self.assertFalse(self.controller.pins_status.pump)
        self.assertFalse(self.controller.pins_status.fan_on)
        self.assertFalse(self.controller.pins_status.ac)
        self.assertFalse(self.controller.pins_status.furnace)


    @patch("gpio_controller.GPIO")  # Mock the GPIO module
    def test_set_pins__turns_off_all_pins(self, mock_gpio: unittest.mock.MagicMock):
        self.controller.set_pins(False, False, False, False)
        mock_gpio.output.assert_any_call(
            gpio_controller.PUMP_PIN, gpio_controller.OFF)
        mock_gpio.output.assert_any_call(
            gpio_controller.FAN_ON_PIN, gpio_controller.OFF)
        mock_gpio.output.assert_any_call(
            gpio_controller.AC_PIN, gpio_controller.OFF)
        mock_gpio.output.assert_any_call(
            gpio_controller.FURNACE_PIN, gpio_controller.OFF)
        
        self.assertFalse(self.controller.pins_status.pump)
        self.assertFalse(self.controller.pins_status.fan_on)
        self.assertFalse(self.controller.pins_status.ac)
        self.assertFalse(self.controller.pins_status.furnace)
        

    @patch("gpio_controller.GPIO")  # Mock the GPIO module
    def test_set_pins__turns_all_on(self, mock_gpio: unittest.mock.MagicMock):
        self.controller.set_pins(True, True, True, True)
        mock_gpio.output.assert_any_call(
            gpio_controller.PUMP_PIN, gpio_controller.ON)
        mock_gpio.output.assert_any_call(
            gpio_controller.FAN_ON_PIN, gpio_controller.ON)
        mock_gpio.output.assert_any_call(
            gpio_controller.AC_PIN, gpio_controller.ON)
        mock_gpio.output.assert_any_call(
            gpio_controller.FURNACE_PIN, gpio_controller.ON)
        
        self.assertTrue(self.controller.pins_status.pump)
        self.assertTrue(self.controller.pins_status.fan_on)
        self.assertTrue(self.controller.pins_status.ac)
        self.assertTrue(self.controller.pins_status.furnace)


    @patch("gpio_controller.GPIO")  # Mock the GPIO module
    def test_set_pins__turns_pump_on(self, mock_gpio: unittest.mock.MagicMock):
        self.controller.set_pins(True, False, False, False)
        mock_gpio.output.assert_any_call(
            gpio_controller.PUMP_PIN, gpio_controller.ON)
        mock_gpio.output.assert_any_call(
            gpio_controller.FAN_ON_PIN, gpio_controller.OFF)
        mock_gpio.output.assert_any_call(
            gpio_controller.AC_PIN, gpio_controller.OFF)
        mock_gpio.output.assert_any_call(
            gpio_controller.FURNACE_PIN, gpio_controller.OFF)
        
        self.assertTrue(self.controller.pins_status.pump)
        self.assertFalse(self.controller.pins_status.fan_on)
        self.assertFalse(self.controller.pins_status.ac)
        self.assertFalse(self.controller.pins_status.furnace)


    @patch("gpio_controller.GPIO")  # Mock the GPIO module
    def test_set_pins__turns_fan_on(self, mock_gpio: unittest.mock.MagicMock):
        self.controller.set_pins(False, True, False, False)
        mock_gpio.output.assert_any_call(
            gpio_controller.PUMP_PIN, gpio_controller.OFF)
        mock_gpio.output.assert_any_call(
            gpio_controller.FAN_ON_PIN, gpio_controller.ON)
        mock_gpio.output.assert_any_call(
            gpio_controller.AC_PIN, gpio_controller.OFF)
        mock_gpio.output.assert_any_call(
            gpio_controller.FURNACE_PIN, gpio_controller.OFF)
        
        print(self.controller.pins_status)

        self.assertFalse(self.controller.pins_status.pump)
        self.assertTrue(self.controller.pins_status.fan_on)
        self.assertFalse(self.controller.pins_status.ac)
        self.assertFalse(self.controller.pins_status.furnace)
        

    @patch("gpio_controller.GPIO")  # Mock the GPIO module
    def test_set_pins__turns_ac_on(self, mock_gpio: unittest.mock.MagicMock):
        self.controller.set_pins(False, False, True, False)
        mock_gpio.output.assert_any_call(
            gpio_controller.PUMP_PIN, gpio_controller.OFF)
        mock_gpio.output.assert_any_call(
            gpio_controller.FAN_ON_PIN, gpio_controller.OFF)
        mock_gpio.output.assert_any_call(
            gpio_controller.AC_PIN, gpio_controller.ON)
        mock_gpio.output.assert_any_call(
            gpio_controller.FURNACE_PIN, gpio_controller.OFF)
        
        self.assertFalse(self.controller.pins_status.pump)
        self.assertFalse(self.controller.pins_status.fan_on)
        self.assertTrue(self.controller.pins_status.ac)
        self.assertFalse(self.controller.pins_status.furnace)
        

    @patch("gpio_controller.GPIO")  # Mock the GPIO module
    def test_set_pins__turns_furnace_on(self, mock_gpio: unittest.mock.MagicMock):
        self.controller.set_pins(False, False, False, True)
        mock_gpio.output.assert_any_call(
            gpio_controller.PUMP_PIN, gpio_controller.OFF)
        mock_gpio.output.assert_any_call(
            gpio_controller.FAN_ON_PIN, gpio_controller.OFF)
        mock_gpio.output.assert_any_call(
            gpio_controller.AC_PIN, gpio_controller.OFF)
        mock_gpio.output.assert_any_call(
            gpio_controller.FURNACE_PIN, gpio_controller.ON)
        
        self.assertFalse(self.controller.pins_status.pump)
        self.assertFalse(self.controller.pins_status.fan_on)
        self.assertFalse(self.controller.pins_status.ac)
        self.assertTrue(self.controller.pins_status.furnace)
