from layer import Layer
from fields import *
from l3 import ArpLayer, IpLayer

MAC_BROADCAST = "FF:FF:FF:FF:FF:FF"


class EthernetLayer(Layer):
    NAME = "Ethernet"

    SUB_LAYERS = [
        [ArpLayer, "ether_type", 0x806],
        [IpLayer, "ether_type", 0x800],
    ]

    @staticmethod
    def fields_info():
        return [MacAddress("dst", MAC_BROADCAST),
                MacAddress("src"),
                UnsignedShort("ether_type", 0)]
