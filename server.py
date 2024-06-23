import sys
import argparse
import traceback
from socket import socket, AF_INET, SOCK_DGRAM
from packet import *


class Server:

    def __init__(self, ip: str, port: int):
        self._server_address = (ip, port)
        self.socket = socket(AF_INET, SOCK_DGRAM)
        self.socket.bind(self._server_address)

    def run_until_done(self):
        eot_received = False
        print("Waiting for packets...")
        while not eot_received:
            data, address = self.socket.recvfrom(4096)
            pkt = Packet(raw=data)
            print(f"Received: {pkt}")
            ack = Packet(pkt_type=ACK, number=pkt.number, length=0, data=b"")
            print(f"Sending: {ack}")
            self.socket.sendto(ack.serialize(), address)
            if pkt.pkt_type == EOT:
                eot_received = True
        self.socket.close()
        print("EOT received.\nTerminating connection.")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog="server.py", description="Receives a file from a client using a custom stop-and-wait protocol.")
    parser.add_argument("ip")
    parser.add_argument("port", type=int)
    args = parser.parse_args()
    try:
        receiver = Server(args.ip, args.port)
        receiver.run_until_done()
    except KeyboardInterrupt:
        print("\nShutting down receiver...")
    except Exception:
        traceback.print_exc(file=sys.stdout)
