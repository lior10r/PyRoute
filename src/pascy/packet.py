import l2

ARP_TABLE = {"1.1.1.1" : "02:42:6f:a4:53:0b", "2.2.2.2" : "02:42:1a:3c:99:5b"}

# indexes of SUB_LAYERS
PROTOCOL_CLASS_INDEX = 0
PROTOCOL_IDENTIFIER_NAME_INDEX = 1
PROTOCOL_IDENTIFIER_VALUE_INDEX = 2


def get_protocol(ether):
    for sub in ether.SUB_LAYERS:
        if ether.ether_type == sub[PROTOCOL_IDENTIFIER_VALUE_INDEX]:
            return sub[PROTOCOL_CLASS_INDEX]


def parse_packet(data):
    # get the layer 2 out of the packet
    ether = l2.EthernetLayer()
    ether.deserialize(data)

    # set data to point on layer 3
    data = data[ether.size:]

    # get the class type of layer 3 (arp / ip)
    layer3 = get_protocol(ether)
    if None:
        raise ValueError("No matching protocol:\n {}".format(ether))

    # create an instance of that class type
    layer3 = layer3()

    # enter the data to the packet
    layer3.deserialize(data)

    # return the parsed packet
    return ether / layer3


def response_arp(packet):
    ether = packet
    arp = packet.next_layer

    # change the MAC addresses of Ethernet layer
    ether.dst = ether.src

    # set the source to my ip, according to the IP requested
    ether.src = ARP_TABLE[l2.IpAddress.ip2str(arp.dst_ip)]

    # swtich the source ip and destination ip
    arp.src_ip, arp.dst_ip = arp.dst_ip, arp.src_ip

    # handle the MAC addresses of the ARP protocol
    arp.src_mac, arp.dst_mac = ether.src, ether.dst

    # set opcode to response
    arp.opcode = l2.ArpLayer.OP_IS_AT

    ether.display()
    return ether


def handle_arp(packet):
    print("handles ARP packet")

    arp = packet.next_layer
    if arp.opcode == arp.OP_WHO_HAS:
        return response_arp(packet)


def handle_packet(packet):
    packet.display()
    if isinstance(packet.next_layer, l2.ArpLayer):
        # return the response packet, True for sending in the same socket received
        return handle_arp(packet), True
