import json
import os

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

    def store_data_to_blockchain(self, data) -> None:
        date, temp_max, temp_min, temp_mean, rel_humidity, wind_speed, sensorId = data

        tx_hash = self.contract \
            .functions \
            .storeSensorData(
                date, 
                int(temp_max), 
                int(temp_min), 
                int(temp_mean), 
                int(rel_humidity), 
                int(wind_speed), 
                sensorId
            ) \
            .transact()
        
        tx_receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)
        print("Sent data: {}, block number: {}".format(data, tx_receipt['blockNumber']))

    def _get_contract_ABI(self):
        file_path = os.path.join(
            os.path.abspath(os.path.dirname(__file__)), 
            'contract-abi/SensorDataStorage.json'
        )

        with open(file_path, "r") as f:
            device_manager_contract_ABI = json.loads(f.read())
            return device_manager_contract_ABI

    def _init_web3(self, web3_http_port):
        w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:{}'.format(web3_http_port)))
        assert w3.isConnected(), "w3 is not connected"

        # See https://web3py.readthedocs.io/en/stable/middleware.html#proof-of-authority
        w3.middleware_onion.inject(geth_poa_middleware, layer=0)

        w3.eth.default_account = w3.eth.accounts[0]

        return w3
