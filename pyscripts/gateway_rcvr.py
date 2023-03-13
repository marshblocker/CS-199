from datetime import datetime, timedelta

import socket
import json

GATEWAY_RCVR_ADDR = ("127.0.0.1", 5001)
GATEWAY_ADDR = ("127.0.0.1", 5000)

def main():
    K = 2 # Number of sensors in the cluster
    date = datetime(2011, 1, 1)
    data: dict[str, list[object]] = {} # data = {'01/01/2011': [{s1 data}, {s2 data}]}
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    sock.bind(GATEWAY_RCVR_ADDR)
    print('Start receiving data...')

    while True:
        message, _ = sock.recvfrom(4096)
        message = json.loads(message.decode('utf-8'))

        if message['date'] in data:
            data[message['date']].append(message)
        else:
            data[message['date']] = [message]

        date_str = date.strftime("%m/%d/%Y")

        if len(data[date_str]) == K:
            print(data)
            message_to_pass = data.pop(date_str)
            message_to_pass_encoded = json.dumps(message_to_pass).encode('utf-8')

            sock.sendto(message_to_pass_encoded, GATEWAY_ADDR)
            date += timedelta(days=1)
            # print('Sent data for {}: {}'.format(datetime.now().isoformat(), message_to_pass))

if __name__ == '__main__':
    main()