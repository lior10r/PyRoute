import socket
import select

ROUTER_IP_FIRST = "net1"
ROUTER_IP_SEC = '2.2.2.2'

def create_socket(ip, port):
    server_socket = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, )
    server_socket.bind((ip, port))
    return server_socket

def establish_connection(ip):
    socket_list = []

    for port in range(1, 100):
        try:
            socket_list.append(create_socket(ip, port))
        except:
            raise
    return socket_list


def handle_connections():
    socket_list = establish_connection(ROUTER_IP_FIRST)
    print("established conn")
    inputs = socket_list[:]
    outputs = []
    message_queues = {}

    while inputs:
        r_list, w_list, e_list = select.select(inputs, outputs, message_queues)
        for sock in r_list:
            data = sock.recv(1024)
            with open("log.txt", 'a+') as fd:
                fd.write(data)
                print(data)

