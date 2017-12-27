import socket
import struct
import binascii
from sip_luces import *

macs = {
    'fca6677d72de' : 'dash-on',
    'ac63be7c6467' : 'dash-fairy',        # Serial G030M90363848352
    'fca6677a9af4' : 'dash-ambipur',      # Serial G030QC0373326649
    'ac63beaae06a' : 'dash-bsn',          # Serial G030M90364563924
    'fca667a8aca2' : 'dash-on2',          # Serial G030QC0372843332
    '000000000000' : 'dash-unasigned1',
    '000000000000' : 'dash_unasigned2'
}
events  = {
    'dash-on'      : 'Focos ON/OFF (ON)',
    'dash-fairy'   : 'Farolas ON/OFF (Fairy)',
    'dash-ambipur' : 'Sin asignar <ambipur>',
    'dash-bsn'     : 'Sin asignar <bsn>',
    'dash-on2'     : 'Sin asignar ON(2)'
}
status  = {
    'dash-on'      : 'off',
    'dash-fairy'   : 'off',
    'dash-ambipur' : 'off',
    'dash-bsn'     : 'off',
    'dash-on2'     : 'off'
}


rawSocket = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.htons(0x0003))

focos = IFTTT_Farolas(False,True)

def flipStatus( status ):
  if status == 'on':
    return 'off'
  else:
    return 'on'



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
    #print " --- ARP from : " + source_mac
    if source_mac in macs:
      buttonId = macs[source_mac]
      status[ buttonId ] = flipStatus( status[buttonId] )

      print "------  Amazon dash button pressed ---------------------"

      print "        Button pressed   : " + buttonId
      print "        Evento  asociado : " + events[buttonId]

      if buttonId  == 'dash-on':
        print "        Status           : " + status[buttonId]
        #focos.turnOnForSeconds(300)
        focos.remoteCall(status[buttonId])

      print "--------------------------------------------------------"
