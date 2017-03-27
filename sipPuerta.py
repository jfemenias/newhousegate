#!/usr/bin/env python
#get phone number list that can open the gate at the NewHouse
#Located DropBox jose.femenias@hermida.com, Carpeta Public, Fichero whitelist.xt
import urllib2  # the lib that handles the url stuff
import os
import linphone
import logging
import signal
import time
import datetime

import re
import RPi.GPIO as GPIO
import urllib2
import smtplib
import json
from datetime import timedelta
from sip_whitelist import *
from sip_luces import *

GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.OUT) ## GPIO 17 as out
GPIO.setup(27, GPIO.OUT) ## GPIO 27 as out


#last_email_datetime = datetime.datetime.now()

def elapsedMoreThan( timeInSeconds ):
    if "lastTime" not in vars(elapsedMoreThan): elapsedMoreThan.lastTime=time.time()
    interval =  time.time() - elapsedMoreThan.lastTime
    elapsedMoreThan.lastTime=time.time()
    # print "Time elapsed = " + str( interval )
    return ( interval ) > timeInSeconds

def send_email(recipient, subject):
    os.system('python sip_email.py "' + subject + '"' )


def send_email_obsolete(recipient, subject):
    print "sending email..."
#    if not elapsedMoreThan( 10 ):
#	return
#    gmail_user = 'pepe.femenias@gmail.com'
    gmail_user = 'newhousegate@gmail.com'
    gmail_pwd = 'newhousegate.google'
#    gmail_pwd = 'crbgkzyeivwkuuqg'
    FROM = "NewHouseGate"
    TO = recipient if type(recipient) is list else [recipient]
    SUBJECT = subject
    TEXT = subject +" has just opened/closed the gate"

    # Prepare actual message
    message = """From: %s\nTo: %s\nSubject: %s\n\n%s
    """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()
        server.login(gmail_user, gmail_pwd)
        server.sendmail(FROM, TO, message)
        server.close()
        print 'successfully sent the mail: ' + subject
    except:
        print "failed to send mail"
    last_email_datetime = datetime.datetime.now()

class sipPuerta:
  def __init__(self, username='', password='', whitelist=[]):
    self.openDoor = False
    self.callerId = ""
    self.timeOpenDoor = 0
    self.maxTimeOpenedDoor = 2 #seconds
    self.quit = False 
    self.f = IFTTT_Farolas(self.testing_lights(),True)
    self.whitelist = whitelist
    callbacks = {
      'call_state_changed': self.call_state_changed,
    }

    # Configure the linphone core
    logging.basicConfig(level=logging.INFO,filename='/tmp/sipPuerta.log',filemode='w')
    linphone.set_log_handler(self.log_handler)
    self.core = linphone.Core.new(callbacks, None, None)
    self.core.disable_chat(linphone.Reason.NotImplemented) 
    self.core.echo_cancellation_enabled = False
    self.core.video_capture_enabled = False
    self.core.video_display_enabled = False
    self.core.mic_enabled = False
    self.ring_during_incoming_early_media = False
    self.core.stun_server = 'stun.linphone.org'
    self.core.firewall_policy = linphone.FirewallPolicy.PolicyUseIce

    self.configure_sip_account(username, password)

  def num(self,s):
    try:
      return int(s)
    except:
      return 0

  def seconds_lights_on(self):
    return self.num(phonebook['seconds_lights_on'])

  def testing_lights(self):
    return phonebook['testing_lights'].strip()=='True'

  def signal_handler(self, signal, frame):
    self.core.terminate_all_calls()
    self.quit = True

  def log_handler(self, level, msg):
    method = getattr(logging, level)
    method(msg)

  def call_state_changed(self, core, call, state, message):
    if state == linphone.CallState.IncomingReceived:
      #if call.remote_address.as_string_uri_only() in self.whitelist:
      phoneNumber = self.getOnlyNumber(call.remote_address.as_string_uri_only())
      self.callerId = phoneNumber
      if phoneNumber  in self.whitelist:
        core.decline_call(call, linphone.Reason.Declined)
        logging.info("On whitelist!!, hang up and open door for "+ phoneNumber)
        print( "On whitelist!!, hang up and open door for "+ phoneNumber)
        #if elapsedMoreThan(10):
        self.openDoor = True # JFC MARZO 2017

  def configure_sip_account(self, username, password):
    # Configure the SIP account
    proxy_cfg = self.core.create_proxy_config()
    proxy_cfg.identity = 'sip:{username}@telefonoweb.com'.format(username=username)
    proxy_cfg.server_addr = 'sip:callproxy.mundo-r.com;transport=udp'
    proxy_cfg.register_enabled = True
    self.core.add_proxy_config(proxy_cfg)
    auth_info = self.core.create_auth_info(username, None, password, None, None, 'telefonoweb.com')
    self.core.add_auth_info(auth_info)

  def getOnlyNumber(self, infoCallIn):
    try:
      numberCaller = re.match("[^:]\D*(\d{9,})[^@]*", infoCallIn)
      if numberCaller:
        strNumberCall = numberCaller.group(1)[-9:]
        return strNumberCall
      else:
        return ""
    except Exception, e:
      return ""

  def chkOpenDoor(self):
    if self.openDoor:
      print "Must open door..."
      self.sendOpenDoorArduino(self.maxTimeOpenedDoor, 1)
      self.f.turnOnForSeconds(self.seconds_lights_on())
      # GPIO.output(17, True) ## enable relay on gpio17
      self.openDoor = False
      self.timeOpenDoor = time.time()
    else:
      if time.time() > (self.timeOpenDoor + self.maxTimeOpenedDoor):
        # GPIO.output(17, False) ## disable relay on gpio17
        self.openDoor = False

  def sendOpenDoorArduino(self, valTimeout, valSalida):
