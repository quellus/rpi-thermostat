# pylint: disable-all

import unittest
from unittest.mock import patch, mock_open

import controller
import models

STATUS_STRING = """{
                "pins":{"pump":false,"fan_on":false,"ac":false,"furnace":false},
                "usable":{"ac":false,"cooler":false,"furnace":true},
                "target_temp":12,
                "manual_override":true,
                "average_temp":34,
                "sensors":{
                "Kitchen":{"humidity":27.5,"temperature":75.02,"timestamp":1741480012.6580677}
                }}"""
INVALID_STATUS_STRING = "{}"

class TestController(unittest.TestCase):
    def setUp(self):
        with patch("builtins.open", mock_open(read_data=STATUS_STRING)):
            self.log = unittest.mock.MagicMock()
            self.controller = controller.Controller(self.log)


    def test_init__reads_status_file(self):
        with patch("builtins.open", mock_open(read_data=STATUS_STRING)):
            self.log = unittest.mock.MagicMock()
            self.controller = controller.Controller(self.log)
        self.assertEqual(self.controller.status.target_temp, 12)
        self.assertEqual(self.controller.status.average_temp, 34)
        self.assertEqual(self.controller.status.manual_override, True)


    def test_init__defaults_status_when_file_invalid(self):
        with patch("builtins.open", mock_open(read_data=INVALID_STATUS_STRING)):
            self.log = unittest.mock.MagicMock()
            self.controller = controller.Controller(self.log)
        self.assertEqual(self.controller.status.target_temp, 72)
        self.assertEqual(self.controller.status.average_temp, 72)
        self.assertEqual(self.controller.status.manual_override, False)


    def test_get_status__returns_status_from_file(self):
        with patch("builtins.open", mock_open(read_data=STATUS_STRING)):
            self.log = unittest.mock.MagicMock()
            self.controller = controller.Controller(self.log)
        status = self.controller.get_status()
        self.assertEqual(status, models.Status.model_validate_json(STATUS_STRING))
    

    def test_get_history__returns_history(self):
        history_list = ["heck"]
        self.controller.history = history_list
        history = self.controller.get_history()
        self.assertEqual(history, history_list)

    
    def test_update_sensor_status__adds_new_sensor(self):
        self.assertTrue("test_name" not in self.controller.status.sensors)
        self.controller.update_sensor_status("test_name", 70, 30)
        self.assertTrue("test_name" in self.controller.status.sensors)
        self.assertEqual(self.controller.status.sensors["test_name"]["temperature"], 70)
        self.assertEqual(self.controller.status.sensors["test_name"]["humidity"], 30)
    

    def test_update_sensor_status__updates_existing_sensor(self):
        self.controller.update_sensor_status("test_name", 70, 30)
        self.controller.update_sensor_status("test_name", 75, 35)
        self.assertTrue("test_name" in self.controller.status.sensors)
        self.assertEqual(self.controller.status.sensors["test_name"]["temperature"], 75)
        self.assertEqual(self.controller.status.sensors["test_name"]["humidity"], 35)
