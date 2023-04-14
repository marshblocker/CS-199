from datetime import datetime, timedelta
from calendar import monthrange
from typing import Optional

import numpy as np
import pandas as pd
from classes.classifier import Classifier
from classes.sensor import Sensor
from classes.srp import SensorRetentionPolicy, SRPEvalResult
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
            end_date: datetime) -> None:
        self.id = gateway_id
        self.srp = srp
        self.classifier = classifier
        self.web3 = web3
        self.sensors = sensors
        self.banned_sensors: list[str] = []
        self.start_date = start_date
        self.end_date = end_date
        self.date = start_date
        self.first_batch_training_end_date = \
            self.compute_first_batch_training_end_date()

    def run(self, test_case) -> None:
        while self.date <= self.end_date and len(self.sensors):
            print('')
            messages = [sensor.transmit_data_entry(
                self.date) for sensor in self.sensors]

            self.inject_malicious_data(messages, test_case)

            if self.date > self.first_batch_training_end_date:
                classification_result = self.classify_data(messages, test_case)
                print('classification result: {}'.format(classification_result))

                if self.srp is not None:
                    newly_banned_sensors, evaluation_result = self.srp.evaluate_sensors(
                        classification_result, self.date)
                    print('newly banned sensors: {}'.format(
                        newly_banned_sensors))
                    print('evaluation result: {}'.format(evaluation_result))

                    match evaluation_result:
                        case SRPEvalResult.Normal | SRPEvalResult.HackedSensors:
                            self.remove_newly_banned_sensors(
                                newly_banned_sensors)
                        case SRPEvalResult.LegitimateReadingShift:
                            self.restart_classifier_training()
                            continue
                        case _:
                            pass
                else:
                    self.handle_no_srp(classification_result)

            # Remove messages from banned sensors
            messages = [
                message for message in messages if message['sender'] not in self.banned_sensors]

            sensor_ids, data_entries, date = self.extract_from_messages(
                messages)
            self.store_data_to_blockchain(sensor_ids, data_entries, date)

            self.date += timedelta(days=1)
            if self.date.day == 1 and self.date != self.start_date:
                self.train_new_classifier()

        if self.date > self.end_date:
            print('Ending program since there are no data left to process.')

        if not len(self.sensors):
            print('Ending program since there are no sensors left in the cluster.')

    def sensor_is_malicious_today(self, sensor_id, test_case):
        if test_case[sensor_id]['atk_date'] != 'None':
            atk_drtn = int(test_case[sensor_id]['atk_drtn'])
            atk_date_start = datetime.strptime(
                test_case[sensor_id]['atk_date'], '%b %d, %Y')
            atk_date_end = atk_date_start + timedelta(days=atk_drtn-1)

            if self.date == atk_date_start:
                print('{} station starts its attack today!'.format(sensor_id))

            return atk_date_start <= self.date <= atk_date_end
        return False

    # For simulation only.
    def inject_malicious_data(self, messages, test_case):
        for sensor in self.sensors:
            # Insert malicious data if the sensor should be malicious today
            if self.sensor_is_malicious_today(sensor.id, test_case):
                malicious_data: pd.Series = sensor.malicious_data.query(
                    f'YEAR == {self.date.year} and MONTH == {self.date.month} and DAY == {self.date.day}'
                ).squeeze().astype(int)
                print('malicious_data: {}'.format(malicious_data))

                for i in range(len(messages)):
                    if messages[i]['sender'] == sensor.id:
                        messages[i]['data'] = malicious_data
                        break

    # Get data_entries in messages and classify them. Returns { id: (result, label), ... }
    def classify_data(self, messages, test_case):
        sensor_ids = [message['sender'] for message in messages]

        data_entries = [message['data'] for message in messages]
        data_entries = pd.DataFrame(data_entries)
        data_entries = data_entries[['TMAX', 'TMIN',
                                     'TMEAN', 'RH', 'WIND_SPEED']].to_numpy()
        
        label = np.full(data_entries.shape[0], 1)
        for i, sensor_id in enumerate(sensor_ids):
            if self.sensor_is_malicious_today(sensor_id, test_case):
                label[i] = -1

        classification_result = self.classifier.classify(
            data_entries, self.date.month)
        classification_result = zip(classification_result, label)
        classification_result = dict(zip(sensor_ids, classification_result))

        return classification_result

    def remove_newly_banned_sensors(self, newly_banned_sensors: list[str]):
        self.banned_sensors += newly_banned_sensors
        self.sensors = [
            sensor for sensor in self.sensors if sensor.id not in self.banned_sensors]

    def restart_classifier_training(self):
        # Clear classifiers
        self.classifier.models = [None for _ in range(12)]

        # Set start date and current date to first day of next month
        curr_month = self.date.month
        curr_year = self.date.year
        updated_curr_month = curr_month + 1 if curr_month != 12 else 1
        updated_curr_year = curr_year if curr_month != 12 else curr_year + 1
        self.start_date = datetime(
            updated_curr_year, updated_curr_month, 1)
        self.date = self.start_date

        # Set first batch training end date to 1 year after start date.
        self.first_batch_training_end_date = self.compute_first_batch_training_end_date()

    def handle_no_srp(self, classification_result):
        malicious_sensors = []
        for sensor in classification_result:
            if classification_result[sensor][0] == -1:
                malicious_sensors.append(sensor)

        self.remove_newly_banned_sensors(malicious_sensors)

    def extract_from_messages(self, messages):
        sensor_ids = [messages[i]['sender'] for i in range(len(messages))]
        data_entries = [messages[i]['data'] for i in range(len(messages))]
        date = messages[0]['date_sent'].strftime("%m/%d/%Y")

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
        training_data = self.web3.read_data_from_blockchain(
            previous_month, year)

        # Remove all data entries from banned sensors and get only the data part.
        training_data = [
            data for data in training_data if data[0] not in self.banned_sensors]
        training_data = [data[1] for data in training_data]

        # Return back to its original precision.
        training_data = np.array(training_data, dtype=float)
        training_data /= self.PRECISION

        self.classifier.train(training_data, previous_month)

    def compute_first_batch_training_end_date(self) -> datetime:
        # This returns the first day of the month a year after the start of
        # first batch training.
        year = self.date.year if self.date.month == 1 else self.date.year + 1
        month = 12 if self.date.month == 1 else self.date.month - 1
        day = monthrange(year, month)[1]
        end_date = datetime(year, month, day)

        return end_date