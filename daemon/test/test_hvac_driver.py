# pylint: disable-all

import unittest
from unittest.mock import patch

import hvac_driver
import time

class TestHvacDriver(unittest.TestCase):
    def setUp(self):
        self.log = unittest.mock.MagicMock()
        self.hvac_driver = hvac_driver.HvacDriver(self.log)
        self.hvac_driver.gpio_controller = unittest.mock.MagicMock()


    def test_drive_hvac__drives_after_2_minutes(self):
        self.hvac_driver.last_update_time = time.time() - (2 * 60)
        self.hvac_driver.drive_hvac()

        self.hvac_driver.gpio_controller.all_off.assert_called()


    def test_drive_hvac__doesnt_drive_before_2_minutes(self):
        self.hvac_driver.last_update_time = time.time()
        self.hvac_driver.drive_hvac()

        self.hvac_driver.gpio_controller.fan_low_on.assert_not_called()
        self.hvac_driver.gpio_controller.ac_on.assert_not_called()
        self.hvac_driver.gpio_controller.furnace_on.assert_not_called()
        self.hvac_driver.gpio_controller.all_off.assert_not_called()


    def test_drive_hvac__turns_ac_on(self):
        # TODO
        self.hvac_driver.last_update_time = time.time() - (2 * 60)
        self.hvac_driver.drive_hvac()

        self.hvac_driver.gpio_controller.ac_on.assert_called()


    def test_drive_hvac__keeps_ac_on(self):
        # TODO
        self.hvac_driver.last_update_time = time.time() - (2 * 60)
        self.hvac_driver.drive_hvac()

        self.hvac_driver.gpio_controller.ac_on.assert_not_called()
