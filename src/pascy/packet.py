import l2
import l3
from ipaddress import ip_network, ip_address

ROUTER_TABLE = {"1.1.1.0/24": "02:42:6f:a4:53:0b", "2.2.2.0/24": "02:42:1a:3c:99:5b"}

ARP_TABLE = {"1.1.1.1": "02:42:6f:a4:53:0b", "2.2.2.1": "02:42:1a:3c:99:5b", "2.2.2.2": "02:42:02:02:02:02",
             "1.1.1.2": "02:42:01:01:01:02"}

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

    # switch the source ip and destination ip
    arp.src_ip, arp.dst_ip = arp.dst_ip, arp.src_ip

    # handle the MAC addresses of the ARP protocol
    arp.src_mac, arp.dst_mac = ether.src, ether.dst

    # set opcode to response
    arp.opcode = l3.ArpLayer.OP_IS_AT

    return ether


def handle_arp(packet):
    print("handles ARP packet")

    arp = packet.next_layer
    if arp.opcode == arp.OP_WHO_HAS:
        return response_arp(packet)


def get_mac_router(ip):
    for network, mac in ROUTER_TABLE.items():
        if ip in ip_network(network):
            return mac


def handle_ip(packet):
    print("handles IP packet")
    ether = packet
    ip = packet.next_layer
    dst_ip = l2.IpAddress.ip2str(ip.dst_ip)

    if dst_ip not in ARP_TABLE.keys():
        return

    ether.dst = ARP_TABLE[dst_ip]

    ether.src = get_mac_router(ip_address(dst_ip))
    print("*******************IP AFTER*******************")
    ether.display()
    return ether


def handle_packet(packet):
    print("*******************BEFORE*******************")
    packet.display()
    if isinstance(packet.next_layer, l3.ArpLayer):
        # return the response packet, True for sending in the same socket received
        return handle_arp(packet)

    if isinstance(packet.next_layer, l3.IpLayer):
        return handle_ip(packet)
