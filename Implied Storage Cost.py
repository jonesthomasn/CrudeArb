#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 27 10:15:28 2016

@author: jonesthomas
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import datetime as dt
from dateutil.relativedelta import relativedelta
import quandl as qd

oil_spot_cli = pd.read_excel("Spot.xlsx","CLI",index_col = 0)
oil_spot_wti = pd.read_excel("Spot.xlsx","USCRWTIC",index_col = 0)

interest_rates = qd.get('FED/RILSPDEPM01_N_B') #daily 1M

oil_futures_ice = pd.read_excel("ICE.xlsx","ICE WTI",index_col = 0)
oil_futures_nymex = pd.read_excel("NYMEX.xlsx","NYMEX",index_col = 0)

fut_ice_price = pd.DataFrame(index = oil_futures_ice.index,data = oil_futures_ice[[0]]).copy()
fut_ice_price.index.name = 'Date'
fut_ice_volume = pd.DataFrame(index = oil_futures_ice.index,data = oil_futures_ice[[1]]).copy()
fut_ice_volume.index.name = 'Date'

for x in range(2,len(oil_futures_ice.columns)-3,3):
    values_price = pd.DataFrame(data = oil_futures_ice[[x,x+1]])
    values_volume = pd.DataFrame(data = oil_futures_ice[[x,x+2]])

    values_price = values_price.set_index(values_price.columns.values[0])
    fut_ice_price = fut_ice_price.join(values_price)
    fut_ice_price = fut_ice_price[pd.notnull(fut_ice_price.index)]

    values_volume = values_volume.set_index(values_volume.columns.values[0])
    fut_ice_volume = fut_ice_volume.join(values_volume)
    fut_ice_volume = fut_ice_volume[pd.notnull(fut_ice_volume.index)]


fut_nymex_price = pd.DataFrame(index = oil_futures_ice.index,data = oil_futures_ice[[0]]).copy()
fut_nymex_price.index.name = 'Date'
fut_nymex_volume = pd.DataFrame(index = oil_futures_ice.index,data = oil_futures_ice[[1]]).copy()
fut_nymex_volume.index.name = 'Date'

for x in range(2,len(oil_futures_ice.columns)-3,3):
    values_price = pd.DataFrame(data = oil_futures_nymex[[x,x+1]])
    values_volume = pd.DataFrame(data = oil_futures_nymex[[x,x+2]])

    values_price = values_price.set_index(values_price.columns.values[0])
    fut_nymex_price = fut_nymex_price.join(values_price)
    fut_nymex_price = fut_nymex_price[pd.notnull(fut_nymex_price.index)]

    values_volume = values_volume.set_index(values_volume.columns.values[0])
    fut_nymex_volume = fut_nymex_volume.join(values_volume)
    fut_nymex_volume = fut_nymex_volume[pd.notnull(fut_nymex_volume.index)]

cli_X6Spot = pd.DataFrame(index = oil_spot_cli.index, data=oil_spot_cli[[0]])
cli_X6Spot.index.name = 'Date'
cli_X6Spot = cli_X6Spot.join(fut_ice_price["ENX6_PRICE"])
cli_X6Spot = cli_X6Spot.join(interest_rates)
cli_X6Spot = cli_X6Spot[pd.notnull(cli_X6Spot.index)]
cli_X6Spot.rename(columns = {'PRICE ':'SPOT'}, inplace = True)
cli_X6Spot.rename(columns = {'Value':'IRate'}, inplace = True)

carry_cost = pd.DataFrame(index = oil_spot_cli.index)
cli_X6Spot['DateV'] =pd.to_datetime(cli_X6Spot.index)
cli_X6Spot['TTM'] = cli_X6Spot['DateV'].map(lambda row :(dt.datetime(2016,11,16).date()-row.date()).days/250)
carry_cost['Cost'] = np.log(cli_X6Spot['ENX6_PRICE']/cli_X6Spot['SPOT'])/cli_X6Spot['TTM'] -cli_X6Spot['IRate'].shift(1)/1200
carry_cost = 100* carry_cost

plt.figure(figsize=(8,4))
plt.xlabel('Date')
plt.title('Implied Cost of Carry')
plt.plot(carry_cost, label='Cost in % per month')