from datetime import datetime
from sensor import SocketlessSensor
from gateway import SocketlessGateway

def main():
    sensor1 = SocketlessSensor('Science Garden Sensor', 'Science Garden')
    sensor2 = SocketlessSensor('Port Area Sensor', 'Port Area')
    sensor3 = SocketlessSensor('Sangley Point Sensor', 'Sangley Point')
    gateway = SocketlessGateway(
        gateway_id='Metro Manila Cluster Gateway', 
        srp=None,
        sensors=[sensor1, sensor2, sensor3],
        start_date=datetime(2011, 1, 1),
        end_date=datetime(2013, 1, 1),
        send_interval=5
    )

    gateway.run()

if __name__ == '__main__':
    main()