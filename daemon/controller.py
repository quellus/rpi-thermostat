"""
Controller class is responsible for the following things:
 - Keep track of each sensor's temperature
 - Keep track of the state of the thermostat
 - Change the state based on average temperature of the thermostat
 - Write to the GPIO pins
 - Write the state to a JSON file
 - Keep track of average temperature's history over time
"""
# pylint: disable=E0401

import time
import models

from gpio_controller import GpioController

CYCLE_TIME = 2 * 60  # minutes converted to seconds
SENSOR_STALE_TIMEOUT = 1 * 60  # minutes converted to seconds
HISTORY_MAX_ENTRIES = 500
DEFAULT_STATUS = models.Status(
                    pins=models.Pins(pump=False, fan_on=False, ac=False, furnace=False),
                    usable=models.Usable(ac=True, cooler=True, furnace=True),
                    target_temp=72,
                    average_temp=72,
                    manual_override=False,
                    sensors={})

class Controller:
    """Handles keeping track of status and controlling the thermostat"""
    def __init__(self, log):
        self.last_update_time = None
        self.history = []
        self.log = log
        self.gpio_controller = GpioController(log)

        try:
            with open("status.json", "r", encoding="utf-8") as file:
                self.status = models.Status.model_validate_json(file.read())
        # pylint: disable=W0718
        except Exception:
            self.log.info("No status file found. Using default values.")
            print("No status file found. Using default values.")
            self.status = DEFAULT_STATUS


    def get_status(self) -> models.Status:
        """Returns current status of thermostat including temperatures."""
        return self.status


    def get_history(self) -> list:
        """
        Gets the history of the average temperatures
        Returns a list of tuples containing timestamps and temperature.
        """
        return self.history


    def update_sensor_status(self, name: str, temp: float, humidity: float):
        """Adds or updates an entry to the sensors list keyed by `name`."""
        self.status.sensors[name] = {
            "humidity": humidity,
            "temperature": temp,
            "timestamp": time.time()}


    def set_target_temp(self, temp: int):
        """Sets the temperature the thermostat aims for."""
        self.log.info(f"target temp set to {temp}")
        print(f"target temp set to {temp}")
        self.status.target_temp = temp


    def set_usable(self, ac: bool, cooler: bool, furnace: bool):
        """Set which systems the thermostat can use."""
        usable = models.Usable(ac=ac, cooler=cooler, furnace=furnace)
        self.status.usable = usable


    def set_manual_override(self, override: bool, pins: models.Pins):
        """
        Overrides the pins to manually turn them on or off.

        Be careful using this if the system is hooked up to a real HVAC system.
        """
        self.status.manual_override = override
        self.gpio_controller.set_pins(pins.pump, pins.fan_on, pins.ac, pins.furnace)
        self.status.pins = self.gpio_controller.pins_status


    def drive_status(self):
        """
        This function:
        1. Calculates the average temperature for all sensors
        2. Uses the average temperature to set pins accordingly (turning heating/cooling on/off)
        3. Writes the updated status to a file
        """
        try:
            self._remove_stale_sensors()
            self.status.average_temp = self._get_average_temp()
            if not self.status.manual_override:
                if (self.last_update_time is None or time.time() -
                        self.last_update_time >= CYCLE_TIME):
                    temp_diff = self.status.average_temp - self.status.target_temp
                    if self.status.pins.ac or self.status.pins.fan_on:
                        if self.status.usable.ac:
                            if temp_diff <= 1:
                                self.gpio_controller.all_off()
                                self.last_update_time = time.time()
                            else:
                                self.gpio_controller.ac_on()
                        elif self.status.usable.cooler:
                            if temp_diff <= 1:
                                self.gpio_controller.all_off()
                                self.last_update_time = time.time()
                            else:
                                self.gpio_controller.fan_low_on()
                        else:
                            self.gpio_controller.all_off()
                    elif self.status.pins.furnace:
                        if temp_diff >= -1:
                            self.gpio_controller.all_off()
                            self.last_update_time = time.time()
                        else:
                            self.gpio_controller.furnace_on()
                    else:
                        if temp_diff <= -2:
                            self.gpio_controller.furnace_on()
                            self.last_update_time = time.time()
                        elif temp_diff >= 2:
                            if self.status.usable.ac:
                                self.gpio_controller.ac_on()
                                self.last_update_time = time.time()
                            elif self.status.usable.cooler:
                                self.gpio_controller.fan_low_on()
                                self.last_update_time = time.time()
                        else:
                            self.gpio_controller.all_off()
            self.status.pins = self.gpio_controller.pins_status
            self._write_status()
        # pylint: disable=W0718
        except Exception as e:
            self.log.critical(str(e))
            print(str(e))


    def update_history(self):
        """
        Adds the current average temperature to the history list.
        Deletes oldest entries if maximum has been reached.
        """
        self.log.info(f"Updating history {str(self.status.average_temp)}")
        print(f"Updating history {str(self.status.average_temp)}")
        time_obj = time.localtime()
        time_asc = time.asctime(time_obj)
        self.history.append((time_asc, self.status.average_temp))
        if len(self.history) > HISTORY_MAX_ENTRIES:
            to_remove = len(self.history) - HISTORY_MAX_ENTRIES
            self.history = self.history[to_remove:]


    def _remove_stale_sensors(self):
        sensor_keys = self.status.sensors.keys()
        sensors_to_remove = []
        for key in sensor_keys:
            if self.status.sensors[key]["timestamp"] + \
                    SENSOR_STALE_TIMEOUT <= time.time():
                sensors_to_remove.append(key)
        for key in sensors_to_remove:
            self.status.sensors.pop(key)


    def _get_average_temp(self):
        temp_sum = 0
        sensor_keys = self.status.sensors.keys()
        for key in sensor_keys:
            temp_sum += self.status.sensors[key]["temperature"]
        return temp_sum / len(sensor_keys)


    def _write_status(self):
        with open("status.json", "w", encoding="utf-8") as f:
            f.write(self.status.json())
            f.close()
