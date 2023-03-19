from web3 import Web3

from datetime import datetime
from sensor import SocketlessSensor
from gateway import SocketlessGateway
from web3client import Web3Client
from classifier import Classifier

def main():
    sensor1 = SocketlessSensor('Science Garden Sensor', 'Science Garden')
    sensor2 = SocketlessSensor('Port Area Sensor', 'Port Area')
    sensor3 = SocketlessSensor('Sangley Point Sensor', 'Sangley Point')
    
    contract_addr = Web3.toChecksumAddress('0x92B9874937907011978544DEE6B34c6C23EFd08a')
    web3 = Web3Client(8545, contract_addr)
    classifier = Classifier()
    
    gateway = SocketlessGateway(
        gateway_id='Metro Manila Cluster Gateway', 
        srp=None,
        classifier=classifier,
        sensors=[sensor1, sensor2, sensor3],
        web3=web3,
        start_date=datetime(2011, 1, 1),
        end_date=datetime(2013, 1, 1),
        send_interval=1
    )

    gateway.run()

if __name__ == '__main__':
    main()