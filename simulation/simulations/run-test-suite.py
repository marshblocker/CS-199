# Run test suite

import json
import os
from datetime import datetime, timedelta
from time import time
from sys import argv

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
            itp = int(argv[4])

            i = str(argv[5])
            test_case = test_suite[i]

            run_with_srp(http_port, contract_addr, itp, test_case, i)

        case 'without-srp':
            http_port = int(argv[2])
            contract_addr = argv[3]

            i = str(argv[4])
            test_case = test_suite[i]

            run_without_srp(http_port, contract_addr, test_case, i)

        case 'without-mndp':
            i = str(argv[2])
            test_case = test_suite[i]

            run_without_mndp(test_case, i)

    print('program ends after {}.'.format(
        timedelta(seconds=time() - start_time)))


def get_test_suite():
    test_suite_path = os.path.join(DIR_PATH, '..', 'test-suite.json')
    with open(test_suite_path, 'r') as f:
        return json.loads(f.read())


def get_malicious_data():
    pass


def run_with_srp(http_port: int, contract_addr: str, itp: int, test_case, i: str):
    gateway = get_gateway(http_port, contract_addr, itp, i)
    gateway.run(test_case)


def run_without_srp(http_port: int, contract_addr: str, test_case, i: str):
    gateway = get_gateway(http_port, contract_addr, None, i)
    gateway.run(test_case)


def run_without_mndp(test_case, i: str):
    pass


def get_gateway(http_port: int, contract_addr: str, itp: int | None, i: str):
    sensor1 = Sensor('Port Area Sensor', 'Port Area')
    sensor2 = Sensor('Sangley Point Sensor', 'Sangley Point')
    sensor3 = Sensor('Science Garden Sensor', 'Science Garden')
    sensors = [sensor1, sensor2, sensor3]

    classifier = Classifier()
    web3 = Web3Client(http_port, contract_addr)
    srp = None if itp is None else SensorRetentionPolicy(itp)

    if type(srp) is SensorRetentionPolicy:
        srp.register_sensor(sensor1.id)
        srp.register_sensor(sensor2.id)
        srp.register_sensor(sensor3.id)

    gateway = Gateway('Metro Manila Cluster', srp, classifier,
                      sensors, web3, START_DATE, END_DATE, i)

    return gateway


if __name__ == '__main__':
    main()
