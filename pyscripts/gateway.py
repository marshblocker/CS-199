from datetime import datetime, timedelta
from typing import Optional
import time
import concurrent.futures
import pandas as pd

from srp import SensorRetentionPolicy
from sensor import SocketlessSensor
from web3client import Web3Client
        

class SocketlessGateway:
    def __init__(
            self,
            gateway_id: str,
            srp: Optional[SensorRetentionPolicy],
            sensors: list[SocketlessSensor],
            web3: Web3Client,
            start_date: datetime,
            end_date: datetime,
            send_interval: int) -> None:
        self.id = gateway_id
        self.srp = srp
        self.models = []
        self.web3 = web3
        self.sensors = sensors
        self.start_date = start_date
        self.end_date = end_date
        self.date = start_date
        self.send_interval = send_interval # in seconds.

    def run(self) -> None:
        while self.date <= self.end_date:
            messages = [
                sensor.transmit_data_entry(self.date) for sensor in self.sensors
            ]
            # We need initial results of classifier for all the messages
            # This is in relation to our pseudocode where we check if the length of the malicious array
            # is already equal to the length of the clean array
            if self.srp != None:
                initial_classifier_results: dict[str, bool] = dict(zip([message['sender'] for message in messages],list(map(self._classify_data_entry,messages))))
                self.srp.initial_classification_results = initial_classifier_results
                self.srp.store_initial_results()
            # TODO: Can we manage to use a ProcessPoolExecutor? An error was
            # encountered wherein the arguments passed to the executor.map
            # iterable must be pickled, but this class instance cannot be pickled.
            res = list(map(self._process_data_entry, messages))
        
            # with concurrent.futures.ProcessPoolExecutor() as executor:
            #     res = list(executor.map(self._process_data_entry, messages))
            #     print(self.date, res)

            self.date += timedelta(days=1)
            time.sleep(self.send_interval)

    def _manual_investigation(self) -> bool:
        # cache received data

        # True for legitimate outlier event
        # Otherwise, False
        return True

    def _process_data_entry(
            self, 
            message: dict[str, str | pd.Series | datetime]) -> bool:
        res = self._classify_data_entry(message)
        res = self._evaluate_sensor_by_SRP(res)
        res = self._store_data_entry_to_blockchain(message)

        return res
    
    def _classify_data_entry(
            self, 
            message: dict[str, str | pd.Series | datetime]) -> bool:
        return True
    
    def _evaluate_sensor_by_SRP(self,classification: bool,message: dict[str, str | pd.Series | datetime]) -> bool:
        # self.srp.store_to_array(classification,message["sender"])
        # Is _classify_data_entry going to return True if the data is invalid?
        if classification == False:
            self.srp.successful_send(message['sender'])
            return True     
        before_manual_investigation = self.srp.no_manual_investigation()
        if before_manual_investigation == "START_MANUAL_INVESTIGATION":
            manual_investigation_result = self._manual_investigation()
            if manual_investigation_result == True:
                # drop cached data
                # restart model training
                # gather 1 yr worth of clean data
                pass
            else:
                # remove malicious sensors from the cluster
                for sensor in self.sensors:
                    if self.srp.initial_classification_results[sensor.id] == False:
                        # remove from cluster
                    else:
                        # store cached data of this sensor into the blockchain
                        pass
        else:
            for sensor in before_manual_investigation:
                # remove this sensor because these are the ones whose trust points are already 0
                pass
        return True
    
    def _store_data_entry_to_blockchain(
            self, 
            message: dict[str, str | pd.Series | datetime]) -> bool:
        date = message['date_sent']
        sensor_id = message['sender']
        data = message['data']

        assert type(date) is datetime
        assert type(sensor_id) is str
        assert type(data) is pd.Series

        date_stringified = date.strftime("%m/%d/%Y")

        tmax = data['TMAX']
        tmin = data['TMIN']
        tmean = data['TMEAN']
        rh = data['RH']
        wind_speed = data['WIND_SPEED']

        data_to_store = (date_stringified, tmax, tmin, tmean, rh, wind_speed, sensor_id)

        self.web3.store_data_to_blockchain(data_to_store)
        
        return True