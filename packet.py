from struct import pack, unpack

# Packet:
# type: offset 0 (First Byte) ACK, DATA, EOT
# number: offset 1 (Second byte) 0-255
# length:  offset 2 (Third byte) 0-255 bytes of data per data packet. 
# data: length bytes starting at offset 3.

EOT = 0
DATA = 1
ACK = 2

class Packet:

    TYPE_MAP = {
        EOT:"EOT",
        DATA:"DATA",
        ACK:"ACK"
    }

    def __init__(self, pkt_type: int = 0, number: int = 0, length: int = 0, data: int = b"", raw: bytes=None):
        if raw:
            fields = unpack("!BBB", raw[0:3])
            payload = raw[3:]
            self.pkt_type = fields[0]
            self.number = fields[1]
            self.length = fields[2]
            self.data = payload
        else:
            self.pkt_type = pkt_type
            self.number = number
            self.length = length
            self.data = data

    def type_to_string(self):
        return self.TYPE_MAP[self.pkt_type]

    def serialize(self):
        return pack("!BBB", self.pkt_type, self.number, self.length) + self.data

    def __repr__(self):
        return f"Packet(pkt_type={self.type_to_string()}, number={self.number}, length={self.length}, data={self.data})"
