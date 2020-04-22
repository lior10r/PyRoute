from abc import ABC, abstractmethod
from collections import OrderedDict
from functools import lru_cache


class Layer(ABC):
    NAME = ""
    SUB_LAYERS = []

    HEADERS = []

    def __init__(self):
        self.next_layer = None
        self.last_layer = self

        self.fields = OrderedDict((f.name, f) for f in self.fields_info())

    def __truediv__(self, other):
        """
        Create a connection between two layers, creating a packet.
        For example:
            >>> packet = EthernetLayer() / ArpLayer()
        Will create an ARP packet, whose L2 structure is Ethernet.

        :param other:   The upper layer
        :return:        self
                        (Usable for multiple one-line connections)
        """
        return self.connect_layer(other)

    def __getattr__(self, key):
        # Prevent infinite loop on init :(
        if "fields" not in self.__dict__:
            self.__dict__["fields"] = {}

        if key in self.__dict__:
            return self.__dict__[key]

        elif key in self.fields.keys():
            return self.fields[key].get()

    def __setattr__(self, key, val):
        if key in self.fields:
            self.fields[key].set(val)

        else:
            self.__dict__[key] = val

    def get_field(self, field_name) -> bytes:
        """
        a function to get value of field
        :param field_name: name of field
        :return: value of the field, None on failure
        """
        if field_name in self.fields.keys():
            return self.fields[field_name].serialize()


    @staticmethod
    @abstractmethod
    def fields_info():
        """
        Build and return the structure of this layer's fields.
        This should be implemented for each layer.

        :return:    A list of instances of Field (or subclasses).
                    Each item in this list represent (by order) the relevant packet field.
        """
        pass

    def display(self):
        content = ""
        indent = ""

        # Layer name
        content += indent + "--- {} ---\n".format(self.NAME)
        for _, f in self.fields.items():
            content += indent + str(f) + "\n"

        # Recurse all sub-layers
        next_layer = self.next_layer
        while next_layer:
            indent += "\t"
            content += indent + "--- {} ---\n".format(next_layer.NAME)

            for _, f in next_layer.fields.items():
                content += indent + str(f) + "\n"

            next_layer = next_layer.next_layer

        print(content)

    @property
    @lru_cache()
    def size(self) -> int:
        """
        :return:    The size (in bytes) of this layer's raw data
        """
        size = 0

        for _, field in self.fields.items():
            size += len(field)

        return size

    def serialize(self) -> bytes:
        """
        Serialize this layer to a buffer
        """
        buffer = b""

        for _, field in self.fields.items():
            buffer += field.serialize()

        return buffer

    def set_field(self, index, field_name, buffer: bytes):
        """
        a function to set the field from the buffer
        :param index: start index of the field in the buffer
        :param field_name: field name to set
        :param buffer: the bytes from the packet
        :return: the index of the next field
        """

        # set the value at field from the buffer
        self.fields[field_name].deserialize(buffer[index:])

        # return the index + size of field = index of next field
        return index + len(self.fields[field_name])

    def deserialize(self, buffer: bytes):
        """
        Deserialize this layer from a buffer
        """
        index = 0
        for header in self.HEADERS:
            index = self.set_field(index, header, buffer)

    def build(self) -> bytes:
        """
        Build the entire packet into a raw buffer
        """
        if self.next_layer:
            return self.serialize() + self.next_layer.build()

        else:
            return self.serialize()

    def __len__(self) -> int:
        """
        :return:    The size (in bytes) of the entire packet's raw data
        """
        if self.next_layer:
            return self.size + len(self.next_layer)

        else:
            return self.size

    def connect_layer(self, other):
        for layer, field, val in self.SUB_LAYERS:
            if isinstance(other, layer):
                self.last_layer.fields[field].set(val)
                self.last_layer = other

                if not self.next_layer:
                    self.next_layer = other
                else:
                    self.next_layer.connect_layer(other)

                return self

        raise Exception("Can't link {} and {}.".format(self.__class__.__name__, other.__class__.__name__))
