import socket
import select
import l2

ROUTER_IP_FIRST = "net1"
ROUTER_IP_SEC = "net2"


def create_socket(interface):
    server_socket = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.htons(socket.PACKET_OTHERHOST))
    server_socket.bind((interface, 0))
    return server_socket


def establish_connection():
    socket_list = [create_socket(ROUTER_IP_FIRST), create_socket(ROUTER_IP_SEC)]
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
            handle_packet(data)


def handle_packet(data):
    ether = l2.EthernetLayer()
    ether.deserialize(data)
    data = data[ether.size:]
    arp = l2.ArpLayer()
    arp.deserialize(data)
    ether.display()
    arp.display()
