import json
import os
from datetime import datetime

from web3 import Web3
from web3.middleware.geth_poa import geth_poa_middleware


class Web3Client:
    def __init__(
            self,
            web3_http_port: int,
            contract_addr) -> None:
        contract_abi = self._get_contract_ABI()
        self.web3 = self._init_web3(web3_http_port)
        self.contract = self.web3.eth.contract(
            address=contract_addr,
            abi=contract_abi
        )

    def store_data_to_blockchain(self, sensor_ids, date, data) -> None:
        for i in range(len(data)):
            data[i] = list(map(lambda x: int(x), data[i]))

        tx_hash = self.contract \
            .functions \
            .storeSensorData(sensor_ids, data, date) \
            .transact()

        tx_receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)
        print("Date: {}, Sent data: {}, block number: {}".format(
            date, data, tx_receipt['blockNumber']))

    def read_data_from_blockchain(self, month: int, year: int):
        event_filter = self.contract \
            .events \
            .storedSensorData \
            .createFilter(
                fromBlock=1,
                toBlock='latest'
            )

        target_data = []
        for event in event_filter.get_all_entries():
            sensor_id = event.args.sensorId
            date = datetime.strptime(event.args.date, "%m/%d/%Y")
            data = event.args.data

            if date.month == month and date.year == year:
                target_data.append((sensor_id, data))

        return target_data

    def _get_contract_ABI(self):
        file_path = os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            'contract-abi/SensorDataStorage.json'
        )

        with open(file_path, "r") as f:
            device_manager_contract_ABI = json.loads(f.read())
            return device_manager_contract_ABI

    def _init_web3(self, web3_http_port):
        w3 = Web3(Web3.HTTPProvider(
            'http://127.0.0.1:{}'.format(web3_http_port)))
        assert w3.isConnected(), "w3 is not connected"

        # See https://web3py.readthedocs.io/en/stable/middleware.html#proof-of-authority
        w3.middleware_onion.inject(geth_poa_middleware, layer=0)

        w3.eth.default_account = w3.eth.accounts[0]

        return w3
