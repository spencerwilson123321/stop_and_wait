import configparser
import sys
import traceback
import logging
from socket import socket, AF_INET, SOCK_DGRAM
from packet import *

logging.basicConfig(filename='receiver.log',
                    encoding='utf-8',
                    level=logging.INFO,
                    format="%(asctime)s - %(message)s")

class Receiver:
    """
        The Receiver class contains all the properties and behaviours needed to implement
        the receiver protocols in the send-and-wait protocol.
    """

    def __init__(self, configuration):
        self.receiver_address = (configuration["receiver"]["ip"], int(configuration["receiver"]["port"]))
        self.sender_address = (configuration["sender"]["ip"], int(configuration["sender"]["port"]))
        self.socket = socket(AF_INET, SOCK_DGRAM)
        self.socket.bind(self.receiver_address)

    def run_until_done(self):
        # The main loop checks for packets and upon receiving a packet, it generates an ack, and sends
        # the ack to the destination. If the packet is the EOT packet then that means the sender has transferred
        # all of it's data and the receiver shuts down.
        eot_received = False
        current_packet_number = 0
        while not eot_received:
            data, address = self.socket.recvfrom(4096)
            pkt = Packet(raw=data)
            ack = Packet(pkt_type=ACK, number=current_packet_number, length=0, data=b"")
            self.socket.sendto(ack.serialize(), self.sender_address())
            if packet.type == EOT:
                eot_received = True
        self.socket.close()
        print("EOT received.\nTerminating connection.")


def main():
    CONFIG = configparser.ConfigParser()
    CONFIG.read("config.ini")
    receiver = Receiver(CONFIG)
    receiver.run_until_done()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\nShutting down receiver...")
    except Exception:
        traceback.print_exc(file=sys.stdout)
