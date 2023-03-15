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

            # TODO: Can we manage to use a ProcessPoolExecutor? An error was
            # encountered wherein the arguments passed to the executor.map
            # iterable must be pickled, but this class instance cannot be pickled.
            # Related link: https://stackoverflow.com/questions/8804830/python-multiprocessing-picklingerror-cant-pickle-type-function
            res = list(map(self._process_data_entry, messages))
            print(self.date, res)

            # with concurrent.futures.ProcessPoolExecutor() as executor:
            #     res = list(executor.map(self._process_data_entry, messages))
            #     print(self.date, res)

            self.date += timedelta(days=1)
            time.sleep(self.send_interval)

    def _process_data_entry(
            self, 
            message: dict[str, str | pd.Series | datetime]) -> bool:
        res = self._classify_data_entry(message)
        res = self._evaluate_sensor_by_SRP()
        res = self._store_data_entry_to_blockchain(message)

        return res
    
    def _classify_data_entry(
            self, 
            message: dict[str, str | pd.Series | datetime]) -> bool:
        return True
    
    def _evaluate_sensor_by_SRP(self) -> bool:
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