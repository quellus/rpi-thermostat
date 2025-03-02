# pylint: disable-all

import unittest
from unittest.mock import patch
import gpio_controller

class TestGpioController(unittest.TestCase):
    @patch("gpio_controller.GPIO")  # Mock the GPIO module
    def test_init__sets_pin_mode(self, mock_gpio):
        gpio_controller.GpioController()
        mock_gpio.setmode.assert_called_once_with(mock_gpio.BCM)

    @patch("gpio_controller.GPIO")  # Mock the GPIO module
    def test_init__sets_pins_to_out(self, mock_gpio):
        gpio_controller.GpioController()
        mock_gpio.setup.assert_any_call(
            gpio_controller.PUMP_PIN, mock_gpio.OUT, initial=gpio_controller.OFF)
        mock_gpio.setup.assert_any_call(
            gpio_controller.FAN_ON_PIN, mock_gpio.OUT, initial=gpio_controller.OFF)
        mock_gpio.setup.assert_any_call(
            gpio_controller.AC_PIN, mock_gpio.OUT, initial=gpio_controller.OFF)
        mock_gpio.setup.assert_any_call(
            gpio_controller.FURNACE_PIN, mock_gpio.OUT, initial=gpio_controller.OFF)
    
    @patch("gpio_controller.GPIO")  # Mock the GPIO module
    def test_set_pins__sets_pins_false(self, mock_gpio):
        con = gpio_controller.GpioController()
        con.set_pins(False, False, False, False)
        mock_gpio.output.assert_any_call(
            gpio_controller.PUMP_PIN, mock_gpio.HIGH)
        mock_gpio.output.assert_any_call(
            gpio_controller.FAN_ON_PIN, mock_gpio.HIGH)
        mock_gpio.output.assert_any_call(
            gpio_controller.AC_PIN, mock_gpio.HIGH)
        mock_gpio.output.assert_any_call(
            gpio_controller.FURNACE_PIN, mock_gpio.HIGH)

