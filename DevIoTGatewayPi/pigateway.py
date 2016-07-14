__author__ = 'tingxxu'

from DevIoTGateway.gateway import Gateway
from DevIoTGateway.sensor import *
from config import config
from sensorlogic import SensorLogic

import os
import time


class PiGateway(Gateway):

    def __init__(self, app_name, iot_address, mqtt_address, deviot_account):
        Gateway.__init__(self, app_name, iot_address, mqtt_address, deviot_account)
        self.__models__ = {}
        self.__logic__ = {}

        self.__import_sensor_model()

        self.__load_sensors()

        self.default_sensor_logic = None

    def run(self):
        Gateway.run(self)

        sensors = self.get_sensors()
        while True:
            for sensor_id, sensor in sensors.iteritems():
                if sensor.kind in self.__logic__:
                    self.__logic__[sensor.kind].update(sensor, None)
                elif self.default_sensor_logic is not None:
                    self.default_sensor_logic.update(sensor, None)

            time.sleep(0.2)

    def __load_sensors(self):
        if "sensors" not in config:
            print("can not find the sensors segment in setting.cfg")
            return
        all_sensors = config["sensors"]
        for sensor_id in all_sensors:
            if self.has_sensor(sensor_id) is False:
                sensor_object = all_sensors[sensor_id]
                if "kind" in sensor_object:
                    sensor_object_kind = sensor_object["kind"]
                    if sensor_object_kind in self.__models__:
                        new_sensor = SensorLogic.copy_with_info(self.__models__[sensor_object_kind],
                                                                sensor_id, sensor_object["name"])
                        if len(new_sensor.__actions__) > 0:
                            self.register_custom_sensor_with_action(new_sensor, self.__custom_action_callback)
                        else:
                            self.register_custom_sensor(new_sensor)
                    else:
                        new_sensor = Sensor(sensor_object_kind, sensor_id, sensor_object["name"])
                        if sensor_object["type"] is "action":
                            self.register_action(sensor_object_kind, sensor_id, sensor_object["name"],
                                                 self.__default_action_callback)
                        else:
                            self.register(sensor_object_kind, sensor_id, sensor_object["name"])
                        self.__sensors__[sensor_id] = new_sensor
                else:
                    print("{0:s} sensor in setting.cfg lost kind property".format(sensor_id))

    def load_sensor_model(self, sensor, logic):
        if sensor.kind not in self.__models__:
            self.__models__[sensor.kind] = sensor
            self.__logic__[sensor.kind] = logic

    def __import_sensor_model(self):
        current_folder = os.getcwd()
        sensors_folder = current_folder + "/sensors"
        sensor_files = os.listdir(sensors_folder)

        for sensor_file in sensor_files:
            if sensor_file.endswith('.py') and sensor_file.endswith('__.py') is False:
                sensor_info = sensor_file.split('.')
                sensor_name = sensor_info[0]
                if len(sensor_name) < 1:
                    continue
                sensor_logic = sensor_name[0].upper() + sensor_name[1:] +"Logic"
                if sensor_name not in self.__models__:
                    import_sensor = "from sensors.{0:s} import {1:s}, {2:s}".format(sensor_name, sensor_name, sensor_logic)

                    exec import_sensor
                    add_sensor = "self.load_sensor_model({0:s},{1:s})".format(sensor_name, sensor_logic)
                    exec add_sensor

    def __default_action_callback(self, sensor_id, action):
        sensor = self.get_sensor(sensor_id)
        self.default_sensor_logic.action(sensor, action)

    def __custom_action_callback(self, sensor_id, action):
        sensor = self.get_sensor(sensor_id)
        self.__logic__[sensor.kind].action(sensor, action)
