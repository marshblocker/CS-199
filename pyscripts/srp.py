import socket
from sensor import Sensor

# Notes:

# For SRP_sensor
# SRP_sensor is a subclass of the Sensor class from sensor.py
# I just added three new attributes for SRP

# For SensorRetentionPolicy
# Based sa pagkakaintindi ko sa gateway.py
# Diba si process_data() ay function na ang input ay one piece of data lang
# Tapos sa loob ni process_data() ang SRP diba
# So that means one piece of data lang din input kay SRP
# So ayun assumption sa gawa ko so far

# Next, I created two special attributes kay SRP
# The first ay si __message_to_gateway
# Dito ko iistore yung mga commands ni SRP kay gateway
# The second is __message_from_gateway
# Dito naman pwede ilagay ni gateway message niya to gateway
# by doing this (assuming that the variable my_srp is an instance of the class SensorRetentionPolicy):
# my_srp.message_from_gateway = "legit spike"

class SRP_sensor(Sensor):
    def __init__(self,id,station):
        super().__init__(id,station)
        self.__consecutive_clean = 0
        self.__trust_points = 5
        self.__isMalicious = False
    
    @property
    def consecutive_clean(self):
        return self.__consecutive_clean
    @consecutive_clean.setter
    def consecutive_clean(self,new_value):
        self.__consecutive_clean = new_value
    @property
    def trust_points(self):
        return self.__trust_points
    @trust_points.setter
    def trust_points(self,new_value):
        self.__trust_points = new_value
    @property
    def isMalicious(self):
        return self.__isMalicious
    @isMalicious.setter
    def isMalicious(self,new_status: bool):
        self.__isMalicious = new_status

class SensorRetentionPolicy:
    # bale list na to nung tuple ng mga sensors
    def __init__(self,K):
        self.__K = K
        self.__theta = self.__K//2
        self.__malicious_sensors = dict()
        self.__clean_sensors = dict()
        self.__message_to_gateway = ""
        self.__message_from_gateway = ""
    
    @property
    def K(self):
        return self.__K
    @property
    def theta(self):
        return self.__theta
    @property
    def status(self):
        return self.__status

    @status.setter
    def status(self,new_status):
        self.__status = new_status

    def add_clean_sensor(self,SENSOR: Sensor):
        temp_sensor = SRP_sensor(SENSOR.id,SENSOR.station)
        self.__clean_sensors[SENSOR.id] = temp_sensor
        temp_sensor.isMalicious = False

    def add_malicious_sensor(self,SENSOR: Sensor):
        temp_sensor = SRP_sensor(SENSOR.id,SENSOR.station)
        self.__malicious_sensors[SENSOR.id] = temp_sensor
        temp_sensor.isMalicious = True

    def successful_send(self,sensorID):
        # increment consecutive successful send counter
        self.__clean_sensors[sensorID].consecutive_clean += 1
        if self.__clean_sensors[sensorID].consecutive_clean == 5:
            self.__clean_sensors[sensorID].trust_points += 1
            # reset consecutive count
            self.__clean_sensors[sensorID].consecutive_clean = 0
    
    def store_to_array(self,isDataMalicious,sensorID):
        if isDataMalicious == False:
            self.add_clean_sensor(sensorID)
            # announce message to store data to blockchain
            self.__message_to_gateway = "SEND TO BLOCKCHAIN"
            # increment consecutive successful send counter
            # call successful_send() sa gateway kapag nakapag send sa blockchain
        else:
            self.add_malicious_sensor(sensorID)

    def proceed_to_investigation(self):
        if len(self.__malicious_sensors >= self.__theta):
            # announce manual investigation
            # tell gateway to cache upcoming sensor data
            self.__message_to_gateway = "START_MANUAL_INVESTIGATION"
            self.__message_from_gateway = None # the value of this should be changed sa gateway.py
            if self.__message_from_gateway == "legit spike":
                # tell gateway to drop cached sensor data and restart model
                self.__message_to_gateway = "restart model"
                return "restart model"
            elif self.__message_from_gateway == "legit malicious":
                # tell gateway to remove malicious sensors from the cluster
                # and store cached data of clean sensors
                self.__message_to_gateway = ("remove then store",self.__malicious_sensors,self.__clean_sensors)
                return ("remove then store",self.__malicious_sensors,self.__clean_sensors)
        else:
            for id in self.__malicious_sensors:
                self.__malicious_sensors[id].trust_points -= 1
            to_remove = filter(lambda x: x.trust_points == 0, self.__malicious_sensors)
            # tells gateway to remove the sensors in the list called to_remove
            self.__message_to_gateway = ("remove_from_cluster",to_remove)
            return ("remove_from_cluster",to_remove)