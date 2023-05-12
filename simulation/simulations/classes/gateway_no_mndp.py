from datetime import datetime, timedelta
from time import time_ns

from classes.sensor import Sensor
from classes.utils import LOG

from classes.web3client import Web3Client


class GatewayNoMNDP:
    # This is needed since Ethereum does not have float type.
    PRECISION = 100.0

    def __init__(
            self,
            gateway_id: str,
            web3: Web3Client,
            sensors: list[Sensor],
            start_date: datetime,
            end_date: datetime):
        self.gateway_id = gateway_id
        self.web3 = web3
        self.sensors = sensors
        self.start_date = start_date
        self.end_date = end_date

        self.date = self.start_date
        self.total_days = (self.end_date - self.start_date).days + 1

        # For simulation only
        self.avg_processing_time = 0.0

    def run(self):
        while self.date <= self.end_date:
            LOG('Date', self.date)

            messages = [sensor.transmit_data_entry(
                self.date) for sensor in self.sensors]
            processing_start = time_ns()

            sensor_ids, data_entries, date = self.extract_from_messages(
                messages)
            self.store_data_to_blockchain(sensor_ids, data_entries, date)

            duration = time_ns() - processing_start
            self.avg_processing_time += duration
            LOG('processing time', duration, '', 'nanoseconds')

            self.date += timedelta(days=1)

        if self.date > self.end_date:
            self.avg_processing_time /= float(self.total_days)
            LOG('average processing time', self.avg_processing_time, '', 'nanoseconds')
            print('Ending program since there are no data left to process.')

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
