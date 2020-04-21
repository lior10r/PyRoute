import l2
import l3
from ipaddress import ip_network, ip_address

# the network : mac address of router in that network
ROUTER_TABLE = {"1.1.1.0/24": "02:42:80:17:94:97", "2.2.2.0/24": "02:42:ef:af:ea:96"}

# ip : mac
ARP_TABLE = {"1.1.1.1": "02:42:80:17:94:97", "2.2.2.1": "02:42:ef:af:ea:96", "2.2.2.2": "02:42:02:02:02:02",
             "1.1.1.2": "02:42:01:01:01:02"}

# a list of ip addresses of the router
ROUTER_IP = [ip_address("1.1.1.1"), ip_address("2.2.2.1")]

# indexes of SUB_LAYERS
PROTOCOL_CLASS_INDEX = 0
PROTOCOL_IDENTIFIER_NAME_INDEX = 1
PROTOCOL_IDENTIFIER_VALUE_INDEX = 2


def get_protocol(ether):
    """
    a function to get the protocol of the third layer
    :param ether: the Ethernet layer
    :return: IP or ARP
    """
    for sub in ether.SUB_LAYERS:
        if ether.ether_type == sub[PROTOCOL_IDENTIFIER_VALUE_INDEX]:
            return sub[PROTOCOL_CLASS_INDEX]


def parse_packet(data):
    """
    a function to parse a packet to layers
    :param data: the received packet in binary
    :return: the parsed packet
    """
    # get the layer 2 out of the packet
    ether = l2.EthernetLayer()
    ether.deserialize(data)

    # set data to point on layer 3
    data = data[ether.size:]

    # get the class type of layer 3 (arp / ip)
    layer3 = get_protocol(ether)
    if not layer3:
        return

    # create an instance of that class type
    layer3 = layer3()

    # enter the data to the packet
    layer3.deserialize(data)

    packet = ether / layer3
    # return the parsed packet
    return packet


def response_arp(packet):
    """
    create the response packet
    :param packet: the received packet
    :return: the packet to send
    """
    ether = packet
    arp = packet.next_layer

    # change the MAC addresses of Ethernet layer
    ether.dst = ether.src

    # set the source to my ip, according to the IP requested
    ether.src = ARP_TABLE[l2.IpAddress.ip2str(arp.dst_ip)]

    # switch the source ip and destination ip
    arp.src_ip, arp.dst_ip = arp.dst_ip, arp.src_ip

    # handle the MAC addresses of the ARP protocol
    arp.src_mac, arp.dst_mac = ether.src, ether.dst

    # set opcode to response
    arp.opcode = l3.ArpLayer.OP_IS_AT

    return ether


def handle_arp(packet):
    """
    a function to handle ARP packets
    :param packet: the received packet
    :return: the packet to send
    """
    print("handles ARP packet")

    arp = packet.next_layer
    # check if the arp is a question, and is asking for me
    if arp.opcode == arp.OP_WHO_HAS and ip_address(arp.dst_ip) in ROUTER_IP:
        return response_arp(packet)


def get_mac_router(ip):
    """
    a function to get the mac of the router in the interface to send to
    :param ip: ip destination
    :return: mac address
    """
    for network, mac in ROUTER_TABLE.items():
        if ip in ip_network(network):
            return mac


def handle_ip(packet):
    """
    a function to forward ip packet
    :param packet: the received packet
    :return: the packet to send
    """
    print("handles IP packet")

    ether = packet
    ip = packet.next_layer

    # get the destination ip
    dst_ip = l2.IpAddress.ip2str(ip.dst_ip)

    # if destination ip not in in the arp table, drop packet
    if dst_ip not in ARP_TABLE.keys():
        return

    # set the MAC addresses
    ether.dst = ARP_TABLE[dst_ip]

    ether.src = get_mac_router(ip_address(dst_ip))

    return ether


def handle_packet(packet):
    # if the packet is an ARP packet
    if isinstance(packet.next_layer, l3.ArpLayer):
        # return the response packet, True for sending in the same socket received
        return handle_arp(packet)

    # if the packet is IP packet
    if isinstance(packet.next_layer, l3.IpLayer):
        return handle_ip(packet)
