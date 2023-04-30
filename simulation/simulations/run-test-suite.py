# Run test suite

import json
import os
from datetime import datetime, timedelta
from time import time
from sys import argv

from classes.gateway_no_mndp import GatewayNoMNDP

from classes.classifier import Classifier
from classes.gateway import Gateway
from classes.sensor import Sensor
from classes.srp import SensorRetentionPolicy
from classes.web3client import Web3Client

DIR_PATH = os.path.dirname(os.path.realpath(__file__))
TEST_CASES = 100
START_DATE = datetime(2011, 1, 1)
END_DATE = datetime(2021, 12, 31)


def main():
    start_time = time()
    test_suite = get_test_suite()

    match argv[1]:
        case 'with-srp':
            http_port = int(argv[2])
            contract_addr = argv[3]
            occ_algo = argv[4]
            decision_threshold = float(argv[5])

            i = str(argv[6])
            test_case = test_suite[i]

            run_with_srp(http_port, contract_addr,
                         test_case, occ_algo, decision_threshold, i)

        case 'without-srp':
            http_port = int(argv[2])
            contract_addr = argv[3]

            i = str(argv[4])
            test_case = test_suite[i]

            run_without_srp(http_port, contract_addr, test_case, i)

        case 'without-mndp':
            http_port = int(argv[2])
            contract_addr = argv[3]

            run_without_mndp(http_port, contract_addr)

    print('program ends after {}.'.format(
        timedelta(seconds=time() - start_time)))


def get_test_suite():
    test_suite_path = os.path.join(DIR_PATH, '..', 'test-suite.json')
    with open(test_suite_path, 'r') as f:
        return json.loads(f.read())


def get_malicious_data():
    pass


def run_with_srp(http_port: int, contract_addr: str, test_case, occ_algo: str, decision_threshold: float, i: str):
    gateway = get_gateway('with-srp', http_port,
                          contract_addr, i, test_case, decision_threshold, occ_algo)
    gateway.run()


def run_without_srp(http_port: int, contract_addr: str, test_case, i: str):
    gateway = get_gateway('without-srp', http_port,
                          contract_addr, i, test_case)
    gateway.run()


def run_without_mndp(http_port: int, contract_addr: str):
    gateway = get_gateway_no_mndp(http_port, contract_addr)
    gateway.run()


def get_gateway(sys_type: str, http_port: int, contract_addr: str, i: str, test_case, decision_threshold: float = 0.0, occ_algo: str = ''):
    sensor1 = Sensor('Port Area Sensor', 'Port Area')
    sensor2 = Sensor('Sangley Point Sensor', 'Sangley Point')
    sensor3 = Sensor('Science Garden Sensor', 'Science Garden')
    sensors = [sensor1, sensor2, sensor3]

    classifier = Classifier(occ_algo, decision_threshold)
    web3 = Web3Client(http_port, contract_addr)
    srp = None if sys_type == 'without-srp' else SensorRetentionPolicy()

    if type(srp) is SensorRetentionPolicy:
        srp.register_sensor(sensor1.id)
        srp.register_sensor(sensor2.id)
        srp.register_sensor(sensor3.id)

    gateway = Gateway('Metro Manila Cluster', srp, classifier,
                      sensors, web3, START_DATE, END_DATE, i, test_case)
    print('decision threshold: {}'.format(
        gateway.classifier.decision_threshold))

    return gateway


def get_gateway_no_mndp(http_port: int, contract_addr: str):
    sensor1 = Sensor('Port Area Sensor', 'Port Area')
    sensor2 = Sensor('Sangley Point Sensor', 'Sangley Point')
    sensor3 = Sensor('Science Garden Sensor', 'Science Garden')
    sensors = [sensor1, sensor2, sensor3]

    web3 = Web3Client(http_port, contract_addr)

    gateway = GatewayNoMNDP('Metro Manila Cluster', web3,
                            sensors, START_DATE, END_DATE)

    return gateway


if __name__ == '__main__':
    main()
