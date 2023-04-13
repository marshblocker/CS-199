from datetime import datetime
import os
import pandas as pd

GATEWAY_RCVR_ADDR = ("127.0.0.1", 5001)

class SocketlessSensor:
    PAGASA_PATH = os.path.join(os.path.dirname(__file__), '..\\PAGASA')
    PRECISION = 100       # This is needed since Ethereum does not have float type.

    def __init__(self, sensor_id: str, station: str) -> None:
        self.id = sensor_id
        self.station = station
        self.data = self._get_data()

    def transmit_data_entry(
            self,
            date: datetime):
        data_entry: pd.Series = self.data.query(
            f'YEAR == {date.year} and MONTH == {date.month} and DAY == {date.day}'
        ).squeeze().astype(int)
        
        message = {
            'sender': self.id,
            'data': data_entry,
            'date_sent': date
        }

        return message


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