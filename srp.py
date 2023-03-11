class SRP_sensor:
    def __init__(self,ID):
        self.__ID = ID
        self.__consecutive_clean = 0
        self.__trust_points = 0
        self.__isMalicious = False
    
    @property
    def ID(self):
        return self.__ID
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

class SRP:
    def __init__(self,K):
        self.__K = K
        self.__theta = self.__K//2
        self.__malicious_sensors = dict()
        self.__clean_sensors = dict()
    
    @property
    def K(self):
        return self.__K
    @property
    def theta(self):
        return self.__theta

    def add_clean_sensor(self,sensorID):
        temp_sensor = SRP_sensor(sensorID)
        self.__clean_sensors[sensorID] = temp_sensor
        temp_sensor.isMalicious = False

    def add_malicious_sensor(self,sensorID):
        temp_sensor = SRP_sensor(sensorID)
        self.__malicious_sensors[sensorID] = temp_sensor
        temp_sensor.isMalicious = True

    def start(self,isDataMalicious,sensorID):
        if isDataMalicious == False:
            self.add_clean_sensor(sensorID)
            # announce message to store data to blockchain
            # code here
            # increment consecutive successful send counter
            self.__clean_sensors[sensorID].consecutive_clean += 1
            if self.__clean_sensors[sensorID].consecutive_clean == 5:
                self.__clean_sensors[sensorID].trust_points += 1
                # reset consecutive count
                self.__clean_sensors[sensorID].consecutive_clean = 0
        else:
            self.add_malicious_sensor(sensorID)
            # I don't think that this will work
            # I don't know how to implement waiting for all to have sent na in just one call sa start()
            while(len(self.__malicious_sensors) + len(self.add_clean_sensor) < K):
                # wait for 1 minute and ask for sensorID and data again
                pass
            if len(self.__malicious_sensors >= self.__theta):
                # announce manual investigation
                pass
            else:
                for id in self.__malicious_sensors:
                    self.__malicious_sensors[id].trust_points -= 1
                to_remove = filter(lambda x: x.trust_points == 0, self.__malicious_sensors)
                # tells gateway to remove the sensors in the list called to_remove
                return ("remove_from_cluster",to_remove)