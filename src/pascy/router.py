import socket
import select
import packet
from ipaddress import ip_address, ip_network

INTERFACES = {"1.1.1.0/24": "net1", "2.2.2.0/24": "net2"}


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

    for interface in INTERFACES.values():
        socket_dict[interface] = create_socket(interface)
    return socket_dict


def handle_connections():
    socket_dict = establish_connection()
    print("established conn")
    inputs = socket_dict.values()
    outputs = []
    message_queues = {}

    while inputs:
        r_list, w_list, e_list = select.select(inputs, outputs, message_queues)
        for sock in r_list:
            data = sock.recv(1024)
            handle_received(socket_dict, data)


def send_interface(send_packet):
    ip = ip_address(send_packet.next_layer.dst_ip)
    for network, interface in INTERFACES.items():
        if ip in ip_network(network):
            return interface


def handle_received(socket_dict, data):
    # parse the received packet
    received = packet.parse_packet(data)

    # get the packet to send
    send_packet = packet.handle_packet(received)

    if send_packet:
        # if the packet is valid, get the interface to send to and send the packet
        interface = send_interface(send_packet)
        socket_dict[interface].send(send_packet.build())



