from datetime import datetime, timedelta
from typing import Optional

import numpy as np
import pandas as pd
from classes.classifier import Classifier
from classes.sensor import Sensor
from classes.srp import SensorRetentionPolicy
from classes.web3client import Web3Client


class Gateway:
    # This is needed since Ethereum does not have float type.
    PRECISION = 100.0

    def __init__(
            self,
            gateway_id: str,
            srp: Optional[SensorRetentionPolicy],
            classifier: Classifier,
            sensors: list[Sensor],
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
        self.send_interval = send_interval  # in seconds.
        self.first_batch_training_end_date = \
            self._compute_first_batch_training_end_date()

        print('Training first batch of OCC models from {} to {}'.format(
            self.start_date, self.first_batch_training_end_date
        ))

    def run(self) -> None:
        while self.date <= self.end_date or len(self.sensors):
            messages = [
                sensor.transmit_data_entry(self.date) for sensor in self.sensors
            ]

            classification_res = {}
            if self.date > self.first_batch_training_end_date:
                classification_res = self._classify_data(messages)

                if self.srp != None:
                    removed_sensors, message_back = \
                        self._evaluate_sensors(classification_res)

                    print('Message by SRP: {}, removed sensors: {}'.format(
                        message_back, removed_sensors))

                    if message_back in ['Updated trust points', 'Hacked sensors']:
                        self.banned_sensors += removed_sensors
                        self.sensors = list(filter(
                            lambda s: s.id not in removed_sensors,
                            self.sensors
                        ))
                    elif message_back == 'Retrain classifier from scratch':
                        # Remove all trained models, update start_date and date to the
                        # first day of the next month and first_batch_training_end_date
                        # a year after that.
                        self.classifier.models = [None for _ in range(12)]

                        curr_month = self.date.month
                        curr_year = self.date.year
                        updated_curr_month = curr_month + 1 if curr_month != 12 else 1
                        updated_curr_year = curr_year if curr_month != 12 else curr_year + 1
                        self.start_date = datetime(
                            updated_curr_year, updated_curr_month, 1)
                        self.date = self.start_date
                        self.first_batch_training_end_date = self._compute_first_batch_training_end_date()

                        print('Retraining the models from {} to {}'.format(
                            self.date, self.first_batch_training_end_date
                        ))

                        continue
                else:
                    malicious_sensors = []
                    for sensor in classification_res:
                        if classification_res[sensor][0] == -1:
                            malicious_sensors.append(sensor)

                    self.banned_sensors += malicious_sensors
                    self.sensors = list(filter(
                        lambda s: s.id not in malicious_sensors,
                        self.sensors
                    ))

                    print("Removed sensors: {}".format(malicious_sensors))

            messages = list(filter(
                lambda x: x['sender'] not in self.banned_sensors,
                messages
            ))

            self._store_data_to_blockchain(messages)

            self.date += timedelta(days=1)

            if self.date.day == 1 and self.date != self.start_date:
                self._train_classifier()

        if not len(self.sensors):
            print('Ending program since there are no sensors left in the cluster.')

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
        previous_month = 12 if self.date.month == 1 else self.date.month - 1
        year = self.date.year - 1 if self.date.month == 1 else self.date.year
        training_data = self.web3.read_data_from_blockchain(
            previous_month, year)
        print('training_data: {}'.format(training_data))
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

    def _evaluate_sensors(self, classification_res):
        assert self.srp is not None

        class_res = {}
        for sensor_id in classification_res:
            class_res[sensor_id] = True \
                if classification_res[sensor_id][0] == -1 else False

        return self.srp.evaluate_sensors(class_res, self.date)

    def _compute_first_batch_training_end_date(self) -> datetime:
        # This returns the first day of the month a year after the start of
        # first batch training.
        date_after = self.start_date + timedelta(days=365)
        month = date_after.month
        year = date_after.year
        end_date = datetime(year, month, 1) - timedelta(days=1)

        return end_date
