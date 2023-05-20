from copy import deepcopy
from datetime import datetime
from enum import Enum, auto

from classes.utils import LOG

MIN_SENSORS_FOR_MANUAL_INVESTIGATION = 2
INITIAL_TRUST_POINTS = 15
MAX_TRUST_POINTS = 30
M = 5


class SRPEvalResult(Enum):
    Normal = auto()
    HackedSensors = auto()
    LegitimateReadingShift = auto()
    Unreachable = auto()


class SensorRetentionPolicy:
    def __init__(self):
        self.K = 0      # number of sensors in the cluster
        self.m = M      # number of consecutive clean data entries to increment a sensor's trust points
        self.sensors_stats = {}
        self.initial_trust_points = INITIAL_TRUST_POINTS
        self.max_trust_points = MAX_TRUST_POINTS

    def register_sensor(self, sensor_id: str) -> None:
        self.sensors_stats[sensor_id] = {
            "consecutive_clean": 0,
            "trust_points": self.initial_trust_points
        }
        self.K += 1

    def unregister_sensor(self, sensor_id: str) -> None:
        self.sensors_stats.pop(sensor_id)
        self.K -= 1

    def evaluate_sensors(self, classification_result):
        # We need to deepcopy this to not mutate the original object
        classif_result = deepcopy(classification_result)
        classif_result = {sensor_id: [classif_result[sensor_id][0],
                                      classif_result[sensor_id][1]] for sensor_id in classif_result}

        # Convert -1 to True and 1 to False
        for sensor_id in classif_result:
            classif_result[sensor_id][0] = classif_result[sensor_id][0] == -1
            classif_result[sensor_id][1] = classif_result[sensor_id][1] == -1

        LOG('classif_result', classif_result)

        # Discard ground truth 
        classif_result = { sensor_id: classif_result[sensor_id][0] for sensor_id in classif_result }

        removed_sensors = self._update_trust_points(classif_result)
        LOG('sensor stats', self.sensors_stats)

        return removed_sensors

    def _update_trust_points(self, classification_result):
        removed_sensors = []
        for sensor_id, is_malicious in classification_result.items():
            if is_malicious:
                self._is_malicious_action(sensor_id, removed_sensors)
            else:
                self._is_not_malicious_action(sensor_id)

        return removed_sensors

    def _is_malicious_action(self, sensor_id, removed_sensors):
        self.sensors_stats[sensor_id]['consecutive_clean'] = 0
        self.sensors_stats[sensor_id]['trust_points'] -= 1

        if not self.sensors_stats[sensor_id]['trust_points']:
            self.unregister_sensor(sensor_id)
            removed_sensors.append(sensor_id)

    def _is_not_malicious_action(self, sensor_id):
        self.sensors_stats[sensor_id]['consecutive_clean'] += 1

        if self.sensors_stats[sensor_id]['consecutive_clean'] == self.m:
            self.sensors_stats[sensor_id]['consecutive_clean'] = 0
            self.sensors_stats[sensor_id]['trust_points'] = min(
                self.sensors_stats[sensor_id]['trust_points'] + 1,
                self.max_trust_points
            )
