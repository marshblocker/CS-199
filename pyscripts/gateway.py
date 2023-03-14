from datetime import datetime, timedelta
from typing import Optional
import time
import concurrent.futures
import pandas as pd

from srp import SensorRetentionPolicy
from sensor import SocketlessSensor

class SocketlessGateway:
    def __init__(
            self,
            gateway_id: str,
            srp: Optional[SensorRetentionPolicy],
            sensors: list[SocketlessSensor],
            start_date: datetime,
            end_date: datetime,
            send_interval: int) -> None:
        self.id = gateway_id
        self.srp = srp
        self.models = []
        self.sensors = sensors
        self.start_date = start_date
        self.end_date = end_date
        self.date = start_date
        self.send_interval = send_interval # in seconds.

    def run(self) -> None:
        while self.date <= self.end_date:
            data_entries = [
                sensor.transmit_data_entry(self.date) for sensor in self.sensors
            ]

            with concurrent.futures.ProcessPoolExecutor() as executor:
                res = list(executor.map(self.process_data_entries, data_entries))
                print(self.date, res)

            self.date += timedelta(days=1)
            time.sleep(self.send_interval)

    def process_data_entries(self, data_entries: list[pd.Series]) -> bool:
        return True
