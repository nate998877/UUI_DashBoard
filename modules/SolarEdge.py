import requests
import pandas as pd
import os
from modules.APIInterface import APIInterface


class SolarEgde(APIInterface):
  def __init__(self, api_key, user_id):
    super().__init__('https://monitoringapi.solaredge.com/site/{}'.format(os.environ['SOLAREDGE_USER_ID']), api_key, user_id)



def get_SEdetails(api_base, param):
    resp = requests.get(api_base + '/details', params=param)
    return dict(resp.json())


# Methods call SolarEgde's (Ground) Array and returns API call depending on Method used
def get_SEenergy(api_base, param, dt=None):
    #dt = datetime.datetime.now() if dt is None else dt
    resp = requests.get(api_base + '/energy', params=param)
    resp = dict(resp.json())
    resp = resp.get('energy', {}).get('values')
    df = pd.DataFrame.from_dict(resp)
    df.columns = ['DateTimeUTC', 'MeanPower(KWh)']
    df['DateTimeUTC'] = df['DateTimeUTC'].map(lambda x: x + "+00:00")
    df['MeanPower(KWh)'] = df['MeanPower(KWh)'].map(lambda x: x / 1000)
    return df