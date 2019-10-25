import requests
import pandas as pd
import os
import datetime
from modules.APIInterface import APIInterface


class SolarEgde(APIInterface):
    def __init__(self, api_key, user_id):
        super().__init__('https://monitoringapi.solaredge.com/site/{}'.format(
            os.environ['SOLAREDGE_USER_ID']), api_key, user_id)

    def get_rawdata(self):
        date = datetime.date.today()
        resp = requests.get(self.api_base + '/energy', params={
                            'api_key': self.api_key, 'timeUnit': 'HOUR', 'startDate': date, 'endDate': date})
        resp = dict(resp.json())
        resp = resp.get('energy', {}).get('values')
        df = pd.DataFrame.from_dict(resp)
        df.columns = ['DateTimeUTC', 'MeanPower(KWh)']
        df['DateTimeUTC'] = df['DateTimeUTC'].map(lambda x: x + "+00:00")
        df['MeanPower(KWh)'] = df['MeanPower(KWh)'].map(lambda x: x / 1000)
        return df

    # this goes unused for now
    def get_sitedata(self):
        date = datetime.date.today()
        resp = requests.get(self.api_base + '/details', params={
                            'api_key': self.api_key, 'timeUnit': 'HOUR', 'startDate': date, 'endDate': date})
        return dict(resp.json())
