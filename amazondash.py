import socket
import struct
import binascii
from sip_luces import *

macs = {
    'fca6677d72de' : 'dash-on',
    '000000000000' : 'dash-fairy',
    '000000000000' : 'dash-ambipur',
    '000000000000' : 'dash-bsn',
    '000000000000' : 'dash-on2',
    '000000000000' : 'dash-unasigned1',
    '000000000000' : 'dash_unasigned2'
}
events  = {
    'dash-on'      : 'Focos ON/OFF',
    'dash-fairy'   : 'Farolas ON/OFF'
}


rawSocket = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.htons(0x0003))

focos = IFTTT_Farolas(False,True)
onoff  = 'off'

while True:

    packet = rawSocket.recvfrom(2048)

    ethernet_header = packet[0][0:14]
    ethernet_detailed = struct.unpack("!6s6s2s", ethernet_header)

    arp_header = packet[0][14:42]
    arp_detailed = struct.unpack("2s2s1s1s2s6s4s6s4s", arp_header)
    source_mac = binascii.hexlify(arp_detailed[5])

    # skip non-ARP packets
    ethertype = ethernet_detailed[2]
    if ethertype != '\x08\x06':
        continue
    if source_mac in macs:

      print "------  Amazon dash button pressed ---------------------"

      print "        Button pressed   : " + macs[source_mac]
      print "        Evento  asociado : " + events[macs[source_mac]]
      if macs[source_mac] == 'dash-on':
        if onoff == 'off':
          onoff = 'on'
        else:
          onoff = 'off'
        print "        Status           : " + onoff
        #focos.turnOnForSeconds(300)
        focos.remoteCall(onoff)

      print "--------------------------------------------------------"
