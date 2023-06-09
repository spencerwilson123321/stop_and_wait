import configparser
import sys
import traceback
from socket import socket, AF_INET, SOCK_DGRAM
from packet import *


class Receiver:

    def __init__(self, configuration):
        self.receiver_address = (configuration["receiver"]["ip"], int(configuration["receiver"]["port"]))
        self.sender_address = (configuration["sender"]["ip"], int(configuration["sender"]["port"]))
        self.socket = socket(AF_INET, SOCK_DGRAM)
        self.socket.bind(self.receiver_address)

    def run_until_done(self):
        eot_received = False
        print("Waiting for packets...")
        while not eot_received:
            data, address = self.socket.recvfrom(4096)
            pkt = Packet(raw=data)
            print(f"Received: {pkt}")
            ack = Packet(pkt_type=ACK, number=pkt.number, length=0, data=b"")
            print(f"Sending: {ack}")
            self.socket.sendto(ack.serialize(), self.sender_address)
            if pkt.pkt_type == EOT:
                eot_received = True
        self.socket.close()
        print("EOT received.\nTerminating connection.")


if __name__ == '__main__':
    try:
        CONFIG = configparser.ConfigParser()
        CONFIG.read("config.ini")
        receiver = Receiver(CONFIG)
        receiver.run_until_done()
    except KeyboardInterrupt:
        print("\nShutting down receiver...")
    except Exception:
        traceback.print_exc(file=sys.stdout)
