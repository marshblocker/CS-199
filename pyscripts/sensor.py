from datetime import datetime, timedelta
import os
import socket
import json
import time
import pandas as pd

GATEWAY_RCVR_ADDR = ("127.0.0.1", 5001)

class Sensor:
    PAGASA_PATH = os.path.join(os.path.dirname(__file__), '..\\PAGASA')

    def __init__(self, id: str, station: str) -> None:
        self.id = id
        self.station = station
        self.data = self._get_data()
        self.sock: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def transmit_data_entry(
            self, 
            date: datetime, 
            gateway_addr: tuple[str, int]) -> None:
        data = self.data.query(
            f'YEAR == {date.year} and MONTH == {date.month} and DAY == {date.day}'
        )
        data = str(data.iloc[0].to_json())
        data = {
            'sender': self.id,
            'type': 'SENSOR_DATA',
            'date': date.strftime("%m/%d/%Y"),
            'data': data
        }

        data_encoded = json.dumps(data).encode('utf-8')

        bytes_sent = self.sock.sendto(data_encoded, gateway_addr)
        print('{}: Sent SENSOR_DATA ({} bytes) to address {}'.format(self.id, bytes_sent, gateway_addr))

    def register(self, gateway_addr: tuple[str, int]) -> None:
        data = {
            'sender': self.id,
            'type': 'REGISTER',
            'data': {}
        }

        data_encoded = json.dumps(data).encode('utf-8')

        bytes_sent = self.sock.sendto(data_encoded, gateway_addr)        
        print('Sent REGISTER ({} bytes) to address {}'.format(bytes_sent, gateway_addr))

    def _get_data(self) -> pd.DataFrame:
        df = pd.read_csv(os.path.join(self.PAGASA_PATH, self.station + '.csv'))

        # Pre-process data.

        df.sort_values(by=['YEAR', 'MONTH', 'DAY'])

        # Discard RAINFALL and WIND_DIRECTION feature of the dataset.
        df = df[['YEAR', 'MONTH', 'DAY', 'TMAX', 'TMIN', 'TMEAN', 'RH', 'WIND_SPEED']]

        max_invalid_entries = 90

        data_begins_late = not len(df[df['YEAR'] == 2011])
        data_has_many_invalid_entries = \
            len(df[df.isin([-999]).any(axis=1)]) >= max_invalid_entries

        # This data will not be useful for us so we will not use it.
        if data_begins_late or data_has_many_invalid_entries:
            raise Exception(
                f'The chosen PAGASA station ({self.station}) fails the pre-processing step.'
            )

        # Compute the mean of each feature.
        tmax_mean = df[df['TMAX'] != -999]['TMAX'].mean()
        tmin_mean = df[df['TMIN'] != -999]['TMIN'].mean()
        tmean_mean = df[df['TMEAN'] != -999]['TMEAN'].mean()
        rh_mean = df[df['RH'] != -999]['RH'].mean()
        windspeed_mean = df[df['WIND_SPEED'] != -999]['WIND_SPEED'].mean()

        # Replace invalid entries with the mean of the feature they belong to.
        df.loc[df['TMAX'] == -999, 'TMAX'] = tmax_mean
        df.loc[df['TMIN'] == -999, 'TMIN'] = tmin_mean
        df.loc[df['TMEAN'] == -999, 'TMEAN'] = tmean_mean
        df.loc[df['RH'] == -999, 'RH'] = rh_mean
        df.loc[df['WIND_SPEED'] == -999, 'WIND_SPEED'] = windspeed_mean

        return df
    
def main():
    date = datetime(2011, 1, 1)

    s1 = Sensor('sensor1', 'Baguio')
    s2 = Sensor('sensor2', 'Sangley Point')

    for i in range(100):
        s1.transmit_data_entry(date + timedelta(i), GATEWAY_RCVR_ADDR)

    for i in range(100):
        s2.transmit_data_entry(date + timedelta(i), GATEWAY_RCVR_ADDR)


if __name__ == '__main__':
    main()