# -*- coding: utf-8 -*-
"""
Created on Tue May  1 21:01:25 2018
@author: nate9
"""


import os
import pytz
#import dash
#import dash_core_components as dcc
#import dash_html_components as html
import requests
import pprint
import datetime
import calendar
import pandas as pd
import time
import importer as impt


pp = pprint.PrettyPrinter(indent=4)


def print_enphase():
    print("ENPHASE --------------------------")
    param = {'key': os.getenv('ENPHASE_API_KEY'), 'user_id': os.getenv('ENPHASE_USER_ID')}
    api_base = 'https://api.enphaseenergy.com/api/v2/systems'
    resp = impt.get_enphase(api_base, param)
    pp.pprint(dict(resp))


def print_enphaseenergy():

    param = {'key': os.getenv('ENPHASE_API_KEY'), 'user_id': os.getenv('ENPHASE_USER_ID')}
    api_base = 'https://api.enphaseenergy.com/api/v2/systems'
    resp = impt.get_enphase(api_base, param)
    pp.pprint(dict(resp))

def print_solaredgesiteinfo(date=datetime.date.today()):
    print("SOLAREDGE --------------------------")
    site_id = os.getenv('SOLAREDGE_USER_ID')
    api_base = 'https://monitoringapi.solaredge.com/site/{}'.format(site_id)
    # Defaults to today
    param = {'api_key': os.getenv('SOLAREDGE_API_KEY'), 'startDate': date, 'endDate': date}
    resp = impt.get_SEdetails(api_base, param)
    pp.pprint(resp)


def print_solaredge(date=datetime.date.today()):
    site_id = os.getenv('SOLAREDGE_USER_ID')
    api_base = 'https://monitoringapi.solaredge.com/site/{}'.format(site_id)
    # Defaults to today
    param = {'api_key': os.getenv('SOLAREDGE_API_KEY'), 'timeUnit': 'HOUR', 'startDate': date, 'endDate': date}
    df = impt.get_SEenergy(api_base, param)
    pp.pprint(df)


def print_sunnyportal():
    print("SUNNYPORTAL --------------------------")
    resp = impt.get_sunnyportal()
    print(resp)


def main():
    #print_enphase()
    #print_solaredge()
    #print_sunnyportal()
    now = time.time()
    today = calendar.timegm(datetime.date.today())
    print(now)
    print(today)


if __name__ == '__main__':
    main()
