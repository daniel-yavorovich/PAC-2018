import time
import json
import random
import asyncio
import logging
from decimal import Decimal, getcontext

SERVER_ADDRESSES = [
    '104.196.126.59',
    '35.230.17.96',
    '35.188.215.158',
    '35.189.208.200',
    '35.204.131.109',
    '35.198.110.194',
    '35.230.157.166',
    '35.229.222.82',
    # '',
    # '',
    # '',
    # ''
]
SERVER_PORT = 9999
DECIMAL_PREC = 8

TIMING_FILE_NAME = 'timing.txt'
TABLE_INFO_FILE_NAME = 'table_info.txt'
LIST_ORDER_FILE_NAME = 'list_order.json'
SERVERS_USED_FILE_NAME = 'servers_used.json'


class TimeMeterClient:
    def __init__(self, loop):
        self.loop = loop
        self.transport = None

    def now(self):
        return Decimal(time.time() * 1000)

    @property
    def list_order(self):
        try:
            return json.load(open(LIST_ORDER_FILE_NAME, 'r'))
        except:
            return [0, 1, 2]

    def update_list_order(self):
        new_list_order = random.sample(self.list_order, len(self.list_order))
        json.dump(new_list_order, open(LIST_ORDER_FILE_NAME, 'w+'))

    def order_data_indices(self, data):
        new_data = []
        for i in range(3):
            new_data.append(data[self.list_order[i]])
        return new_data

    def __write_timing_data(self, data):
        timing_line = " ".join(data) + '\n'

        timing_file = open(TIMING_FILE_NAME, 'a+')
        timing_file.write(timing_line)

        timing_file.close()

        logging.info('Write timing line: {line}'.format(line=timing_line.strip()))

    def __write_table_info_data(self):
        try:
            lines = open(TABLE_INFO_FILE_NAME, 'r').readlines()
        except:
            lines = []

        if lines:
            last_line = lines[-1]
            last_value_f, last_value_t = last_line.split('-')
            last_value_f = int(last_value_f)
            last_value_t = int(last_value_t)
        else:
            last_value_f = last_value_t = 0

        if last_value_t % 12 == 0:
            lines.append('{f}-{t}\n'.format(f=last_value_t + 1, t=last_value_t + 1))
            self.update_list_order()
        else:
            try:
                lines.pop()
            except:
                pass
            lines.append('{f}-{t}\n'.format(f=last_value_f, t=last_value_t + 1))

        open(TABLE_INFO_FILE_NAME, 'w+').writelines(lines)

    def save_result(self, send_delay, receive_delay, total_delay):
        data = [str(i) for i in self.order_data_indices([send_delay, receive_delay, total_delay])]

        self.__write_timing_data(data)
        self.__write_table_info_data()

    def connection_made(self, transport):
        self.transport = transport

        timestamp = self.now()

        self.transport.sendto(str(timestamp).encode())

    def datagram_received(self, data, addr):
        timestamp_now = self.now()

        receive_timestamp_str, send_delay_str = data.decode().split()

        receive_timestamp = Decimal(receive_timestamp_str)
        send_delay = Decimal(send_delay_str)

        receive_delay = timestamp_now - receive_timestamp
        total_delay = send_delay + receive_delay

        self.save_result(send_delay_str, receive_delay, total_delay)

        self.transport.sendto(str(timestamp_now).encode())

        self.transport.close()

    def error_received(self, exc):
        logging.error('Error received:', exc)

    def connection_lost(self, exc):
        loop = asyncio.get_event_loop()
        loop.stop()


def get_random_server():
    try:
        addresses = json.load(open(SERVERS_USED_FILE_NAME, 'r'))
        assert len(addresses)
    except:
        addresses = random.sample(SERVER_ADDRESSES, len(SERVER_ADDRESSES))

    address = addresses.pop()

    json.dump(addresses, open(SERVERS_USED_FILE_NAME, 'w+'))

    return address


def main():
    logging.basicConfig(level=logging.INFO)

    loop = asyncio.get_event_loop()
    connect = loop.create_datagram_endpoint(lambda: TimeMeterClient(loop),
                                            remote_addr=(get_random_server(), SERVER_PORT))
    transport, protocol = loop.run_until_complete(connect)
    loop.run_forever()
    transport.close()

    loop.close()


if __name__ == '__main__':
    getcontext().prec = DECIMAL_PREC
    main()
