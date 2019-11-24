import argparse
import time
import random
from scipy.stats import norm
import multiprocessing as mp
import socket
import struct

def return_second_line(warning, request, ack, power):
    # assert(type(power) == type(int))
    # assert((power >= 0) and (power < 32))

    w = (1 << 7) if warning == True else 0
    r = (1 << 6) if request == True else 0
    a = (1 << 5) if ack == True else 0

    return w | r | a | int(power)

def send(name, dest, warning, request, ack, power, info, length=0):
    # print(type(name))
    # assert(type(name) == type(int))
    # assert((name >= 0) and (name < 256))
    if (request == False) and (ack == False):
        packet = bytearray(10)
        packet[0] = name
        packet[1] = return_second_line(warning, request, ack, power)
        info = struct.pack('d', info)
        for i in range(len(info)):
            packet[2 + i] = info[i]
    elif (request == False) and (ack == True):
        packet = bytearray(2)
        packet[0] = name
        packet[1] = return_second_line(warning, request, ack, power)
    elif (request == True) and (ack == False):
        packet = bytearray(10)
        packet[0] = name
        packet[1] = return_second_line(warning, request, ack, power)
        info = struct.pack('d', info)
        for i in range(len(info)):
            packet[2 + i] = info[i]
    elif (request == True) and (ack == True):
        packet = bytearray(3 + (8 * length))
        packet[0] = name
        packet[1] = return_second_line(warning, request, ack, power)
    if dest == 0: 
        UDP_IP_ADDRESS = '127.0.0.1' # Sink IP
    else:
        UDP_IP_ADDRESS = '127.0.0.1' # Send to another device
    UDP_PORT_NO = 2356

    print('send: ', packet)
    try:
        clientSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        clientSock.sendto(packet, (UDP_IP_ADDRESS, UDP_PORT_NO + dest))
    finally:
        clientSock.close()

def recv(name, timeout, port):
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_socket.bind(('127.0.0.1', 2356 + port))
        server_socket.settimeout(timeout)

        ack = False
        packet = []
        mac = []

        while True:
            try:
                message, address = server_socket.recvfrom(128)
                if ((message[1] & 0x20) > 0) and (message[0] == name): # ack
                    ack = True
                else:
                    if ((message[1] & 0x40) > 0) and ((message[1] & 0x20) > 0):
                        for i in range(message[2]):
                            mac.append(
                                (message[3 + i] << 40) |
                                (message[4 + i] << 32) |
                                (message[5 + i] << 24) |
                                (message[6 + i] << 16) |
                                (message[7 + i] << 8)  |
                                (message[8 + i] << 0)
                            )
                    elif (message[1] & 0x20) == 0:
                        packet.append({
                            'n': message[0],
                            'w': True if message[1] & 0x80 > 0 else False,
                            'm': True if message[1] & 0x40 > 0 else False,
                            'a': True if message[1] & 0x20 > 0 else False,
                            'p': float(message[1] & 0x1F),
                            'i': struct.unpack('d', message[2:])[0],
                        })
                    send(name, message[0], False, False, True, 0, None)
            except socket.timeout:
                break
    finally:
        server_socket.close()

    return {
        'ack': ack,
        'packet': packet,
        'mac': mac,
    }

def device(mean, variance, sleep, sleep_variance, dev=255):
    power = 32.0
    mac = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    for i in range(len(mac) - 1):
        if mac[i] == dev:
            del mac[i]
    if dev == 9:
        del mac[8]

    messages_to_forward = []

    while(True):
        time.sleep(abs(random.gauss(sleep, sleep_variance)))
        level = random.gauss(mean, variance)
        cdf = norm(mean, variance).cdf(level)

        can_break = False
        while can_break == False:
            print("""
Number  : %d
Status  : %s
Battery : %f
        """ % (dev, 'Normal' if cdf > 0.1 else 'Warning', power))

            if power > 7.0: # High power
                if cdf > 0.1: # Normal
                    send(dev, 0, False, False, False, int(power), level)
                    recv_info = recv(0, sleep, dev)
                    messages_to_forward += recv_info['packet']
                    if recv_info['mac'] != []:
                        mac = recv_info['mac']
                    power -= random.gauss(0.1, 0.001)
                    can_break = True
                else: # Warning
                    send(dev, 0, True, False, False, int(power), level)
                    recv_info = recv(0, sleep, dev)
                    if recv_info['mac'] != []:
                        mac = recv_info['mac']
                    messages_to_forward += recv_info['packet']
                    if recv_info['ack'] == False:
                        for m in mac:
                            send(dev, m, True, False, False, int(power), level)
                            recv_info = recv(m, sleep, dev)
                            messages_to_forward += recv_info['packet']
                            if recv_info['ack'] == True:
                                can_break = True
                                break
                            power -= random.gauss(0.1, 0.001)
                    else:
                        can_break = True
                        power -= random.gauss(0.1, 0.001)
            elif power > 0.0: # Low power
                if cdf > 0.1: # Normal
                    power -= random.gauss(0.01, 0.0001)
                    can_break = True
                else: # Warning
                    send(dev, 0, True, False, False, int(power), level)
                    recv_info = recv(0, sleep, dev)
                    messages_to_forward += recv_info['packet']
                    if recv_info['mac'] != []:
                        mac = recv_info['mac']
                    if recv_info['ack'] == False:
                        for m in mac:
                            send(dev, m, True, False, False, int(power), level)
                            recv_info = recv(m, sleep, dev)
                            messages_to_forward += recv_info['packet']
                            if recv_info['ack'] == True:
                                can_break = True
                                break
                            power -= random.gauss(0.1, 0.001)
                    else:
                        can_break = True
                        power -= random.gauss(0.1, 0.001)
            elif power <= 0:
                can_break = True
        if power <= 0:
            break
        
        index_to_delete = []
        for m in range(len(messages_to_forward)):
            send(
                messages_to_forward[m]['n'], 
                0, 
                messages_to_forward[m]['w'], 
                messages_to_forward[m]['m'], 
                messages_to_forward[m]['a'], 
                messages_to_forward[m]['p'], 
                messages_to_forward[m]['i']
            )
            recv_info = recv(messages_to_forward[m]['n'], sleep, dev)
            if recv_info['ack'] == True:
                index_to_delete.append(m)

        for i in range(len(index_to_delete) - 1, -1, -1):
            del messages_to_forward[index_to_delete[i]]

    print('Device %d dead' % (dev))
def main():
    parser = argparse.ArgumentParser()
    args = parser.parse_args()
    devices = [1, 2, 3, 4, 5, 6, 7, 8, 9]

    procs = []
    for dev in devices:
        p = mp.Process(target=device, args=(75, 2, 1, 0.1, dev))
        procs.append(p)
        p.start()

    # device(75, 2, 1, 0.1, 'ecg')


if __name__ == '__main__':
    main()
