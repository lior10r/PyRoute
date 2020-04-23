import l2
import l3
import l4
from ipaddress import ip_network, ip_address
from netifaces import ifaddresses
from struct import unpack
from socket import AF_PACKET
from functools import lru_cache


ROUTER_NET1_MAC = ifaddresses("net1")[AF_PACKET.numerator][0]['addr']
ROUTER_NET2_MAC = ifaddresses("net2")[AF_PACKET.numerator][0]['addr']

# the network : mac address of router in that network
ROUTER_TABLE = {ip_network("1.1.1.0/24"): ROUTER_NET1_MAC, ip_network("2.2.2.0/24"): ROUTER_NET2_MAC}

# ip : mac
ARP_TABLE = {"1.1.1.1": ROUTER_NET1_MAC, "2.2.2.1": ROUTER_NET2_MAC, "2.2.2.2": "02:42:02:02:02:02",
             "1.1.1.2": "02:42:01:01:01:02"}

# a list of ip addresses of the router
ROUTER_IP = [ip_address("1.1.1.1"), ip_address("2.2.2.1")]

# indexes of SUB_LAYERS
PROTOCOL_CLASS_INDEX = 0
PROTOCOL_IDENTIFIER_NAME_INDEX = 1
PROTOCOL_IDENTIFIER_VALUE_INDEX = 2

SHORT_MAX = 0xffff

BYTE_SIZE = 8
SHORT_SIZE = 16


def get_protocol(ether):
    """
    a function to get the protocol of the third layer
    :param ether: the Ethernet layer
    :return: IP or ARP
    """
    for sub in ether.SUB_LAYERS:
        # check if ether type is matching to a type in SUB_LAYER, if yes return the type of the next layer
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
        print("UNKNOWN PACKET RECEIVED")
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
    if l2.IpAddress.ip2str(arp.dst_ip) in ARP_TABLE:
        ether.src = ARP_TABLE[l2.IpAddress.ip2str(arp.dst_ip)]
    else:
        # if no entry in the arp table, i can't reply on the message
        return

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
        if ip in network:
            return mac


def handle_packet_to_me(packet):
    """
    a function that handles packets directed to the routed (for now only pings)
    :param packet: received packet
    :return: packet to send, None on failure
    """
    ether = packet
    ip = packet.next_layer

    # if not icmp, I can't handle it
    if ip.protocol != l3.IpLayer.ICMP_PROTOCOL:
        return

    # create the icmp layer from the ip payload
    icmp = l4.IcmpLayer()
    icmp.deserialize(ip.payload)

    # the payload is now the icmp layer
    ip.payload = b''

    # if not ping, return None
    if icmp.type == l4.IcmpLayer.ICMP_PING_TYPE and icmp.code == l4.IcmpLayer.ICMP_PING_CODE:
        print("Handle PING packet")
        # set the packet's field to send back
        icmp.type = l4.IcmpLayer.ICMP_PONG_TYPE
        icmp.checksum = calc_checksum(icmp)

        # switch the ip dst and src
        ip.src_ip, ip.dst_ip = ip.dst_ip, ip.src_ip

        # set the mac src to me
        ether.src = get_mac_router(ip_address(ip.src_ip))

        # set the mac dst
        if l2.IpAddress.ip2str(ip.dst_ip) in ARP_TABLE:
            ether.dst = ARP_TABLE[l2.IpAddress.ip2str(ip.dst_ip)]
        else:
            print("RECEIVED PACKET FROM AN UNKNOWN PC")
            return

        ip.checksum = calc_checksum(ip)
        # connect the icmp next to the ip
        ip / icmp
        return packet


@lru_cache()
def calc_checksum(layer):
    """
    a function to recalculate the ip header
    :param layer: layer to calculate checksum
    """
    layer_content = b''

    fields = layer.fields.keys()
    try:
        # the payload isn't calculated in the checksum
        fields.remove("payload")
    except:
        pass

    # get all the header to bytes
    for header in fields:
        layer_content += layer.get_field(header)

    checksum = 0
    # sum all the layer as shorts
    for i in range(0, len(layer_content), 2):
        checksum += unpack(">H", layer_content[i:i+2])[0]

    # subtract the previous checksum
    checksum -= layer.checksum

    # if the checksum is bigger the short, loop and do the calculations until checksum is two byte size
    while checksum > SHORT_MAX:
        # calc the carry, everything after the first two bytes
        carry = checksum >> SHORT_SIZE
        # get only the first two bytes
        checksum = checksum & SHORT_MAX
        # add the carry to the checksum
        checksum += carry
    # the checksum is the complement of this result, and make it two byte size
    return (~checksum) & SHORT_MAX


def create_ip_send(packet):
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


def handle_ip(packet):
    ip = packet.next_layer

    if ip_address(ip.dst_ip) in ROUTER_IP:
        return handle_packet_to_me(packet)

    else:
        return create_ip_send(packet)


def handle_packet(packet):
    # if the packet is an ARP packet
    if isinstance(packet.next_layer, l3.ArpLayer):
        # return the response packet, True for sending in the same socket received
        return handle_arp(packet)

    # if the packet is IP packet
    if isinstance(packet.next_layer, l3.IpLayer):
        return handle_ip(packet)
