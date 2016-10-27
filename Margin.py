#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Plot margin account dynamics of $1 sold Oil
Created on Wed Oct 5 18:23:48 2016

@author: jonesthomas
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import datetime as dt
from dateutil.relativedelta import relativedelta

#set initial margin and maintenance margin as % of spot
margin_init = 0.75
margin_main = 0.70

#get start date of contract and length of contract
start_date = dt.date(2013,1,1)
contract_length = 12

#get spot oil prices
oil_spot_cli = pd.read_excel("Spot.xlsx","CLI",index_col = 0) #for oil in Chicago
oil_spot_wti = pd.read_excel("Spot.xlsx","USCRWTIC",index_col = 0) #for oil in NYMEX

#% by which price must rise to get margin call
margin_trig = margin_main/margin_init
futures_price = 50


end_date = start_date + relativedelta(months=contract_length)

start_date = start_date.strftime('%Y/%m/%d')
end_date = end_date.strftime('%Y/%m/%d')

#oil prices for duration of contract
oil_price_cli = oil_spot_cli.loc[start_date:end_date]
oil_price_wti = oil_spot_wti.loc[start_date:end_date]

oil_price_cli = oil_price_cli[[0]]
oil_price_wti = oil_price_wti[[0]]

#returns calculation
oil_ret_cli = oil_price_cli.shift(-1) / oil_price_cli-1
oil_ret_wti = oil_price_wti.shift(-1) / oil_price_wti-1

#cumulative returns
oil_level_cli = oil_ret_cli.expanding().apply(lambda x:np.prod(1+x))
oil_level_wti = oil_ret_wti.expanding().apply(lambda x:np.prod(1+x))

#value of short position
oil_short_cli= 1/oil_level_cli
oil_short_wti= 1/oil_level_wti

plt.figure(figsize=(12,6))
plt.plot(oil_short_cli, label='value of short', color='c')

ix =0;
margin_called = oil_short_cli.copy()
margin_called[:]=0

for index,row in oil_short_cli.iterrows():
    if row.values[0] < margin_trig: #check if margin call
        margin_called.iloc[ix] = 1-row.values[0]
        oil_short_cli.iloc[ix+1:]= oil_short_cli.iloc[ix+1:]/oil_short_cli.iloc[ix+1]
    ix = ix+1

cum_margin = margin_called.cumsum() #total margin required

plt.plot(oil_short_cli-1+margin_init, label='margin account level', color='b')
plt.plot(margin_called, label='margin call', drawstyle='steps',color='r')
plt.plot(cum_margin, label='total additional margin posted', drawstyle='steps',color='y')
plt.xlabel('Date')
plt.axhline(y=margin_main, color='m', label = 'maintenance margin')
plt.axhline(y=margin_init, color='k', label = 'initial margin')
plt.legend(loc='upper left', prop={'size':6}, bbox_to_anchor=(1,1))

plt.annotate('%0.2f' % cum_margin.max(), xy=(1, cum_margin.max()), xytext=(8, 0),
                 xycoords=('axes fraction', 'data'), textcoords='offset points')

plt.tight_layout(pad=7)
plt.show()