import socket
import datetime
import argparse
import random
import json
import time

SEND_INTERVAL = 5.0

def main():    
    device_id, port = parse_command_args()
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    gateway_addr = ("127.0.0.1", port)

    while True:
        random_data = get_random_data(device_id).encode('utf-8')
        bytes = sock.sendto(random_data, gateway_addr)
        print("Sent {} bytes".format(bytes))

        time.sleep(SEND_INTERVAL)

def parse_command_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '-d', 
        metavar='deviceid', 
        type=str, 
        required=True
    )

    parser.add_argument(
        '-p', 
        metavar='port', 
        type=int, 
        required=True
    )

    args = parser.parse_args()
    device_id = args.d
    port = args.p

    return device_id, port

def get_random_data(device_id) -> str:
    current_time = str(datetime.datetime.now())
    random_pos = [random.randint(1, 50), random.randint(1, 50)]
    random_data = json.dumps(
        [
            device_id, 
            random_pos, 
            current_time
        ]
    )

    return random_data


if __name__ == '__main__':
    main()