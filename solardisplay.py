# -*- coding: utf-8 -*-
"""
Created on Tue May  1 21:01:25 2018
@author: nate9
"""

import os
import pprint
import datetime
import logging
import logging.config
import yaml

from importer import importer as impt

pp = pprint.PrettyPrinter(indent=4)

def config_logger():
    """Setup logging configuration"""
    path = 'logging.yaml'
    with open(path, 'rt') as f:
        config = yaml.safe_load(f.read())
        logging.config.dictConfig(config)
    return logging.getLogger(__name__)


# Create module logger from config file
logger = config_logger()

def print_enphase():
    print("ENPHASE --------------------------")
    param = {'key': os.getenv('ENPHASE_API_KEY'), 'user_id': os.getenv('ENPHASE_USER_ID')}
    api_base = 'https://api.enphaseenergy.com/api/v2/systems'
    resp = impt.get_enphase(api_base, param)
    pp.pprint(resp)
    impt.enphase(resp)


def print_solaredgesiteinfo(date=datetime.date.today()):
    print("SOLAREDGE --------------------------")
    site_id = os.getenv('SOLAREDGE_USER_ID')
    api_base = 'https://monitoringapi.solaredge.com/site/{}'.format(site_id)
    # Defaults to today
    param = {'api_key': os.getenv('SOLAREDGE_API_KEY'), 'startDate': date, 'endDate': date}
    resp = impt.get_SEdetails(api_base, param)
    pp.pprint(resp)


def print_solaredge(date=datetime.date.today()):
    print("SUNNYEDGE --------------------------")
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


def log_start_stop(start_dt=None):
    """logs a startup or shutdown banner that is easy to spot"""
    dashed_line = '\n' + '-' * (len(__file__) + 15)
    if not start_dt:
        start_dt = datetime.datetime.now()
        loglevel = logging.getLevelName(logger.getEffectiveLevel())
        fmt = (
            dashed_line + '\n'
            '    Running ' + __file__ + '\n'
            '    Started on %s\n'
            '    Loglevel is %s'
            + dashed_line
        )
        logger.info(fmt % (start_dt.isoformat(), loglevel))
    else:
        uptime = datetime.datetime.now() - start_dt
        fmt = (
            dashed_line + '\n'
            '    Stopped ' + __file__ + '\n'
            '    Uptime was %s'
            + dashed_line
        )
        logger.info(fmt % str(uptime))
    return start_dt

# methods currently only return values from today in kWh
def main():
    
    # Indicate application startup in logs
    app_start_time = log_start_stop()

    print_enphase()
    print_solaredge()
    print_sunnyportal()

    # Indicate app shutdown in logs
    log_start_stop(app_start_time)
    logging.shutdown()


if __name__ == '__main__':
    main()
