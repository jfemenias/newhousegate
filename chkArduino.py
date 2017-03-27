#!/usr/bin/env python

import urllib2
import sys

url =  'http://192.168.1.13/?uptime=' + str(sys.argv[1]) + '&salida=' + str(sys.argv[2])

req = urllib2.Request(url)
response = urllib2.urlopen(req)
thePage = response.read()
