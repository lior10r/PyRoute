from layer import Layer
from fields import *


class IcmpLayer(Layer):
    # icmp ping values
    ICMP_PING_TYPE = 8
    ICMP_PONG_TYPE = 0
    ICMP_PING_CODE = 0

    NAME = "ICMP"

    @staticmethod
    def fields_info():
        return [UnsignedByte("type"),
                UnsignedByte("code"),
                UnsignedShort("checksum"),
                UnsignedShort("id"),
                UnsignedShort("seq_num"),
                ByteString("payload")]
