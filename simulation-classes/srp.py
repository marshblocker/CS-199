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

# NOTE: Minodify ko muna yung code mo para maging compatible sa codebase.
# import socket
# from sensor import SocketlessSensor

# # Notes:

# # For SRP_sensor
# # SRP_sensor is a subclass of the Sensor class from sensor.py
# # I just added three new attributes for SRP

# # For SensorRetentionPolicy
# # Based sa pagkakaintindi ko sa gateway.py
# # Diba si process_data() ay function na ang input ay one piece of data lang
# # Tapos sa loob ni process_data() ang SRP diba
# # So that means one piece of data lang din input kay SRP
# # So ayun assumption sa gawa ko so far

# # Next, I created two special attributes kay SRP
# # The first ay si __message_to_gateway
# # Dito ko iistore yung mga commands ni SRP kay gateway
# # The second is __message_from_gateway
# # Dito naman pwede ilagay ni gateway message niya to gateway
# # by doing this (assuming that the variable my_srp is an instance of the class SensorRetentionPolicy):
# # my_srp.message_from_gateway = "legit spike"

# class SRP_sensor(SocketlessSensor):
#     def __init__(self,id,station):
#         super().__init__(id,station)
#         self.__consecutive_clean = 0
#         self.__trust_points = 5
#         self.__isMalicious = False
    
#     @property
#     def consecutive_clean(self):
#         return self.__consecutive_clean
#     @consecutive_clean.setter
#     def consecutive_clean(self,new_value):
#         self.__consecutive_clean = new_value
#     @property
#     def trust_points(self):
#         return self.__trust_points
#     @trust_points.setter
#     def trust_points(self,new_value):
#         self.__trust_points = new_value
#     @property
#     def isMalicious(self):
#         return self.__isMalicious
#     @isMalicious.setter
#     def isMalicious(self,new_status: bool):
#         self.__isMalicious = new_status

# class SensorRetentionPolicy:
#     # bale list na to nung tuple ng mga sensors
#     def __init__(self,K):
#         self.__K = K
#         self.__theta = self.__K//2
#         self.__malicious_sensors = dict()
#         self.__clean_sensors = dict()
#         self.__message_to_gateway = ""
#         self.__message_from_gateway = ""
#         self.__initial_classification_results: dict[str,bool] = dict()
    
#     @property
#     def K(self):
#         return self.__K
#     @property
#     def theta(self):
#         return self.__theta
#     @property
#     def status(self):
#         return self.__status
#     @property
#     def message_to_gateway(self):
#         return self.__message_to_gateway
#     @property
#     def message_from_gateway(self):
#         return self.__message_from_gateway
#     @property
#     def initial_classification_results(self):
#         return self.__initial_classification_results

#     @initial_classification_results.setter
#     def initial_classification_results(self,new_results):
#         self.__initial_classification_results = new_results

#     @message_from_gateway.setter
#     def message_from_gateway(self,new_message):
#         self.__message_from_gateway = new_message

#     @status.setter
#     def status(self,new_status):
#         self.__status = new_status

#     def add_clean_sensor(self,SENSOR: SocketlessSensor):
#         temp_sensor = SRP_sensor(SENSOR.id,SENSOR.station)
#         self.__clean_sensors[SENSOR.id] = temp_sensor
#         temp_sensor.isMalicious = False

#     def add_malicious_sensor(self,SENSOR: SocketlessSensor):
#         temp_sensor = SRP_sensor(SENSOR.id,SENSOR.station)
#         self.__malicious_sensors[SENSOR.id] = temp_sensor
#         temp_sensor.isMalicious = True

#     def successful_send(self,sensorID):
#         # increment consecutive successful send counter
#         self.__clean_sensors[sensorID].consecutive_clean += 1
#         if self.__clean_sensors[sensorID].consecutive_clean == 5:
#             self.__clean_sensors[sensorID].trust_points += 1
#             # reset consecutive count
#             self.__clean_sensors[sensorID].consecutive_clean = 0
    
#     def store_to_array(self,isDataMalicious,sensorID):
#         if isDataMalicious == False:
#             self.add_clean_sensor(sensorID)
#             # announce message to store data to blockchain
#             self.__message_to_gateway = "SEND TO BLOCKCHAIN"
#             # increment consecutive successful send counter
#             # call successful_send() sa gateway kapag nakapag send sa blockchain
#         else:
#             self.add_malicious_sensor(sensorID)

#     def store_initial_results(self):
#         for sensorID in self.__initial_classification_results:
#             self.store_to_array(self.__initial_classification_results[sensorID],sensorID)

#     def no_manual_investigation(self):
#         if len(self.__malicious_sensors >= self.__theta):
#             # announce manual investigation
#             # tell gateway to cache upcoming sensor data
#             self.__message_to_gateway = "START_MANUAL_INVESTIGATION"
#             return self.__message_to_gateway
#         else:
#             for id in self.__malicious_sensors:
#                 self.__malicious_sensors[id].trust_points -= 1
#             to_remove = list(filter(lambda x: x.trust_points == 0, self.__malicious_sensors))
#             # tells gateway to remove the sensors in the list called to_remove
#             self.__message_to_gateway = ("remove_from_cluster",to_remove)
#             return ("remove_from_cluster",to_remove)
#     def legit_invalid_sensors(self):
#         for id in self.__malicious_sensors:
#             self.__malicious_sensors[id].trust_points -= 1
#         to_remove = list(filter(lambda x: x.trust_points == 0, self.__malicious_sensors))
#         # tells gateway to remove the sensors in the list called to_remove
#         self.__message_to_gateway = ("remove_from_cluster",to_remove)
#         return ("remove_from_cluster",to_remove)