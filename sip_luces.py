#!/usr/bin/env python
import urllib2  # the lib that handles the url stuff
import time
import datetime
import smtplib
import json
from datetime import timedelta

# ----------------- IFTT_Farolas Begin        -----------------

class IFTTT_Farolas:

    def __init__(self, testing_lights_mode,  show_debug_messages):

        self.description = "Class to control external lights in Grandaquia"
        self.author = "JFC"
        self.light_is_on = False
        self.on_until_time = datetime.datetime.now()
        self.failed_attempts = 0
        self.min_retry_seconds = 1
        self.retry_after_seconds = self.min_retry_seconds # Will double until < max_retry_seconds
        self.max_retry_seconds = 16
        self.send_message_after_this_many_failed_attempts = 5
        self.sunrise = datetime.datetime.utcnow().time()
        self.sunset = datetime.datetime.utcnow().time()
        self.lastDateCalled = datetime.date(1970,1,1)

        self.debug = show_debug_messages
        self.testing_lights = testing_lights_mode

    def utc_string_to_local(self, utc_dt):

       # local_tz = pytz.timezone('Europe/Paris') # use your local timezone name here
       # local_dt = utc_dt.replace(tzinfo=pytz.utc)
       # return local_tz.normalize(local_dt) # .normalize might be unnecessary
        return utc_dt


    def isDarkNow(self):

       	if self.testing_lights: return True
        now = datetime.datetime.utcnow().time()

        if self.lastDateCalled == datetime.datetime.today().date():
            #print "There was a previous call:"
            #print " Sunrise = " , self.sunrise
            #print " Sunrset = " , self.sunset
            return (now < self.sunrise ) or (now > self.sunset)
        else:
            print "FIRST CALL TO RETRIEVE ASTRONOMICAL DATA FROM HTTP API !!!"

        self.lastDateCalled = datetime.datetime.today().date()
        print "lastDateCalled = ", self.lastDateCalled

        try:
            print 'Reading astronomical data '
            api_result = urllib2.urlopen('http://api.sunrise-sunset.org/json?lat=43.558294&lng=-7.264564&date=today' )
            json_data = api_result.readline()
            print "API result : " + json_data
            data=json.loads(json_data)
            print 'Astronomical data retrieved '

            self.sunrise = datetime.datetime.strptime(data["results"]["civil_twilight_begin"], '%I:%M:%S %p').time()
            self.sunset  = datetime.datetime.strptime(data["results"]["civil_twilight_end"], '%I:%M:%S %p').time()

        except Exception, e:

            print 'Failed to retrieve astronomical data : ' + str(e)
            month_now =  datetime.datetime.now()
            month_number = month_now.month-1
            amanecer_mes =  ['08:38','08:25','07:48','07:58','07:14','06:47','06:49','07:13','07:43','08:12','07:45','08:19']
            anochecer_mes = ['17:57','18:31','19:05','20:38','21:09','21:38','21:47','21:28','20:45','19:55','18:10','17:47']

            self.sunrise = (datetime.datetime.strptime(amanecer_mes[month_number],"%H:%M")-timedelta(minutes = 120)).time()
            self.sunset  = (datetime.datetime.strptime(anochecer_mes[month_number],"%H:%M")-timedelta(minutes = 120)).time()



        #print "Surise = ", self.sunrise
        #print "Now = ", now
        #print "Sunset = ", self.sunset
        isdark = (now < self.sunrise ) or (now > self.sunset)
        return isdark

    def remoteCall(self, event_on_off):
            url = 'https://maker.ifttt.com/trigger/farolas_' + event_on_off + '/with/key/gOjFZ8UzHTOf91UXNnXD_y5vWESpYw2QmOffX2PyTzo'
            req = urllib2.Request(url)
            try:
                urllib2.urlopen(req)
                self.retry_after_seconds = self.min_retry_seconds
                return True
            except Exception as e:
                self.failed_attempts += 1
                self.retry_after_seconds *= 2
                if self.retry_after_seconds > self.max_retry_seconds:
                    self.retry_after_seconds = self.max_retry_seconds
                # Send a message
                if (self.failed_attempts % self.send_message_after_this_many_failed_attempts) == 0:
                    self.send_alert_mail()
                return False

    def send_alert_mail(self):
        if self.debug: print "Sending alert mail after %i failed attempts to turn lights on-off" % self.failed_attempts
        return

    def turnOnForSeconds(self, seconds):
        if self.isDarkNow():
            if self.debug : print "Yes it is DARK..."
        else:
            if self.debug: print "Not dark until " , self.sunset, self.utc_string_to_local(self.sunset)
            return 
        self.light_is_on = True
        # Placed before the call intentionally
        # Just to make sure the off call will be triggered in any event
        if self.remoteCall('on'):

            # Actual call goes here
            self.on_until_time = datetime.datetime.now() + datetime.timedelta(0,seconds)
            if self.debug: print "Lights on for %i seconds until: " % seconds, self.on_until_time
        else:
            if self.debug: print "There was a problem with the IFTTT call. Lights are NOT on"

    def turnOff_if_needed(self):
        if not self.light_is_on:
	    if int(time.time()) % 600  == 0: #Turn lights off every n seconds, just in case the last off command failed
		self.remoteCall('off')
		time.sleep(1) # To make sure it doesn't call repeatedly within the nth second
            return
        else:
            current_time = datetime.datetime.now()
            if (current_time < self.on_until_time):
                return
            else:
                # Call turn light off

                if self.remoteCall('off'):
                    self.light_is_on = False
                    if self.debug: print "Light is off"
                else:
                    self.on_until_time = datetime.datetime.now() + datetime.timedelta(0, self.retry_after_seconds)
                    if self.debug: print "The light off call didn't work. Will retry after %i seconds" % self.retry_after_seconds

# ----------------- IFTT_Farolas End          -----------------
