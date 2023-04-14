import os
from datetime import datetime

import numpy as np
import pandas as pd


class Sensor:
    PAGASA_PATH = os.path.join(os.path.dirname(
        __file__), '..', '..', '..', 'PAGASA')
    # This is needed since Ethereum does not have float type.
    PRECISION = 100

    def __init__(self, sensor_id: str, station: str) -> None:
        self.id = sensor_id
        self.station = station
        self.data = self._get_data()
        # For simulation only.
        self.malicious_data = self._get_malicious_data()

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
        df = df[['YEAR', 'MONTH', 'DAY', 'TMAX',
                 'TMIN', 'TMEAN', 'RH', 'WIND_SPEED']]

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

    def _get_malicious_data(self):
        new_rows = []
        for (year, month), group in self.data.groupby(['YEAR', 'MONTH']):
            tmax_max = group['TMAX'].max()
            tmax_min = group['TMAX'].min()
            tmin_max = group['TMIN'].max()
            tmin_min = group['TMIN'].min()
            tmean_max = group['TMEAN'].max()
            tmean_min = group['TMEAN'].min()
            rh_max = group['RH'].max()
            rh_min = group['RH'].min()
            wind_speed_max = group['WIND_SPEED'].max()
            wind_speed_min = group['WIND_SPEED'].min()
            delta = np.random.randint(1, 51)
            for _, row in group.iterrows():
                new_tmax_val = np.random.choice(
                    [tmax_max, tmax_min]) + delta * np.random.choice([-1, 1])
                new_tmin_val = np.random.choice(
                    [tmin_max, tmin_min]) + delta * np.random.choice([-1, 1])
                new_tmean_val = np.random.choice(
                    [tmean_max, tmean_min]) + delta * np.random.choice([-1, 1])
                new_rh_val = np.random.choice(
                    [rh_max, rh_min]) + delta * np.random.choice([-1, 1])
                new_wind_speed_val = np.random.choice(
                    [wind_speed_max, wind_speed_min]) + delta * np.random.choice([-1, 1])
                new_rows.append([year, month, row['DAY'], new_tmax_val,
                                new_tmin_val, new_tmean_val, new_rh_val, new_wind_speed_val])
        return pd.DataFrame(new_rows, columns=['YEAR', 'MONTH', 'DAY', 'TMAX', 'TMIN', 'TMEAN', 'RH', 'WIND_SPEED'])
