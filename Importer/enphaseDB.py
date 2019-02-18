import requests
import sqlite3
import os

# Method calls Enphase's (Cottage Rooftop) Array and returns a summary of the system
def get_enphase(api_base, param):
    resp = requests.get(api_base, params=param)
    d = dict(resp.json())
    system_id = d['systems'][1]['system_id']
    resp = requests.get('{0}/{1}/summary'.format(api_base, system_id), params=param)
    return dict(resp.json())


def initalize(db_path):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
#    c.execute("""CREATE DATABASE IF NOT EXISTS enphase""")
    c.execute("""CREATE TABLE IF NOT EXISTS historicPower (date, time, power)""")
    return conn;


def add(c, values):
    insert = """INSERT INTO historicPower (date, time, power) values({0}, {1}, {2})"""
    c.execute(insert.format(values[0], values[1], values[2]))


def call(c):
    print(c)
    c.execute("""SELECT * FROM historicPower""")
    rows = c.fetchall()
    for row in rows:
        print(row)
