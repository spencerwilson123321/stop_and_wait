from struct import pack, unpack

# Packet:
# type: offset 0 (First Byte) ACK, DATA, EOT
# number: offset 1 (Second byte) 0-255
# length:  offset 2 (Third byte) 0-255 bytes of data per data packet. 
# data: length bytes starting at offset 3.

def parse_packet(pkt: bytes) -> Packet:
    try:
        fields = unpack("!BBB", pkt[0:3])
        payload = pkt[3:]
    except Exception:
        return None
    return Packet(fields[0], fields[1], fields[2], payload)


class Packet:
    
    def __init__(self, pkt_type, number, length, data):
        self.pkt_type = pkt_type
        self.number = number
        self.length = length
        self.data = data
    
    def serialize(self):
        return pack("!BBB", self.pkt_type, self.number, self.length) + self.data