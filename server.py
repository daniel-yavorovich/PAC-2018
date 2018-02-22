import time
import asyncio
from decimal import Decimal, getcontext

BIND_ADDRESS = '0.0.0.0'
BIND_PORT = 9999
DECIMAL_PREC = 8


class TimeMeterServer:
    def now(self):
        return Decimal(time.time() * 1000)

    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        now_timestamp = self.now()
        send_timestamp = Decimal(data.decode())

        delay = now_timestamp - send_timestamp

        message = "{now} {delay}".format(now=now_timestamp, delay=delay)

        self.transport.sendto(message.encode(), addr)


def main():
    print('Starting time-meter server')
    loop = asyncio.get_event_loop()

    listen = loop.create_datagram_endpoint(TimeMeterServer, local_addr=(BIND_ADDRESS, BIND_PORT))
    transport, protocol = loop.run_until_complete(listen)

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        print('Server stopped')

    transport.close()
    loop.close()


if __name__ == '__main__':
    getcontext().prec = DECIMAL_PREC
    main()
