from layer import Layer
from fields import *

MAC_BROADCAST = "FF:FF:FF:FF:FF:FF"


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
        pass


class EthernetLayer(Layer):
    NAME = "Ethernet"

    HEADERS = ["dst", "src", "ether_type"]

    SUB_LAYERS = [
        [ArpLayer, "ether_type", 0x806],
    ]

    @staticmethod
    def fields_info():
        return [MacAddress("dst", MAC_BROADCAST),
                MacAddress("src"),
                UnsignedShort("ether_type", 0)]
