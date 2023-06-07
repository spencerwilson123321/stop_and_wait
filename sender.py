import traceback
import sys
import logging
import configparser
from socket import socket, AF_INET, SOCK_DGRAM
from timer import Timer
from packet import *
from os.path import isFile

logging.basicConfig(filename='sender.log',
                    encoding='utf-8',
                    level=logging.INFO,
                    format="%(asctime)s - %(message)s")

class Sender:
    """
        The Sender class has all the properties and behaviours to implement the sender portion of the
        send-and-wait protocol. 
    """

    def __init__(self, configuration):
        self.receiver_address = (configuration["receiver"]["ip"], int(configuration["receiver"]["port"]))
        self.sender_address = (configuration["sender"]["ip"], int(configuration["sender"]["port"]))
        self.networK_address = (configuration["network"]["ip"], int(configuration["network"]["port"]))
        
        # alpha - gain constant used in retransmit timer.
        self.alpha = 0.8
        self.predicted_rtt = 80.0
        self.predicted_deviation = 50.0
        
        # Time out threshold for retransmission timer.
        self.tot = self.predicted_deviation + self.predicted_rtt
        self.timer = Timer()
        
        # The sender window.
        self.num_acks_received = 0
        self.num_timeouts = 0
        self.socket = socket(AF_INET, SOCK_DGRAM)
        self.socket.bind(self.sender_address)
        self.socket.setblocking(0)
        self.PAYLOAD_SIZE = 512
        self.total_pkts_sent = 0

    def start_timer(self):
        self.timer.start()

    def stop_timer(self):
        self.timer.stop()

    def check_timer(self):
        return self.timer.check_time()

    def increment_acks_received(self):
        self.num_acks_received = self.num_acks_received+1

    def increment_num_timeouts(self):
        self.num_timeouts = self.num_timeouts + 1

    def receive_packet(self):
        data, addr = self.socket.recvfrom(1024)
        return pickle.loads(data), addr

    def update_retransmission_timer_info(self, actual_rtt):
        # avg RTT using techniques from Jacobson's paper
        actual_deviation = abs(self.predicted_rtt - actual_rtt)
        self.predicted_rtt = self.predicted_rtt*self.alpha + (1.0 - self.alpha)*actual_rtt
        self.predicted_deviation = self.alpha*self.predicted_deviation + (1.0 - self.alpha)*actual_deviation
        # Update timeout timer
        self.tot = (10.0*self.predicted_deviation) + (1.5*self.predicted_rtt)

    def exponential_back_off_timer(self):
        # When there is a timeout, increase the retransmission timer exponentially.
        self.tot = self.tot*2

    def transmit(self, path=""):
        
        if not isFile(path):
            print(f"File not found: {path}")
            exit(1)
        with open(path, "rb") as f:
            data = f.read()
        if not data:
            print(f"Cannot transmit empty file.")
            exit(1)
        
        bytes_acked = 0
        while bytes_acked < len(data):
            # 1. Construct packet.
            # 2. Send packet.
            # 3. Start retransmission timer.
            # 4. Wait for response.
            # 5. Ack receieved, adjust timer, send next packet, repeat.
            # OR
            # 5. Timeout, resend packet, adjust timer, repeat.
            # 6. All data sent and received.
            # 7. Send EOT packet.
            # 8. Wait for response.
            # 9. Ack received, end transmission.
            # OR
            # 9. Timeout, adjust timer, retransmit EOT, repeat.


# def main():

#     CONFIG = configparser.ConfigParser()
#     CONFIG.read("config.ini")
#     sender = Sender(CONFIG)

#     while True:
#         # If eot has been sent, then finish
#         if sender.get_state() == 1:
#             break
#         # Determine packets to send, send, start timer.
#         sender.generate_window()
#         # sender.adjust_timer_thresh()
#         sender.send_all_in_window()
#         sender.start_timer()
#         # Start checking for acknowledgements.
#         tot = sender.tot
#         while True:
#             t = sender.check_timer()
#             if t > float(tot):
#                 logging.info(f"Timeout: tot = {format(tot, '.2f')}, time = {t}")
#                 # Exponentially increase back off timer.
#                 sender.exponential_back_off_timer()
#                 sender.increment_num_timeouts()
#                 # Stop timer, and then break out of loop.
#                 sender.stop_timer()
#                 break
#             if sender.last_biggest_ack == sender.last_highest_sequence_number:
#                 logging.info("Successful Transaction: All Data has been Acknowledged")
#                 break
#             try:
#                 ack, addr = sender.receive_packet()
#                 if ack is None:
#                     continue
#             except BlockingIOError:
#                 continue
#             logging.info(f"Received: {ack}")
#             # Increment number of acks received.
#             sender.increment_acks_received()
#             # Check and set last biggest ack
#             if ack.seq_num >= sender.ending_sequence_number:
#                 sender.send_eot()
#                 sender.set_state(1)
#                 break
#             if ack.seq_num > sender.last_biggest_ack:
#                 sender.last_biggest_ack = ack.seq_num
#             # Update rolling average for RTT.
#             sender.update_retransmission_timer_info(sender.timer.check_time())
#     logging.info(f"Total Acks received: {sender.num_acks_received}")
#     logging.info(f"Total Pkts sent: {sender.total_pkts_sent}")
#     logging.info(f"Total number of timeouts: {sender.num_timeouts}")
#     sender.socket.close()


if __name__ == '__main__':

    try:
        CONFIG = configparser.ConfigParser()
        CONFIG.read("config.ini")
        sender = Sender(CONFIG)
        sender.transmit()
    except KeyboardInterrupt:
        print("\nShutting down sender...")
    except Exception:
        traceback.print_exc(file=sys.stdout)
    sys.exit(-1)

