import traceback
import sys
import logging
import time
import configparser
from socket import socket, AF_INET, SOCK_DGRAM
from packet import *

logging.basicConfig(filename='sender.log',
                    encoding='utf-8',
                    level=logging.INFO,
                    format="%(asctime)s - %(message)s")


class Timer:

    def __init__(self):
        self._start_time = None

    def start(self):
        self._start_time = time.perf_counter()
    
    def elapsed_time(self):
        elapsed_time = time.perf_counter() - self._start_time
        return float(elapsed_time*1000)

class Sender:

    # Retransmission Timer Constants
    ALPHA = 0.125
    BETA = 0.25
    K = 4
    BUFFSIZE = 4096

    def __init__(self, configuration):
        self.receiver_address = (configuration["receiver"]["ip"], int(configuration["receiver"]["port"]))
        self.sender_address = (configuration["sender"]["ip"], int(configuration["sender"]["port"]))
        self.timer = Timer()

        self.rto = 1.0 # Retransmission Timeout Threshold
        self.srtt = None # Smoothed RTT
        self.vrtt = None # RTT Variance

        self.socket = socket(AF_INET, SOCK_DGRAM)
        self.socket.bind(self.sender_address)
        self.socket.setblocking(0)

        self.PAYLOAD_SIZE = 255
        self.current_packet_number = 0
        self.timed_out = False

    def on_rtt_measured(self, rtt):
        if self.srtt is None:
            self.srtt = rtt
            self.vrtt = rtt/2
            self.rto = self.srtt + self.K*self.vrtt
        else:
            self.vrtt = (1-self.BETA)*self.vrtt + self.BETA*abs(self.srtt - rtt)
            self.srtt = (1-self.ALPHA)*self.srtt + self.ALPHA*rtt
            self.rto = self.srtt + self.K*self.vrtt
    
    def on_timeout(self):
        self.timed_out = True
        self.rto *= 2 # Double Retransmission Timeout Threshold

    def load_data(self, path) -> bytes:
        with open(path, "rb") as f:
            data = f.read()
        return data

    def send(self, packet):
        self.socket.sendto(packet.serialize(), self.receiver_address)
        start = time.perf_counter()
        waiting = True
        while waiting:
            if time.perf_counter() - start >= self.rto:
                self.on_timeout()
                self.socket.sendto(packet.serialize(), self.receiver_address)
                start = time.perf_counter()
            try:
                response, address = self.socket.recvfrom(self.BUFFSIZE)
                timestamp = time.perf_counter()
                ack = Packet(raw=response)
                print(f"Received: {ack}")
                if ack.number == packet.number:
                    waiting = False
                    # Update RTT if we did not timeout.
                    if not self.timed_out:
                        rtt = timestamp - start
                        self.on_rtt_measured(rtt)
                    # Return the number of bytes acked.
                    self.timed_out = False
                    return packet.length
            except Exception:
                continue
    
    def increment(self, number):
        if number == 255:
            return 0
        else:
            return number + 1

    def transmit(self, path=""):

        data = self.load_data(path)
        bytes_acked = 0
        total_bytes = len(data)
        current_packet_number = 0

        while bytes_acked < total_bytes:
            
            payload = data[0:self.PAYLOAD_SIZE]
            data = data[self.PAYLOAD_SIZE:]

            pkt = Packet(DATA, current_packet_number, len(payload), payload)
            print(f"Sending: {pkt}")
            bytes_acked += self.send(pkt)
            current_packet_number = self.increment(current_packet_number)

        eot = Packet(pkt_type=EOT, number=current_packet_number, length=0, data=b"")
        print(f"Sending: {eot}")
        num_acked = self.send(eot)

        print("EOT received.\nTerminating transmission.")
        self.socket.close()

if __name__ == '__main__':

    try:
        CONFIG = configparser.ConfigParser()
        CONFIG.read("config.ini")
        sender = Sender(CONFIG)
        sender.transmit(sys.argv[1])
    except KeyboardInterrupt:
        print("\nShutting down sender...")
    except Exception:
        traceback.print_exc(file=sys.stdout)
    sys.exit(-1)
