# -*- coding: utf-8 -*-
"""
Created on Mon Oct 31 13:21:52 2016

@author: zhaoyong
"""

import os
import time
import numpy as np
import pandas as pd
from datetime import datetime

###--------------------------------------------------------------------------
def conver_data(filename):
    df_day = pd.read_csv('../../ts_data/day/'+filename+'.DAY.csv',index_col=0)
    df_day['date'] = df_day.index.to_datetime().date
    df_hist = pd.read_csv('../../ts_data/1min/'+filename+'.1MIN.csv',index_col=0)
    df_hist['datetime'] = df_hist.index.to_datetime()

    ###--------------------------------------------------------------------------
    """find last price"""
    # TODO:用dataframe会不会太慢
    Lclose = np.zeros(len(df_hist))
    Lopen = np.zeros(len(df_hist))
    Lhigh = np.zeros(len(df_hist))
    Llow = np.zeros(len(df_hist))
    start_time = time.time()
    for i, t in enumerate(df_hist['datetime']):
        # 跳过第一天
        if t.date() != df_day['date'][0]:
            tdate = df_day[df_day['date'] < t.date()]
            Lclose[i] = tdate['close'][-1]
            Lopen[i] = tdate['open'][-1]
            Lhigh[i] = tdate['high'][-1]
            Llow[i] = tdate['low'][-1]
    finish_time = time.time()
    print str(finish_time-start_time) + ' seconds.'
    ###--------------------------------------------------------------------------
    df_hist['Lclose'] = Lclose
    df_hist['Lopen'] = Lopen
    df_hist['Lhigh'] = Lhigh
    df_hist['Llow'] = Llow
    df_hist.to_csv('../../ts_data/1min/'+filename+'.1MIN_PLUS.csv')

    ###--------------------------------------------------------------------------
if __name__ == '__main__':
    from readdata import *
    conver_data('RB.SHF')








