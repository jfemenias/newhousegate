#!/usr/bin/env python
#get phone number list that can open the gate at the NewHouse
#Located at https://raw.githubusercontent.com/jfemenias/tutorial/initial/newhousegate_whitelist.txt
import urllib2  # the lib that handles the url stuff

import time
import datetime

phonebook = {}

# ----------------- Phonebook Managing Begin -----------------

def get_whitelist():
    phone = []
    owner = []

    # white_list_url = 'https://dl.dropboxusercontent.com/u/36752286/newhousegate_whitelist.txt'
    white_list_url = 'https://raw.githubusercontent.com/jfemenias/tutorial/initial/newhousegate_whitelist.txt'
    try:
        # print 'Accessing data from ' + white_list_url
        data = urllib2.urlopen(white_list_url ) # it's a file like object and works just like a file

        for line in data: # files are iterable
            li=line.strip()

            if not li.startswith("#"):
                phone_number = li.split(",")[0]
                owners_name = li.split(",")[1]
                phone.append(phone_number.strip())
                owner.append(owners_name.strip())
                phonebook[phone_number] = owners_name
                print line.rstrip()
        return phone, owner, phonebook
    except:
        return get_default_whitelist()

def get_default_whitelist():
    phone = []
    owner = []
    phonebook = {}

    phone_number = "seconds_lights_on"
    owners_name = ("600")
    phone.append(phone_number)
    owner.append(owners_name)
    phonebook[phone_number] = owners_name


    phone_number = "testing_lights"
    owners_name = ("False")
    phone.append(phone_number)
    owner.append(owners_name)
    phonebook[phone_number] = owners_name


    phone_number = "651955102"
    owners_name = ("Jose Femenias")
    phone.append(phone_number)
    owner.append(owners_name)
    phonebook[phone_number] = owners_name

    phone_number = "620260812"
    owners_name = "Ana Hermida"
    phone.append(phone_number)
    owner.append(owners_name)
    phonebook[phone_number] = owners_name

    phone_number = "722715028"
    owners_name = "Maria Femenias Hermida"
    phone.append(phone_number)
    owner.append(owners_name)
    phonebook[phone_number] = owners_name
    
    phone_number = "626026842"
    owners_name = "Alberto Femenias Hermida"
    phone.append(phone_number)
    owner.append(owners_name)
    phonebook[phone_number] = owners_name

    phone_number = "647673632"
    owners_name = "Mary Paz"
    phone.append(phone_number)
    owner.append(owners_name)
    phonebook[phone_number] = owners_name
    
    phone_number = "689874360"
    owners_name = "Elsa"
    phone.append(phone_number)
    owner.append(owners_name)
    phonebook[phone_number] = owners_name

    return phone, owner, phonebook

