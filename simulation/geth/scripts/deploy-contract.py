import os
from sys import argv

from web3 import Web3
from web3.middleware.geth_poa import geth_poa_middleware

DIR_PATH = os.path.dirname(os.path.realpath(__file__))
HTTP_PORT = argv[1]


def main():
    w3 = get_web3()

    abi, bytecode = get_contract_data()
    contract = w3.eth.contract(abi=abi, bytecode=bytecode)

    tx_hash = contract.constructor().transact()
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    contract = w3.eth.contract(address=tx_receipt['contractAddress'], abi=abi)
    print(contract.address)
    
def get_web3():
    w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:{}'.format(HTTP_PORT)))
    assert w3.isConnected(), "w3 is not connected"

    # See https://web3py.readthedocs.io/en/stable/middleware.html#proof-of-authority
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)

    w3.eth.default_account = w3.eth.accounts[0]

    return w3


def get_contract_data():
    abi_path = os.path.join(DIR_PATH, '..', 'contracts',
                            'SensorDataStorageABI.json')
    bytecode_path = os.path.join(
        DIR_PATH, '..', 'contracts', 'SensorDataStorageBytecode.txt')
    
    abi = ''
    bytecode = ''

    with open(abi_path, 'r') as f:
        abi = f.read()

    with open(bytecode_path, 'r') as f:
        bytecode = f.read()

    return abi, bytecode

if __name__ == '__main__':
    main()
