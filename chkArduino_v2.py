#!/usr/bin/env python

import urllib2
import sys


try:
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

  if(dictValues):
    if (('x' in dictValues) and ('y' in dictValues)):
      resultado = (int(dictValues['x'])*int(dictValues['y'])) % 49339
      #print resultado

      url =  'http://192.168.1.13/?uptime=2&salida=2&token='+str(resultado)
      req = urllib2.Request(url)
      response = urllib2.urlopen(req, timeout=10)
      thePage = response.read()
      print "OK" #print thePage
except Exception, e:
  pass
