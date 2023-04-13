import os
import json
import argparse
import time
from web3 import Web3
from web3.middleware import geth_poa_middleware

POLLING_INTERVAL = 1.0

def main():
    contract_addr, web3_http_port = parse_command_args()
    contract_abi = get_device_manager_contract_ABI()
    w3 = init_web3(web3_http_port)

    contract = w3.eth.contract(
        address=contract_addr,
        abi=contract_abi
    )

    event_filter = contract \
        .events \
        .storedDeviceData \
        .createFilter(
            fromBlock=1, 
            toBlock='latest'
        )

    for event in event_filter.get_all_entries():
        log_event(event)

    while True:
        for event in event_filter.get_new_entries():
            log_event(event)

        time.sleep(POLLING_INTERVAL)
    
def parse_command_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '-a',
        metavar='device_manager_contract_addr',
        type=str,
        required=True,
    )

    parser.add_argument(
        '-w',
        metavar='web3_http_port',
        type=int,
        required=True,
    )

    args = parser.parse_args()
    device_manager_contract_addr = Web3.toChecksumAddress(args.a)
    web3_http_port = args.w

    return device_manager_contract_addr, web3_http_port

def get_device_manager_contract_ABI():
    file_path = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), 
        'contract-abi/DeviceManagerABI.json'
    )

    with open(file_path, "r") as f:
        device_manager_contract_ABI = json.loads(f.read())
        return device_manager_contract_ABI

def init_web3(web3_http_port):
    w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:{}'.format(web3_http_port)))
    assert w3.isConnected(), "w3 is not connected"

    # See https://web3py.readthedocs.io/en/stable/middleware.html#proof-of-authority
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)

    w3.eth.default_account = w3.eth.accounts[0]

    return w3

def log_event(event):
    print('Sender: {}'.format(event.args.sender))
    print('Data: {}\n'.format(event.args.data))

if __name__ == '__main__':
    main()