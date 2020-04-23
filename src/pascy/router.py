import socket
import select
import packet
from ipaddress import ip_address, ip_network

INTERFACES = {"net1": ip_network("1.1.1.0/24"), "net2": ip_network("2.2.2.0/24")}

MTU = 1500


def create_socket(interface):
    """
    a function that creates a raw socket for interface
    :param interface: interface name
    :return: raw socket
    """
    server_socket = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.htons(socket.PACKET_OTHERHOST))
    server_socket.bind((interface, 0))
    return server_socket


def establish_connection():
    """
    a function that creates raw sockets to all interfaces
    :return: a list of all sockets
    """
    socket_dict = {}

    for interface in INTERFACES.keys():
        socket_dict[interface] = create_socket(interface)
    return socket_dict


def handle_connections():
    socket_dict = establish_connection()
    print("established conn")

    inputs = list(socket_dict.values())

    while inputs:
        r_list, _, _ = select.select(inputs, [], [])

        for sock in r_list:
            data = sock.recv(MTU)
            handle_received(socket_dict, data)


def get_send_interface_name(send_packet):
    """
    a function that gets a packet and returns the interface it should be sent in
    :param send_packet: packet to send
    :return: interface name
    """
    ip = ip_address(send_packet.next_layer.dst_ip)

    for interface, network in INTERFACES.items():
        # if ip in the network of the interface, return interface name
        if ip in network:
            return interface


def handle_received(socket_dict, data):
    """
    a function to handle the received packet
    :param socket_dict: dictionary of interface to socket
    :param data: the packet received
    """
    # parse the received packet
    received = packet.parse_packet(data)
    if not received:
        return

    # get the packet to send
    send_packet = packet.handle_packet(received)
    if send_packet:
        # if the packet is valid, get the interface to send to and send the packet
        interface = get_send_interface_name(send_packet)
        socket_dict[interface].send(send_packet.build())

