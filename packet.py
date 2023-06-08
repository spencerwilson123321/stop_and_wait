from struct import pack, unpack

# Packet:
# type: offset 0 (First Byte) ACK, DATA, EOT
# number: offset 1 (Second byte) 0-255
# length:  offset 2 (Third byte) 0-255 bytes of data per data packet. 
# data: length bytes starting at offset 3.

def parse_packet(pkt: bytes) -> Packet:
    fields = unpack("!BBB", pkt[0:3])
    payload = pkt[3:]
    return Packet(fields[0], fields[1], fields[2], payload)

TYPE_MAP = {
    0:"EOT",
    1:"DATA",
    2:"ACK"
}

class Packet:
    
    def __init__(self, pkt_type, number, length, data):
        self.pkt_type = pkt_type
        self.number = number
        self.length = length
        self.data = data

    def type_to_string(self):
        return TYPE_MAP[self.pkt_type]

    def serialize(self):
        return pack("!BBB", self.pkt_type, self.number, self.length) + self.data

    def __repr__(self):
        return f"Packet(pkt_type={self.type_to_string}, number={self.number}, length={self.length}, data={self.data})"
