from layer import Layer
from fields import *


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
        return [UnsignedShort("hardware_type", 0),
                UnsignedShort("protocol_type", 0),
                UnsignedByte("hardware_size", 0),
                UnsignedByte("protocol_size", 0),
                UnsignedShort("opcode", 0),
                MacAddress("src_mac"),
                IpAddress("src_ip"),
                MacAddress("dst_mac"),
                IpAddress("dst_ip")]


class IpLayer(Layer):

    NAME = "IP"

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
