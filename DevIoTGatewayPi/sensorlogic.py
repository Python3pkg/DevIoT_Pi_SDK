
__author__ = 'tingxxu'

from DevIoTGateway.sensor import Sensor
from DevIoTGateway.sproperty import SProperty
from DevIoTGateway.ssetting import SSetting
from DevIoTGateway.saction import SAction


class SensorLogic:
    @staticmethod
    def run(data):
        pass

    @staticmethod
    def update(sensor, data):
        pass

    @staticmethod
    def action(sensor, data):
        pass

    @staticmethod
    def modify(sensor, data):
        return False

    @staticmethod
    def copy(sensor):
        new_sensor = SensorLogic.copy_with_info(sensor, sensor.id, sensor.name)
        return new_sensor

    @staticmethod
    def copy_with_info(sensor, new_id, new_name):
        new_sensor = Sensor(sensor.kind, new_id, new_name)
        for property_item in sensor.__properties__:
            new_property = SProperty(property_item.name, property_item.type, property_item.range, property_item.value)
            new_sensor.add_property(new_property)

        for setting_item in sensor.__settings__:
            new_setting = SSetting(setting_item.name, setting_item.type, setting_item.range,
                                   setting_item.value, setting_item.required)
            new_sensor.add_setting(new_setting)

        for action_item in sensor.__actions__:
            new_action = SAction(action_item.name)

            for setting_item in action_item.parameters:
                new_setting = SSetting(setting_item.name, setting_item.type, setting_item.range,
                                   setting_item.value, setting_item.required)
                new_action.parameters.append(new_setting)

            new_sensor.add_action(new_action)

        return new_sensor

    @staticmethod
    def copy_with_key(key, sensor):
        new_sensor = SensorLogic.copy_with_info(sensor, key, sensor.name)
        return new_sensor

    @staticmethod
    def update_properties(sensor, properties):
        if len(sensor.__properties__) > 0:
            for sensor_property in sensor.__properties__:
                if sensor_property.name in properties:
                    sensor_property.value = properties[sensor_property.name]

