import time
from typing import Optional
import socket
import json
import concurrent.futures
import pandas as pd

from srp import SensorRetentionPolicy

GATEWAY_ADDR = ("127.0.0.1", 5000)

class Gateway:
    def __init__(
            self, 
            id: str, 
            addr: tuple[str, int], 
            srp: Optional[SensorRetentionPolicy]) -> None:
        self.id = id
        self.addr = addr
        self.srp = srp
        self.models = []
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sensors: list[str] = []

    def run(self) -> None:
        self.sock.bind(self.addr)
        print('Start receiving data...')

        while True:
            message, _ = self.sock.recvfrom(4096)
            message = json.loads(message.decode('utf-8'))

            with concurrent.futures.ProcessPoolExecutor() as executor:
                res = list(executor.map(self.process_data, message))
                print(res)

    def process_data(self, data):
        # TODO: Implement model training and eval, srp, blockchain stuff
        time.sleep(10.0) # Kunwari pinaprocess

        return {
            'sensor_id': data['sender'],
            'date': data['date'],
            'is_malicious': True
        }

    def register_sensor(self, sensor_id: str) -> None:
        if sensor_id in self.sensors:
            print('sensor {} is already registered.'.format(sensor_id))
            return
        
        if self.srp:
            self.srp.register_sensor(sensor_id)

        self.sensors.append(sensor_id)
        print('sensor {} successfully registered!'.format(sensor_id))

def main():
    g = Gateway('gateway1', GATEWAY_ADDR, None)

    g.run()

if __name__ == '__main__':
    main()
