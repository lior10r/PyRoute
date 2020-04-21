import socket
import select
import packet

ROUTER_IP_FIRST = "net1"
ROUTER_IP_SEC = "net2"
INTERFACES = ["net1", "net2"]

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
    socket_list = []

    for interface in INTERFACES:
        socket_list.append(create_socket(interface))
    return socket_list


def handle_connections():
    socket_list = establish_connection()
    print("established conn")
    inputs = socket_list[:]
    outputs = []
    message_queues = {}

    while inputs:
        r_list, w_list, e_list = select.select(inputs, outputs, message_queues)
        for sock in r_list:
            data = sock.recv(1024)
            handle_received(sock, data)


def handle_received(sock, data):
    received = packet.parse_packet(data)
    to_send, is_same_socket = packet.handle_packet(received)
    if is_same_socket:
        sock.send(to_send.build())

