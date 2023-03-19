from datetime import datetime, timedelta
from typing import Optional
import time
import concurrent.futures
import numpy as np
import pandas as pd

from srp import SensorRetentionPolicy
from sensor import SocketlessSensor
from web3client import Web3Client
from classifier import Classifier
        

class SocketlessGateway:
    PRECISION = 100.0       # This is needed since Ethereum does not have float type.

    def __init__(
            self,
            gateway_id: str,
            srp: Optional[SensorRetentionPolicy],
            classifier: Classifier,
            sensors: list[SocketlessSensor],
            web3: Web3Client,
            start_date: datetime,
            end_date: datetime,
            send_interval: int) -> None:
        self.id = gateway_id
        self.srp = srp
        self.classifier = classifier
        self.web3 = web3
        self.sensors = sensors
        self.banned_sensors: list[str] = []
        self.start_date = start_date
        self.end_date = end_date
        self.date = start_date
        self.send_interval = send_interval # in seconds.

    def run(self) -> None:
        while self.date <= self.end_date:
            messages = [
                sensor.transmit_data_entry(self.date) for sensor in self.sensors
            ]

            if self.date.year != self.start_date.year:
                classification_res = self._classify_data(messages)
                print(classification_res)

            self._store_data_to_blockchain(messages)

            self.date += timedelta(days=1)

            if self.date.day == 1 and self.date.month != 1:
                self._train_classifier()

    def _classify_data(self, messages) -> dict[str, tuple[int, int]]:
        sensor_ids = [messages[i]['sender'] for i in range(len(messages))]

        data = [messages[i]['data'] for i in range(len(messages))]
        data = pd.DataFrame(data)
        data = data[['TMAX', 'TMIN', 'TMEAN', 'RH', 'WIND_SPEED']].to_numpy()

        label = np.ones(data.shape[0])
        
        res = self.classifier.classify(data, self.date.month)
        res = [(res[i], label[i]) for i in range(len(res))]

        classification_res = dict(zip(sensor_ids, res))

        return classification_res
    
    def _evaluate_sensor_by_SRP(self) -> bool:
        return True
    
    def _store_data_to_blockchain(self, messages) -> bool:
        sensor_ids = [messages[i]['sender'] for i in range(len(messages))]
        date = messages[0]['date_sent'].strftime("%m/%d/%Y")

        data = []
        for i in range(len(messages)):
            data_i = messages[i]['data']

            tmax = data_i['TMAX']
            tmin = data_i['TMIN']
            tmean = data_i['TMEAN']
            rh = data_i['RH']
            wind_speed = data_i['WIND_SPEED']

            # We multiply by self.PRECISION to be able to store float number in Ethereum.
            tmax = int(tmax * self.PRECISION)
            tmin = int(tmin * self.PRECISION)
            tmean = int(tmean * self.PRECISION)
            rh = int(rh * self.PRECISION)
            wind_speed = int(wind_speed * self.PRECISION)

            data.append((tmax, tmin, tmean, rh, wind_speed))

        self.web3.store_data_to_blockchain(sensor_ids, date, data)    
        return True
    
    def _train_classifier(self) -> None:
        previous_month = self.date.month - 1
        training_data = self.web3.read_data_from_blockchain(self.date.month-1, self.date.year)
        # Remove all data entries from banned sensors and get only the data part.
        training_data = list(
            map(
                lambda x: x[1],
                filter(
                    lambda x: x[0] not in self.banned_sensors, 
                    training_data
                )
            )
        )
        training_data = np.array(training_data, dtype=float)
        training_data /= self.PRECISION

        self.classifier.train(training_data, previous_month)
        print(self.classifier.models)