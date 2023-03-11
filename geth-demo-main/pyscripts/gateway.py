import socket
import json
import argparse
import os
from web3 import Web3
from web3.middleware import geth_poa_middleware


def main():
    contract_addr, port, web3_http_port = parse_command_args()
    contract_abi = get_device_manager_contract_ABI()
    w3 = init_web3(web3_http_port)

    contract = w3.eth.contract(
        address=contract_addr,
        abi=contract_abi
    )

    GATEWAY_ADDR = ("127.0.0.1", port)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(GATEWAY_ADDR)

    print("Start receiving data...")

    while True:
        message, _ = sock.recvfrom(4096)
        random_data = json.loads(message.decode('utf-8'))
        print("Received random data: {}".format(random_data))

        device_id, random_pos, current_time = random_data
        x, y = random_pos

        tx_hash = contract \
            .functions \
            .storeDeviceData(device_id, x, y, current_time) \
            .transact()
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        print("Transaction receipt: {}\n".format(tx_receipt))


def parse_command_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '-a',
        metavar='device_manager_contract_addr',
        type=str,
        required=True,
    )

    parser.add_argument(
        '-p',
        metavar='port',
        type=int,
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
    port = args.p
    web3_http_port = args.w

    return device_manager_contract_addr, port, web3_http_port


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


if __name__ == '__main__':
    main()