#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 26 22:35:57 2016

@author: jonesthomas
"""

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
from datetime import datetime as dt
from dateutil.relativedelta import relativedelta


#####################################################

def calc_margin_contrib(start_dat,contract_length,irate,oil_spot_cli,margin_init,margin_main):

    #start_date = dt.strptime(start_dat, '%Y-%m-%d').date()

    #% by which price must rise to get margin call
    margin_trig = margin_main/margin_init

    end_date = start_dat + relativedelta(months=contract_length)
    start_date = start_dat.strftime('%Y/%m/%d')
    end_date = end_date.strftime('%Y/%m/%d')

    oil_price_cli = oil_spot_cli.loc[start_date:end_date]
    oil_price_cli = oil_price_cli[[0]]
    oil_ret_cli = oil_price_cli.shift(-1) / oil_price_cli-1
    oil_level_cli = oil_ret_cli.expanding().apply(lambda x:np.prod((1+x)*(1+irate)))
    oil_short_cli= 1/oil_level_cli

    ix =0;
    margin_called = oil_short_cli.copy()
    margin_called[:]=0

    for index,row in oil_short_cli.iterrows():
        if row.values[0] < margin_trig: #check if margin call
            margin_called.iloc[ix] = 1-row.values[0]
            oil_short_cli.iloc[ix+1:]= oil_short_cli.iloc[ix+1:]/oil_short_cli.iloc[ix+1]
        ix = ix+1

    cum_margin = margin_called.cumsum() #total margin required

    return(cum_margin.max())

#####################################################

#get spot oil prices
oil_spot_cli = pd.read_excel("Spot.xlsx","CLI",index_col = 0) #for oil in Chicago
oil_spot_cli = oil_spot_cli.loc['2010-01-01':'2016-10-01']


future_length=6
margin_initial = 0.7
margin_maintenance = 0.6
interest_rate = 0.03/250

margin_called = oil_spot_cli[[0]].copy()
margin_called[:]=0

ix=0;

for index,row in oil_spot_cli.iterrows():
    y = calc_margin_contrib(index,future_length,interest_rate,oil_spot_cli,margin_initial,margin_maintenance)
    margin_called.values[ix] =y
    ix = ix+1

plt.figure(figsize=(12,4))
plt.plot(margin_called)
plt.xlabel('Date')
plt.show()

