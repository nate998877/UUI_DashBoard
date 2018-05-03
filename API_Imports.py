# -*- coding: utf-8 -*-
"""
Created on Tue May  1 21:01:25 2018

@author: nate9
"""

import urllib
import contextlib
import json

#imports API key and user ID
with open('config.txt', 'r') as file:
    API = file.readline().rstrip()
    User = file.readline().rstrip()

#Imports User info and Prints for debugging
URL = ('https://api.enphaseenergy.com/api/v2/systems?key=' + API + '&user_id=' + User)
with contextlib.closing(urllib.request.urlopen(URL)) as enlighten:
    print(json.loads(enlighten.read()))