from copy import deepcopy
from datetime import datetime
from enum import Enum, auto

MAX_TRUST_POINTS = 30
M = 5


class SRPEvalResult(Enum):
    Normal = auto()
    HackedSensors = auto()
    LegitimateReadingShift = auto()
    Unreachable = auto()


class SensorRetentionPolicy:
    def __init__(self, initial_trust_points: int):
        self.K = 0      # number of sensors in the cluster
        self.theta = self.K      # threshold for manual investigation, dependent on K
        self.m = M      # number of consecutive clean data entries to increment a sensor's trust points
        self.sensors_stats = {}
        self.initial_trust_points = initial_trust_points
        self.max_trust_points = MAX_TRUST_POINTS

        # TODO: Implement this.
        # number of times theta condition must be met during the last 10 evaluations
        # before going into manual investigation
        # self.phi = phi

        # self.consec_eval = 0
        # self.consec_manual_inves = 0

    def register_sensor(self, sensor_id: str) -> None:
        self.sensors_stats[sensor_id] = {
            "consecutive_clean": 0,
            "trust_points": self.initial_trust_points
        }
        self.K += 1
        self.theta = self.K

    def unregister_sensor(self, sensor_id: str) -> None:
        self.sensors_stats.pop(sensor_id)
        self.K -= 1
        self.theta = self.K

    def evaluate_sensors(self, classification_result, curr_date: datetime):
        # We need to deepcopy this to not mutate the original object
        classif_result = deepcopy(classification_result)
        classif_result = {sensor_id: [classif_result[sensor_id][0],
                                      classif_result[sensor_id][1]] for sensor_id in classif_result}

        # Convert -1 to True and 1 to False
        for sensor_id in classif_result:
            classif_result[sensor_id][0] = classif_result[sensor_id][0] == -1
            classif_result[sensor_id][1] = classif_result[sensor_id][1] == -1

        print('classif_result: {}'.format(classif_result))

        self.curr_date = curr_date
        malicious_amount = sum(
            [res[0] for res in list(classif_result.values())])

        print('K: {}, malicious_amount: {}, theta: {}'.format(
            self.K, malicious_amount, self.theta))
        if malicious_amount >= self.theta:
            result = self._do_manual_investigation(classif_result)
            print('sensor stats: {}'.format(self.sensors_stats))
            return result
        else:
            classif_result = {
                sensor_id: classif_result[sensor_id][0] for sensor_id in classif_result}
            result = self._update_trust_points(classif_result)
            print('sensor stats: {}'.format(self.sensors_stats))
            return result

    def _do_manual_investigation(self, classification_result):
        # For simulation purposes, if a classification result is correct, then
        # the result of the manual investigation is hack, otherwise its
        # legitimate reading shift
        hacked_sensors = self._get_hacked_sensors(classification_result)

        if hacked_sensors:
            # Remove hacked sensor in list of monitored sensors.
            # The removed sensor will also be removed in self.sensor_stats.
            for sensor_id in hacked_sensors:
                self.unregister_sensor(sensor_id)

            # Possibly increase trust points of non-hacked sensors.
            for sensor_id in self.sensors_stats:
                self._is_not_malicious_action(sensor_id)

            return (hacked_sensors, SRPEvalResult.HackedSensors)
        else:
            # There is a legitimate reading shift.
            return ([], SRPEvalResult.LegitimateReadingShift)

    # Returns a list of hacked sensors. If the list is empty, then
    # no sensors were hacked so the decision must be legitimate
    # reading shift.
    def _get_hacked_sensors(self, classification_result):
        hacked_sensors = []
        for sensor_id in classification_result:
            result = classification_result[sensor_id][0]
            label = classification_result[sensor_id][1]
            if result and label:
                hacked_sensors.append(sensor_id)

        return hacked_sensors

    def _update_trust_points(self, classification_result):
        removed_sensors = []
        for sensor_id, is_malicious in classification_result.items():
            if is_malicious:
                self._is_malicious_action(sensor_id, removed_sensors)
            else:
                self._is_not_malicious_action(sensor_id)

        return (removed_sensors, SRPEvalResult.Normal)

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
