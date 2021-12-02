__author__ = 'josefemenias'
# Documentation https://info.kmtronic.com/manuals/user_manuals/UD8CR_UDP_EIGHT_CHANNEL_RELAY.pdf
import binascii
import socket
import time
from random import randint

UDP_IP = "192.168.1.199"
UDP_PORT = 12345
COMMAND_ON = b"FF0101" # b"11"
COMMAND_OFF = b"FF0100" # b"11"
WAIT = 0.125


print("UDP target IP:", UDP_IP)
print("UDP target port:", UDP_PORT)
print("message:", COMMAND_ON)

sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP


for i in range(1,5):
        sock.sendto( bytes(f'FF0{2*i}01', 'ascii'), (UDP_IP, UDP_PORT))
        sock.sendto(bytes(f'FF0{2*i-1}01', 'ascii'), (UDP_IP, UDP_PORT))
        time.sleep(WAIT)
        sock.sendto(bytes(f'FF0{2*i}00', 'ascii'), (UDP_IP, UDP_PORT))
        sock.sendto(bytes(f'FF0{2*i-1}00', 'ascii'), (UDP_IP, UDP_PORT))
        time.sleep(WAIT)

exit(0)

for i in range(0,256):
        hex_string = hex(i)[2:].rjust(2, '0')
        time.sleep(0.1)
        print(hex_string.upper())
        sock.sendto(COMMAND + hex_string, (UDP_IP, UDP_PORT))

for i in range(256,-1,-1):

        randv = randint(0,255)
        hex_string = hex(i)[2:].rjust(2, '0')
        time.sleep(0.5)
        print(hex_string.upper())
        sock.sendto(COMMAND + hex_string, (UDP_IP, UDP_PORT))

