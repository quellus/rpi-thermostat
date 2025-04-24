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
        with patch.object(self.hvac_driver, '_is_cooling_on', return_value=False):
            with patch.object(self.hvac_driver, '_is_heating_on', return_value=False):
                self.hvac_driver.last_update_time = time.time() - (2 * 61)
                self.hvac_driver.drive_hvac(72, 72)

                self.hvac_driver.gpio_controller.fan_low_on.assert_not_called()
                self.hvac_driver.gpio_controller.cooling_on.assert_not_called()
                self.hvac_driver.gpio_controller.furnace_on.assert_not_called()
                self.hvac_driver.gpio_controller.all_off.assert_called()


    def test_drive_hvac__doesnt_drive_before_2_minutes(self):
        with patch.object(self.hvac_driver, '_is_cooling_on', return_value=False):
            with patch.object(self.hvac_driver, '_is_heating_on', return_value=False):
                self.hvac_driver.last_update_time = time.time()
                self.hvac_driver.drive_hvac(72, 72)

                self.hvac_driver.gpio_controller.fan_low_on.assert_not_called()
                self.hvac_driver.gpio_controller.cooling_on.assert_not_called()
                self.hvac_driver.gpio_controller.furnace_on.assert_not_called()
                self.hvac_driver.gpio_controller.all_off.assert_not_called()


    def test_drive_hvac__updates_last_update_time_when_it_updates_pins(self):
        self.hvac_driver.last_update_time = time.time() - (2 * 61)
        update_time = self.hvac_driver.last_update_time
        self.hvac_driver.drive_hvac(72, 72)

        self.hvac_driver.gpio_controller.fan_low_on.assert_not_called()
        self.hvac_driver.gpio_controller.cooling_on.assert_not_called()
        self.hvac_driver.gpio_controller.furnace_on.assert_not_called()
        self.hvac_driver.gpio_controller.all_off.assert_called()
        self.assertNotEqual(self.hvac_driver.last_update_time, update_time)



    def test_drive_hvac__doesnt_update_time_when_it_doesnt_update_pins(self):
        self.hvac_driver.last_update_time = time.time()
        update_time = self.hvac_driver.last_update_time
        self.hvac_driver.drive_hvac(72, 72)

        self.hvac_driver.gpio_controller.fan_low_on.assert_not_called()
        self.hvac_driver.gpio_controller.cooling_on.assert_not_called()
        self.hvac_driver.gpio_controller.furnace_on.assert_not_called()
        self.hvac_driver.gpio_controller.all_off.assert_not_called()
        self.assertEqual(self.hvac_driver.last_update_time, update_time)


    def test_drive_hvac__turns_ac_on(self):
        with patch.object(self.hvac_driver, '_is_cooling_on', return_value=False):
            with patch.object(self.hvac_driver, '_is_heating_on', return_value=False):
                self.hvac_driver.last_update_time = time.time() - (2 * 61)
                self.hvac_driver.drive_hvac(72, 60)

                self.hvac_driver.gpio_controller.fan_low_on.assert_not_called()
                self.hvac_driver.gpio_controller.cooling_on.assert_called()
                self.hvac_driver.gpio_controller.furnace_on.assert_not_called()
                self.hvac_driver.gpio_controller.all_off.assert_not_called()


    def test_drive_hvac__keeps_ac_on(self):
        with patch.object(self.hvac_driver, '_is_cooling_on', return_value=True):
            with patch.object(self.hvac_driver, '_is_heating_on', return_value=False):
                self.hvac_driver.last_update_time = time.time() - (2 * 60)
                self.hvac_driver.drive_hvac(72, 60)

                self.hvac_driver.gpio_controller.fan_low_on.assert_not_called()
                self.hvac_driver.gpio_controller.cooling_on.assert_called()
                self.hvac_driver.gpio_controller.furnace_on.assert_not_called()
                self.hvac_driver.gpio_controller.all_off.assert_not_called()


    def test_drive_hvac__turns_ac_off(self):
        with patch.object(self.hvac_driver, '_is_cooling_on', return_value=True):
            with patch.object(self.hvac_driver, '_is_heating_on', return_value=False):
                self.hvac_driver.last_update_time = time.time() - (2 * 60)
                self.hvac_driver.drive_hvac(72, 72)

                self.hvac_driver.gpio_controller.fan_low_on.assert_not_called()
                self.hvac_driver.gpio_controller.cooling_on.assert_not_called()
                self.hvac_driver.gpio_controller.furnace_on.assert_not_called()
                self.hvac_driver.gpio_controller.all_off.assert_called()


    def test_drive_hvac__turns_furnace_on(self):
        with patch.object(self.hvac_driver, '_is_cooling_on', return_value=False):
            with patch.object(self.hvac_driver, '_is_heating_on', return_value=False):
                self.hvac_driver.last_update_time = time.time() - (2 * 60)
                self.hvac_driver.drive_hvac(70, 74)

                self.hvac_driver.gpio_controller.fan_low_on.assert_not_called()
                self.hvac_driver.gpio_controller.cooling_on.assert_not_called()
                self.hvac_driver.gpio_controller.furnace_on.assert_called()
                self.hvac_driver.gpio_controller.all_off.assert_not_called()

    
    def test_drive_hvac__keeps_furnace_on(self):
        with patch.object(self.hvac_driver, '_is_cooling_on', return_value=False):
            with patch.object(self.hvac_driver, '_is_heating_on', return_value=True):
                self.hvac_driver.last_update_time = time.time() - (2 * 60)
                self.hvac_driver.drive_hvac(70, 74)

                self.hvac_driver.gpio_controller.fan_low_on.assert_not_called()
                self.hvac_driver.gpio_controller.cooling_on.assert_not_called()
                self.hvac_driver.gpio_controller.furnace_on.assert_called()
                self.hvac_driver.gpio_controller.all_off.assert_not_called()


    def test_drive_hvac__keeps_furnace_on(self):
        with patch.object(self.hvac_driver, '_is_cooling_on', return_value=False):
            with patch.object(self.hvac_driver, '_is_heating_on', return_value=True):
                self.hvac_driver.last_update_time = time.time() - (2 * 60)
                self.hvac_driver.drive_hvac(74, 74)

                self.hvac_driver.gpio_controller.fan_low_on.assert_not_called()
                self.hvac_driver.gpio_controller.cooling_on.assert_not_called()
                self.hvac_driver.gpio_controller.furnace_on.assert_not_called()
                self.hvac_driver.gpio_controller.all_off.assert_called()
