from layer import Layer
from fields import *
from l4 import IcmpLayer

class ArpLayer(Layer):
    OP_WHO_HAS = 1
    OP_IS_AT = 2

    NAME = "ARP"

    HEADERS = ["hardware_type",
               "protocol_type",
               "hardware_size",
               "protocol_size",
               "opcode",
               "src_mac",
               "src_ip",
               "dst_mac",
               "dst_ip"]

    @staticmethod
    def fields_info():
        return [UnsignedShort("hardware_type"),
                UnsignedShort("protocol_type"),
                UnsignedByte("hardware_size"),
                UnsignedByte("protocol_size"),
                UnsignedShort("opcode"),
                MacAddress("src_mac"),
                IpAddress("src_ip"),
                MacAddress("dst_mac"),
                IpAddress("dst_ip")]


class IpLayer(Layer):

    NAME = "IP"

    SUB_LAYERS = [
        [IcmpLayer, "protocol", 1]
    ]

    HEADERS = ["Version_Header_length",
               "DSCP",
               "total_length",
               "id",
               "flags",
               "ttl",
               "protocol",
               "checksum",
               "src_ip",
               "dst_ip",
               "payload"]

    @staticmethod
    def fields_info():
        return [UnsignedByte("Version_Header_length"),
                UnsignedByte("DSCP"),
                UnsignedShort("total_length"),
                UnsignedShort("id"),
                UnsignedShort("flags"),
                UnsignedByte("ttl"),
                UnsignedByte("protocol"),
                UnsignedShort("checksum"),
                IpAddress("src_ip"),
                IpAddress("dst_ip"),
                ByteString("payload", 0)]
