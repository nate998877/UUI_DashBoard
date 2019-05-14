import pandas as pd

def pandadance(solaredgedataframe, enphasedataframe, sunnyportaldataframe):
    mergeddataframe = pd.DataFrame(columns=['DateTimeUTC', 'SunnyEdge(KWh)', 'Enphase(KWh)', 'SunnyPortal(KWh)'])
    #mergeddataframe = pd.concat(solaredgedataframe,enphasedataframe,sunnyportaldataframe)
    mergeddataframe['DateTimeUTC'] = solaredgedataframe['DateTimeUTC']
    mergeddataframe['SunnyEdge(KWh)'] = solaredgedataframe['MeanPower(KWh)']
    mergeddataframe[''] = enphasedataframe['MeanPower(KWh)']
    mergeddataframe[''] = sunnyportaldataframe['MeanPower(KWh)']
    return mergeddataframe


def pandaFiEnphase():
  return

def pandaFiSolarEdge():
  return

def pandaFiSunnyPortal():
  return