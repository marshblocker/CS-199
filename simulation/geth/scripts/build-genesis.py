# Builds genesis.json

import json
import os

BALANCE = "5000000000000000000000"
DIR_PATH = os.path.dirname(os.path.realpath(__file__))

def main():
    genesis = get_init_genesis()
    account_address = get_account_address()

    genesis['extradata'] = '0x0000000000000000000000000000000000000000000000000000000000000000' + account_address + '0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000'
    genesis['alloc'][account_address] = { 'balance': BALANCE }

    genesis_path = os.path.join(DIR_PATH, '..', 'genesis.json')
    with open(genesis_path, 'w') as f:
        json.dump(genesis, f, indent=4)

    print(account_address)

def get_init_genesis():
    return {
        "config": {
        "chainId": 123,
        "homesteadBlock": 0,
        "eip150Block": 0,
        "eip155Block": 0,
        "eip158Block": 0,
        "byzantiumBlock": 0,
        "constantinopleBlock": 0,
        "petersburgBlock": 0,
        "istanbulBlock": 0,
        "berlinBlock": 0,
        "clique": {
            "period": 5,
            "epoch": 30000
        }
        },
        "difficulty": "1",
        "gasLimit": "5000000",
        "extradata": "",
        "alloc": {}
    }

def get_account_address():
    keystore_path = os.path.join(DIR_PATH, '..', 'keystore')
    account_file_name = os.listdir(keystore_path)[0]
    account_file_path = os.path.join(keystore_path, account_file_name)

    with open(account_file_path, 'r') as f:
        data = f.read()
        data = json.loads(data)
        account_address = data['address']

        return account_address
    
if __name__ == '__main__':
    main()