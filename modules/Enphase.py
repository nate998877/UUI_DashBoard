import requests
import sqlite3
import datetime
import pytz
import pandas as pd
from modules.APIInterface import APIInterface


class Enphase(APIInterface):
    def __init__(self, api_key, user_id):
        super().__init__('https://api.enphaseenergy.com/api/v2/systems', api_key, user_id)
        self.init_db_connection()
        self.params = {
            'key': self.api_key,
            'user_id': self.user_id
        }

    def init_db_connection(self):
        self.db = sqlite3.connect("data/enphase.db")
        self.cursor = self.db.cursor()
        self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS historicPower (unixTime, energy_lifetime, energy_today)""")

    def main(self):
        """Envokes all nessasary functions to construct a dataframe out of database values that are being updated
        """
        self.get_system_summary()
        if(self.update_db()): return
        self.create_df()
        self.close_connection()
        return self.df

    def get_system_summary(self):
        """Fetches raw site data from Enphase api
        """
        resp = requests.get(self.api_base, params=self.params).json()
        system_id = resp['systems'][1]['system_id']
        resp = requests.get(
            '{0}/{1}/summary'.format(self.api_base, system_id), params=self.params)
        self.raw_data = resp.json()


    #there might be a better way to handle this, but I'm not sure how.
    def update_db(self):
        """Inserts energy_lifetime and energy_total from raw data into sql database
        """
        if(self.raw_data):
            report_time_utc = datetime.datetime.utcfromtimestamp(
                self.raw_data["last_report_at"])
            dt = datetime.datetime(*report_time_utc.timetuple()[:4])
            # This is supposed to be run every hour @ 1 minute past the hour.
            # The hour saved in the database rounds down to the nearest hour so 11:59 => 11:00
            values = [dt, self.raw_data["energy_lifetime"],
                      self.raw_data["energy_today"]]
            self.cursor.execute(
                """INSERT INTO historicPower (unixTime, energy_lifetime, energy_today) values(?, ?, ?)""", values)
            return 0
        else:
            return 1

    def create_df(self):
        """fetches data from db and constructs self.df from the returned values
        """
        self.cursor.execute(
            """SELECT unixTime, energy_today FROM historicPower ORDER BY unixTime DESC LIMIT 24;""")
        rows = self.cursor.fetchall()
        self.df = pd.DataFrame(list(filter(lambda x: x[0] == rows[0][0], rows)), 
                                columns=['DateTimeUTC', 'MeanPower(KWh)'])

    def close_connection(self):
        """saves and closes database connection
        """
        self.db.commit()
        self.db.close()