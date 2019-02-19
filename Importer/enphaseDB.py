import requests
import sqlite3
import datetime
import pytz


class Enphase:
    def __init__(self):
        self.databasepath = "enphase.db"
        self.connection = sqlite3.connect(self.databasepath)
        self.cursor = self.connection.cursor()

    def create_database(self):
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS historicPower (datetime, power)""")

    def insert_database(self, values):
        self.cursor.execute("""INSERT INTO historicPower (datetime, power) values(?, ?)""", (str(values[0]), str(values[1])))

    def call_database(self, dt):
        self.cursor.execute("""SELECT * FROM historicPower ORDER BY ? DESC LIMIT 1;""", dt)
        rows = self.cursor.fetchall()
        return rows

#if database is empty causes error. DB needs to be initialized w/ data before it's called
    def call_last(self):
        self.cursor.execute("""SELECT * FROM historicPower ORDER BY power DESC LIMIT 1;""")
        return self.cursor.fetchone()[0]

    def printout(self):
        self.cursor.execute("""SELECT * FROM historicPower""")
        rows = self.cursor.fetchall()
        for row in rows:
            print(row)

    def tohour(self, power):
        if power != self.call_last():
            hourpower = power - self.call_last()
            return hourpower
        else:
            return 100


def getvalues(resp):
    values = [0, 0]
    values[0] = datetime.datetime.utcfromtimestamp(resp.get('last_interval_end_at'))
    values[0] = values[0].isoformat(' ')
    values[0] = datetime.datetime.strptime(str(values[0]), '%Y-%m-%d %H:%M:%S').replace(tzinfo=pytz.timezone('EST'))
    values[1] = resp.get('energy_lifetime')
    return values
