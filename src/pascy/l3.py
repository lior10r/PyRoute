from layer import Layer
from fields import *
from l4 import IcmpLayer


class ArpLayer(Layer):
    OP_WHO_HAS = 1
    OP_IS_AT = 2

    NAME = "ARP"

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
    # number of icmp protocol in ip packet
    ICMP_PROTOCOL = 1

    NAME = "IP"

    SUB_LAYERS = [
        [IcmpLayer, "protocol", 1],
    ]

    @staticmethod
    def fields_info():
        return [UnsignedByte("version_Header_length"),
                UnsignedByte("dscp"),
                UnsignedShort("total_length"),
                UnsignedShort("id"),
                UnsignedShort("flags"),
                UnsignedByte("ttl"),
                UnsignedByte("protocol"),
                UnsignedShort("checksum"),
                IpAddress("src_ip"),
                IpAddress("dst_ip"),
                ByteString("payload")]
