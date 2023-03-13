import socket

class SRP_sensor:
    def __init__(self,ID):
        self.__ID = ID
        self.__consecutive_clean = 0
        self.__trust_points = 5
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

class SensorRetentionPolicy:
    # bale list na to nung tuple ng mga sensors
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
    
    def send_to_gateway(self,message):
        # with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        #     s.connect((HOST, PORT))
        #     s.sendall(message.encode())
        pass

    def recieve_from_gateway(self):
        # with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        #     s.bind((HOST, PORT))
        #     s.listen()
        #     conn, addr = s.accept()
        #     with conn:
        #         print(f"Connected by {addr}")
        #         while True:
        #             data = conn.recv(1024)
        #             if len(data) > 0:
        #                 received_message = data.decode()
        #                 print(f"received data = {received_message}")
        #                 return received_message
        pass

    def start(self,isDataMalicious,sensorID):
        if isDataMalicious == False:
            self.add_clean_sensor(sensorID)
            # announce message to store data to blockchain
            self.send_to_gateway("SEND_TO_BLOCKCHAIN")
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
            while(len(self.__malicious_sensors) + len(self.add_clean_sensor) < self.__K):
                # wait for 1 minute and ask for sensorID and data again
                pass
            if len(self.__malicious_sensors >= self.__theta):
                # announce manual investigation
                # tell gateway to cache upcoming sensor data
                self.send_to_gateway("START_MANUAL_INVESTIGATION")
                investigation_result = None # this will be something
                if investigation_result == "legit spike":
                    # tell gateway to drop cached sensor data and restart model
                    return "restart model"
                elif investigation_result == "legit malicious":
                    # tell gateway to remove malicious sensors from the cluster
                    # and store cached data of clean sensors
                    return ("remove then store",self.__malicious_sensors,self.__clean_sensors)
                pass
            else:
                for id in self.__malicious_sensors:
                    self.__malicious_sensors[id].trust_points -= 1
                to_remove = filter(lambda x: x.trust_points == 0, self.__malicious_sensors)
                # tells gateway to remove the sensors in the list called to_remove
                return ("remove_from_cluster",to_remove)