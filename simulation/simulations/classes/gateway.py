from datetime import datetime, timedelta
from time import time_ns
from typing import Optional

import numpy as np
import pandas as pd
from classes.classifier import Classifier
from classes.sensor import Sensor
from classes.srp import SensorRetentionPolicy
from classes.utils import LOG, LOG_DUR
from classes.web3client import Web3Client
from pympler import asizeof


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
            i: str,
            test_case) -> None:
        self.id = gateway_id
        self.srp = srp
        self.classifier = classifier
        self.web3 = web3
        self.sensors = sensors
        self.banned_sensors: list[str] = []
        self.start_date = start_date
        self.end_date = end_date
        self.date = start_date

        # Test case number
        self.i = i
        self.test_case = test_case

        self.detection_tracker = {}

    def run(self) -> None:
        while self.date <= self.end_date and len(self.sensors):
            # To separate logs per date
            print('')
            LOG('Date', self.date)

            messages = [sensor.transmit_data_entry(self.date) for sensor in self.sensors]
            processing_start = time_ns()

            self.inject_malicious_data(messages)

            classification_result = {}
            if not self.in_training_phase():
                classification_result = self.classify_data(messages)

                if self.srp is not None:
                    newly_banned_sensors = self.srp.evaluate_sensors(classification_result)
                    LOG('newly banned sensors', newly_banned_sensors)

                    self.update_detection_tracker(newly_banned_sensors)
                    self.log_detection_time(newly_banned_sensors)
                    self.remove_newly_banned_sensors(newly_banned_sensors)
                else:
                    self.handle_no_srp(classification_result)

            # Remove messages from banned sensors
            messages = [
                message for message in messages if message['sender'] not in self.banned_sensors]

            # Remove messages from classified malicious sensors
            if len(classification_result):
                classified_malicious_sensors = []
                for sensor_id in classification_result:
                    if classification_result[sensor_id][0] == -1:
                        classified_malicious_sensors.append(sensor_id)

                messages = [
                    message for message in messages if message['sender'] not in classified_malicious_sensors
                ]

            if len(messages):
                sensor_ids, data_entries, date = self.extract_from_messages(messages)
                self.store_data_to_blockchain(sensor_ids, data_entries, date)

            # Only log processing time when we simultaneously stored three data entries
            # in the blockchain. This behavior is similar to noMNDP.
            if len(messages) == 3:
                duration = time_ns() - processing_start
                LOG('processing time', duration, self.i, 'nanoseconds')

            self.date += timedelta(days=1)
            if self.time_to_train() and len(self.sensors):
                self.train_new_classifier()

        if self.date > self.end_date:
            print('Ending program since there are no data left to process.')

        if not len(self.sensors):
            print('Ending program since there are no sensors left in the cluster.')

        self.log_modified_fscore_components()

    def sensor_is_malicious_today(self, sensor_id):
        if self.test_case[sensor_id]['atk_date'] != 'None':
            atk_drtn = int(self.test_case[sensor_id]['atk_drtn'])
            atk_date_start = datetime.strptime(
                self.test_case[sensor_id]['atk_date'], '%b %d, %Y')
            atk_date_end = atk_date_start + timedelta(days=atk_drtn-1)

            if self.date == atk_date_start:
                print('{} station starts its attack today!'.format(sensor_id))

            return atk_date_start <= self.date <= atk_date_end
        return False

    def inject_malicious_data(self, messages):
        ''' For simulation only. '''
        for sensor in self.sensors:
            # Insert malicious data if the sensor should be malicious today
            if self.sensor_is_malicious_today(sensor.id):
                malicious_data: pd.Series = sensor.malicious_data.query(
                    f'YEAR == {self.date.year} and MONTH == {self.date.month} and DAY == {self.date.day}'
                ).squeeze().astype(int)
                LOG('malicious_data', malicious_data)

                for i in range(len(messages)):
                    if messages[i]['sender'] == sensor.id:
                        messages[i]['data'] = malicious_data
                        break

    def classify_data(self, messages):
        ''' 
        Get data_entries in messages and classify them. 
        Returns { id: (result, label), ... } 
        '''
        sensor_ids = [message['sender'] for message in messages]

        data_entries = [message['data'] for message in messages]
        data_entries = pd.DataFrame(data_entries)

        data_entries = data_entries[['TMAX', 'TMIN',
                                     'TMEAN', 'RH', 'WIND_SPEED']].to_numpy()

        label = np.full(data_entries.shape[0], 1)

        for i, sensor_id in enumerate(sensor_ids):
            if self.sensor_is_malicious_today(sensor_id):
                label[i] = -1

        LOG('data_entries', data_entries)
        LOG('label', label)

        classification_result = self.classifier.classify(data_entries, self.date.month)
        classification_result = list(zip(classification_result, label))

        for res, label in classification_result:
            match (res, label):
                case (1,  1): LOG('tp', 1)
                case (-1, -1): LOG('tn', 1)
                case (1, -1): LOG('fp', 1)
                case (-1,  1): LOG('fn', 1)

        classification_result = dict(zip(sensor_ids, classification_result))

        return classification_result

    def remove_newly_banned_sensors(self, newly_banned_sensors: list[str]):
        self.banned_sensors += newly_banned_sensors
        self.sensors = [
            sensor for sensor in self.sensors if sensor.id not in self.banned_sensors]

    def handle_no_srp(self, classification_result):
        malicious_sensors = []
        for sensor in classification_result:
            if classification_result[sensor][0] == -1:
                malicious_sensors.append(sensor)

        self.remove_newly_banned_sensors(malicious_sensors)

    def extract_from_messages(self, messages):
        sensor_ids = [messages[i]['sender'] for i in range(len(messages))]
        data_entries = [messages[i]['data'] for i in range(len(messages))]
        date = messages[0]['date_sent']

        return sensor_ids, data_entries, date

    def store_data_to_blockchain(self, sensor_ids, data_entries, date):
        data = []
        for data_i in data_entries:
            # We multiply by self.PRECISION to be able to store float number in Ethereum.
            data_i *= self.PRECISION

            tmax = int(data_i['TMAX'])
            tmin = int(data_i['TMIN'])
            tmean = int(data_i['TMEAN'])
            rh = int(data_i['RH'])
            wind_speed = int(data_i['WIND_SPEED'])

            data.append((tmax, tmin, tmean, rh, wind_speed))

        self.web3.store_data_to_blockchain(sensor_ids, date, data)

    def train_new_classifier(self):
        previous_month = 12 if self.date.month == 1 else self.date.month - 1
        year = self.date.year - 1 if self.date.month == 1 else self.date.year

        read_data_start_time = time_ns()
        training_data = self.web3.read_data_from_blockchain(
            previous_month, year)
        LOG_DUR('read data from blockchain', read_data_start_time)

        # Remove all data entries from banned sensors and get only the data part.
        training_data = [
            data for data in training_data if data[0] not in self.banned_sensors]
        training_data = [data[1] for data in training_data]

        # Return back to its original precision.
        training_data = np.array(training_data, dtype=float)
        training_data /= self.PRECISION

        train_start_time = time_ns()
        self.classifier.train(training_data, previous_month)
        LOG_DUR('train classifier', train_start_time)

        if self.classifier.is_complete_models():
            models_size = asizeof.asizeof(self.classifier.models)
            LOG('models memory size', models_size, self.i, 'bytes')

    def update_detection_tracker(self, banned_sensors):
        for sensor_id in banned_sensors:
            self.detection_tracker[sensor_id] = self.date

    def time_to_train(self) -> bool:
        ''' 
        This returns True every first day of the month (except January) of the 
        first year and January of the second year
        '''
        return (self.date.day == 1 \
            and self.date.year == self.start_date.year \
            and self.date != self.start_date) \
            or (self.date == datetime(self.start_date.year + 1, 1, 1))

    def in_training_phase(self):
        return self.date.year == self.start_date.year

    def log_detection_time(self, newly_banned_sensors):
        for sensor in newly_banned_sensors:
            attack_date = self.test_case[sensor]['atk_date']

            if attack_date == 'None':
                continue

            attack_date = datetime.strptime(attack_date, '%b %d, %Y')
            if self.date > attack_date:
                detection_time = (self.date - attack_date).days
                LOG('detection time', detection_time, self.i, 'days')

    def log_modified_fscore_components(self):
        for sensor in self.sensors:
            if self.test_case[sensor.id]['atk_date'] == 'None':
                LOG('tp', sensor.id, self.i)
            else:
                LOG('fp', sensor.id, self.i)

        for sensor in self.banned_sensors:
            if self.test_case[sensor]['atk_date'] == 'None' or self.has_attacked_prematurely(sensor):
                LOG('fn', sensor, self.i)
            else:
                LOG('tn', sensor, self.i)

    def has_attacked_prematurely(self, sensor_id: str) -> bool:
        '''
        This occurs when a sensor is removed from the cluster before its
        attack date.
        '''
        attack_date = datetime.strptime(
            self.test_case[sensor_id]['atk_date'], '%b %d, %Y')
        return (sensor_id in self.detection_tracker) \
            and (self.detection_tracker[sensor_id] < attack_date)
