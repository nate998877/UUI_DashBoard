# -*- coding: utf-8 -*-
"""
Created on Tue May  1 21:01:25 2018

@author: nate9
"""


import os
#import dash
#import dash_core_components as dcc
#import dash_html_components as html
import requests
import pprint
import datetime
#import urllib3

pp = pprint.PrettyPrinter(indent=4)


def get_sunnyportal(dt=None):
    """
    Downloads a csv file from Sunnyportal containing daily energy yield output data.
    :param dt: A datetime object containing the desired date. If not specified (None), it will use today's date.
    :return:
    """
    base_url = 'https://www.sunnyportal.com'
    user_id = os.getenv('SUNNYPORTAL_USER_ID')
    pwd = os.getenv('SUNNYPORTAL_PWD')

    # compose the url
    dt = datetime.datetime.now() if dt is None else dt
    url = 'https://www.sunnyportal.com/Templates/PublicChartValues.aspx'

    # perform the query
    with requests.Session() as s:
        s.auth = (user_id, pwd)
        params = {
            'ID': 'c570606c-374e-474d-ac75-bb7759c00845',
            'endTime': '{} 11:59:59 PM'.format(dt.date()),
            'splang': 'en - US',
            'plantTimezoneBias': '-240',
            'name': 'Day {}'.format(dt.date())
        }

        r = s.get(url, params=params)
        # NOTE the response content at this point is still in html .. needs translation to a dataframe.
        # Ensure that the string 'UUI String Inverter Solar' is somewhere in the response.
        print r.content
    pass


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
    some_date = datetime.datetime.strptime('May 13 2018', '%b %d %Y')
    get_sunnyportal(some_date)

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
