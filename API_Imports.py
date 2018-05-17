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
import pandas as pd


pp = pprint.PrettyPrinter(indent=4)


def convert_sunnyp_to_datetime(dt, sunnyp_date_str):
    """
    Converts a single sunny_portal timestamp into a datetime object.  Sunny_portal timestamp is an
    abbreviated string that is based on the original requested time window.
    The shortened string in the example format of '2:00 PM/ 13' where 13 is the day of the requested date.
    :param dt: The requested datetime sent to sunny_portal api
    :param sunnyp_date_str: Sunny Portal timestamp string e.g. '2:00 PM/ 13'
    :return: A datetime object that combines both values, and is EST timezone-aware.
    """
    dt_before = dt - datetime.timedelta(days=1)
    dt_after = dt + datetime.timedelta(days=1)
    d = sunnyp_date_str.split('/')

    # In some cases, Sunny Portal returns timestamps from adjacent days.
    if int(d[1]) == dt_before.date().day:
        dt = dt_before
    elif int(d[1]) == dt_after.date().day:
        dt = dt_after
    # combine the correct date with parsed time and apply Eastern Standard Time zone.
    new_dt = datetime.datetime.strptime(str(dt.date()) + ' ' + d[0], '%Y-%m-%d %I:%M %p').replace(tzinfo=pytz.timezone('EST'))
    return new_dt


def get_sunnyportal(dt=None):
    """
    Downloads a csv file from Sunnyportal containing daily energy yield output data.
    :param dt: A datetime object containing the desired date. If not specified (None), it will use today's date.
    :return: A dataframe containing time series hourly values of Mean Solar Power (KWh), with UTC time index
    """
    user_id = os.getenv('SUNNYPORTAL_USER_ID')
    pwd = os.getenv('SUNNYPORTAL_PWD')
    url = 'https://www.sunnyportal.com/Templates/PublicChartValues.aspx'
    dt = datetime.datetime.now() if dt is None else dt

    # perform the api query
    r = None
    with requests.Session() as s:
        s.auth = (user_id, pwd)
        params = {
            'ID': 'c570606c-374e-474d-ac75-bb7759c00845',
            'endTime': '{} 11:59:59 PM'.format(dt.date()),
            'splang': 'en - US',
            'plantTimezoneBias': '-240',  # Use 0 for UTC,  Use -240 for local Indianapolis offset THIS DOES NOT WORK
            'name': 'Day {}'.format(dt.date())
        }
        r = s.get(url, params=params)

    # parse the returned html into pandas dataframe
    if r is not None:
        data = pd.read_html(r.text)
        # select only the first two columns: Timestamp and Mean Power [KWh]
        df = data[0][[0, 1]]
        # drop first row because it contains text headers, not data
        df = df.drop(0)
        # The returned data contains the previous day as well as current day.
        # The Timestamp format is '2:00 PM/ 13' where 13 is the Day.
        # Transform the date stamps into something more standard.
        df[0] = df[0].map(lambda x: convert_sunnyp_to_datetime(dt, x))
        # drop every row that does not match the requested date
        df = df[df[0].map(lambda x: x.date() == dt.date())]
        # convert timestamps to UTC zone
        df[0] = df[0].map(lambda x: x.astimezone(pytz.utc))
        df.columns = ['DateTimeUTC', 'MeanPower(KWh)']
        df.set_index('DateTimeUTC')
        # NOTE that Mean Power still contains NaN values
        return df

#
#Method calls Enphase's (Cottage Rooftop) Array and returns a summary of the system
def get_summary(api_base, param):
    resp = requests.get(api_base , params=param)
    resp.raise_for_status()
    d = dict(resp.json())
    #pp.pprint(d) #removed for clarity, reimpliment if debugging
    system_id = d['systems'][1]['system_id']
    print('The UUI system id is: ', system_id)
    resp = requests.get('{0}/{1}/summary'.format(api_base, system_id), params=param)
    resp.raise_for_status()
    return dict(resp.json())


def main():

    # Get today's sunnyp reading
    df_sunny = get_sunnyportal()
    print(df_sunny)

    param = {'key': os.getenv('ENPHASE_API_KEY'), 'user_id': os.getenv('ENPHASE_USER_ID')}
    api_base = 'https://api.enphaseenergy.com/api/v2/systems'
    resp = get_summary(api_base, param)
    pp.pprint(dict(resp))

    #Methods call SolarEgde's (Ground) Array and returns API call depending on Method used
    def get_details(api_base, param):
        resp = requests.get(api_base + '/details', params=param)
        resp.raise_for_status()
        return  dict(resp.json())

    def get_energy(api_base, param):
        resp = requests.get(api_base + '/energy', params=param,)
        resp.raise_for_status()
        return  dict(resp.json())

    site_id = os.getenv('SOLAREDGE_USER_ID')
    api_base = 'https://monitoringapi.solaredge.com/site/{}'.format(site_id)
    param = {'api_key': os.getenv('SOLAREDGE_API_KEY'), 'startDate': '2018-04-10', 'endDate': '2018-04-10'}
    #date = {'startDate': '2018-04-10 12:00:00', 'endDate': '2018-04-10 23:59:59'}

    details = get_details(api_base, param)
    energy = get_energy(api_base, param)

    pp.pprint(details)
    pp.pprint(energy)

if __name__ == '__main__':
    main()