#    if not elapsedMoreThan( 30 ):
#	return
    try:
      timestampVal = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
      logging.info(str(timestampVal) + ": Send open door Arduino valTimeout: <"+str(valTimeout)+">")
      url =  'http://192.168.1.13'
      req = urllib2.Request(url)
      response = urllib2.urlopen(req, timeout=10)
      thePage = response.read()

      posXini = thePage.index('x=')
      posXend = thePage.index('<br>')
      #print thePage[posXini:posXend]
      tmpArrayValues = thePage[posXini:posXend].split(' ')
      dictValues = dict(s.split('=') for s in tmpArrayValues)
      #print d
      #send_email("jose.femenias@gmail.com","Gate activity")


      if(dictValues):
        print "sendOpenDoorArduino.A"
        if (('x' in dictValues) and ('y' in dictValues)):
          print "sendOpenDoorArduino.B"
          resultado = (int(dictValues['x'])*int(dictValues['y'])) % 49339
          strResultado = str(resultado)
          print "sendOpenDoorArduino.C Resultado: ", strResultado
          url =  'http://192.168.1.13/?uptime=' + str(valTimeout) + '&salida=' + str(valSalida)  + '&token='+strResultado.zfill(5)
          req = urllib2.Request(url)
          response = urllib2.urlopen(req, timeout=10)
          thePage = response.read()
          print "sendOpenDoorArduino.D Response OK"
          #print "OK" #print thePage
          timestampVal = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
          logging.info(str(timestampVal) + ": URL "+str(url))
          print "sendOpenDoorArduino.E About to send email"
          send_email( "jose.femenias@gmail.com", self.callerId + " : " + phonebook[self.callerId]) 
          #send_email( "jose.femenias@gmail.com","NewHouse Activity " + phoneNumber + " : " + phonebook[phoneNumber] )
          #send_email("jose.femenias@gmail.com","NewHouseGate activity" )
    except Exception, e:
      timestampVal = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
      logging.info(str(timestampVal) + ": Error sendOpenDoorArduino: <"+str(e)+">")
      pass

  def run(self): 

    while not self.quit:
      self.core.iterate()
      time.sleep(0.01) #0.03 el 25 Marzo 2017
      self.f.turnOff_if_needed()
      self.chkOpenDoor()

def main():
  white_list_url = 'https://raw.githubusercontent.com/jfemenias/tutorial/initial/newhousegate_whitelist.txt'
  white_list_numbers, white_list_names, white_list_phonebook = get_whitelist()

  cam = sipPuerta(username='09821409xx', password='47xxxxxx', whitelist=white_list_numbers) 

  cam.run()
  GPIO.cleanup() ## clear all GPIO

main()
