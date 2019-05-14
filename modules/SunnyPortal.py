import datetime
import os
import requests
import pytz
from modules.APIInterface import APIInterface
from bs4 import BeautifulSoup as bs

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

    user_id = os.environ['SUNNYPORTAL_USER_ID']

    pwd = os.environ['SUNNYPORTAL_PWD']
    
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
    if r.text is not None:
        if sunnyPortalDataCheck(r.text) == -1:
            return
        else:
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

def sunnyPortalDataCheck(html):
    """
    Takes an HTML page and searches for instance of error message
    :html: Raw HTML from sunnyPortal endpoint
    """
    prettyHtml = bs(html, features="lxml")
    liTag = prettyHtml.find('li')
    status, _, date = liTag.contents
    if status.find("Raw data for the display period is not availt available."):
        return -1