import socket

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind(('127.0.0.1', 1234))

while True:
    message, address = server_socket.recvfrom(1234)
    print(message)
    message = message.upper()