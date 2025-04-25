"""Handles when the cooling and heating systems turn off/on"""

import time

from gpio_controller import GpioController

CYCLE_TIME = 2 * 60  # minutes converted to seconds

class HvacDriver():
    """Handles when the cooling and heating systems turn off/on"""
    def __init__(self, gpio_controller: GpioController, log):
        self.log = log
        self.last_update_time = None
        self.gpio_controller = gpio_controller


    def drive_hvac(self, average_temperature, target_temperature):
        """
        If 2 minutes has passed:
            compares difference between set temperature and average temperature
            then turns on/off the appropriate system
        """
        if (self.last_update_time is None or time.time() - self.last_update_time >= CYCLE_TIME):
            temp_diff = average_temperature - target_temperature
            if self._is_cooling_on():
                if temp_diff <= 1:
                    self.gpio_controller.all_off()
                else:
                    self.gpio_controller.cooling_on()
            elif self._is_heating_on():
                if temp_diff >= -1:
                    self.gpio_controller.all_off()
                else:
                    self.gpio_controller.furnace_on()
            else:
                if temp_diff >= 2:
                    self.gpio_controller.cooling_on()
                elif temp_diff <= -2:
                    self.gpio_controller.furnace_on()
                else:
                    self.gpio_controller.all_off()
            self._update()


    def _update(self):
        self.last_update_time = time.time()


    def _is_cooling_on(self) -> bool:
        ac_on = self.gpio_controller.pins_status.ac
        cooler_on = self.gpio_controller.pins_status.fan_on
        return ac_on or cooler_on


    def _is_heating_on(self) -> bool:
        return self.gpio_controller.pins_status.furnace
