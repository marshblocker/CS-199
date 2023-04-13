from datetime import datetime


class SensorRetentionPolicy:
    def __init__(self, m: int, initial_trust_points: int, max_trust_points: int):
        self.K = 0      # number of sensors in the cluster
        self.theta = self.K      # threshold for manual investigation, dependent on K
        self.m = m      # number of consecutive clean data entries to increment a sensor's trust points
        self.sensors_stats = {}
        self.initial_trust_points = initial_trust_points
        self.max_trust_points = max_trust_points

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

    def evaluate_sensors(self, classification_res, curr_date: datetime):
        print(self.sensors_stats)
        self.curr_date = curr_date
        malicious_amount = sum([
            1 for is_malicious in list(classification_res.values()) if is_malicious
        ])

        if self.K > 1 and malicious_amount >= self.theta:
            return self._do_manual_investigation()
        else:
            return self._update_trust_points(classification_res)
        
    def _do_manual_investigation(self):
        removed_sensors = []
        print('Commence manual investigation...')
        investigation_res = '' 
        
        while True:
            investigation_res = input("Result of manual investigation ('s' for legitimate spike/dip in sensor readings and 'h' for hacking of sensors): ")
            if investigation_res.lower() in ['s', 'h']:
                investigation_res = investigation_res.lower()
                break

        if investigation_res  == 's':
            message_back = 'Retrain classifier from scratch'
            return (removed_sensors, message_back)
        elif investigation_res == 'h':
            invalid_input = True
            while invalid_input:
                hacked_sensors = input('List the ids of all the hacked sensors (format: <sensor_id_1>,<sensorid2>,...): ')
                hacked_sensors = hacked_sensors.split(',')

                sensors = list(self.sensors_stats.keys())
                for sensor in hacked_sensors:
                    if sensor not in sensors:
                        print('{} is not in the list of sensors.'.format(sensor))
                        break
                else:
                    for sensor_id in hacked_sensors:
                        self.unregister_sensor(sensor_id)
                        removed_sensors.append(sensor_id)

                        print("{}: '{}' is removed from sensors since it was hacked!".format(self.curr_date, sensor_id))
                    
                    for sensor_id in self.sensors_stats:
                        self._is_not_malicious_action(sensor_id)

                    message_back = 'Hacked sensors'
                    return (removed_sensors, message_back)
        return ([], 'Cannot be reached')

    def _update_trust_points(self, classification_res):
        removed_sensors = []
        for sensor_id, is_malicious in classification_res.items():
                if is_malicious:
                    self._is_malicious_action(sensor_id, removed_sensors)
                else:
                    self._is_not_malicious_action(sensor_id)

        message_back = 'Updated trust points'
        return (removed_sensors, message_back)
    
    def _is_malicious_action(self, sensor_id, removed_sensors):
        self.sensors_stats[sensor_id]['consecutive_clean'] = 0
        self.sensors_stats[sensor_id]['trust_points'] -= 1

        if self.sensors_stats[sensor_id]['trust_points'] == 0:
            self.unregister_sensor(sensor_id)
            removed_sensors.append(sensor_id)
            self.K -= 1
            self.theta = self.K

            print("{}: '{}' is removed from the cluster since its trust points have reached 0!".format(self.curr_date, sensor_id))
    
    def _is_not_malicious_action(self, sensor_id):
        self.sensors_stats[sensor_id]['consecutive_clean'] += 1
                    
        if self.sensors_stats[sensor_id]['consecutive_clean'] == self.m:
            self.sensors_stats[sensor_id]['consecutive_clean'] = 0
            self.sensors_stats[sensor_id]['trust_points'] = min(
                self.sensors_stats[sensor_id]['trust_points'] + 1, 
                self.max_trust_points
            )