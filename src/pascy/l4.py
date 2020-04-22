from layer import Layer
from fields import *


class IcmpLayer(Layer):

    NAME = "ICMP"

    HEADERS = ["type",
               "code",
               "checksum",
               "id",
               "seq_num",
               "payload"]

    @staticmethod
    def fields_info():
        return [UnsignedByte("type"),
                UnsignedByte("code"),
                UnsignedShort("checksum"),
                UnsignedShort("id"),
                UnsignedShort("seq_num"),
                ByteString("payload", 0)]
