import requests
from modules.APIInterface import APIInterface


class Enphase(APIInterface):
  def __init__(self, api_key, user_id):
    super().__init__('https://api.enphaseenergy.com/api/v2/systems', api_key, user_id)

  def get_rawdata(self):
    """
    Fetches today's raw data
    TODO add ability to fetch different days
    """
    params={
        'key': self.apikey,
        'user_id': self.user_id
      }
    system_id_request = requests.get(self.api_base, params=params)
    parsedJson = dict(system_id_request.json())
    system_id = parsedJson['systems'][1]['system_id']
    self.rawData = requests.get('{0}/{1}/summary'.format(self.api_base, system_id), params=params)
    return dict(self.rawData.json())

  def queryDB(self):
    db = EnphaseDB()
    return db.call_last()

  def initDB(self, response):
    db = EnphaseDB()
    db.create_database()
    values = db.getvalues(response)
    try:
      values[1] = db.tohour(values[1])
    except TypeError:
      db.insert_database(values)
    df = EnphaseDB.db_to_df(db)
    db.printout()
    return df

  def enphase(response):
	database = enphaseDB.Enphase()
	database.create_database()
	values = enphaseDB.getvalues(response)
	try:
		values[1] = database.tohour(values[1])
	except TypeError:
		database.insert_database(values)
	df = db_to_df(database)
	database.printout()
	return df





# Method calls Enphase's (Cottage Rooftop) Array and returns a summary of the system
def get_enphase(api_base, param):
	resp = requests.get(api_base, params=param)
	d = dict(resp.json())
	system_id = d['systems'][1]['system_id']
	resp = requests.get(
		'{0}/{1}/summary'.format(api_base, system_id), params=param)
	return dict(resp.json())

# values are datetime and generation


def enphase(response):
	database = enphaseDB.Enphase()
	database.create_database()
	values = enphaseDB.getvalues(response)

	try:
		values[1] = database.tohour(values[1])
	except TypeError:
		database.insert_database(values)
	df = db_to_df(database)
	database.printout()
	return df


# send to pandapandapanda to be converted to panda
def db_to_df(db):
	df = pd.read_sql_query("SELECT * FROM historicPower", db.connection)
	df.columns = ['DateTimeUTC', 'MeanPower(KWh)']
	df['MeanPower(KWh)'] = df['MeanPower(KWh)'].map(lambda x: int(x) / 1000)
	return df


import sqlite3
import datetime
import pytz


#if database is empty causes error. DB needs to be initialized w/ data. This is done automatically.
class EnphaseDB:
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

  def call_last(self):
    self.cursor.execute("""SELECT * FROM historicPower ORDER BY power DESC LIMIT 1;""")
    return self.cursor.fetchone()[0]

  def printout(self):
    self.cursor.execute("""SELECT * FROM historicPower""")
    rows = self.cursor.fetchall()
    for row in rows:
      print(row)
    self.connection.commit()

  def tohour(self, power):
    if power != self.call_last():
      hourpower = power - self.call_last()
      return hourpower
    else:
      return 100

  def getvalues(self, resp):
    values = [0, 0]
    values[0] = datetime.datetime.utcfromtimestamp(resp.get('last_interval_end_at')).isoformat(' ')
    values[0] = datetime.datetime.strptime(str(values[0]), '%Y-%m-%d %H:%M:%S').replace(tzinfo=pytz.timezone('EST'))
    values[1] = resp.get('energy_today')
    return values

  def hourlypower(self, values):
    return 1 - 2