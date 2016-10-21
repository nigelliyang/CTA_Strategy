# -*- coding: utf-8 -*-
"""
Created on Wed Oct 19 09:05:32 2016

@author: zhao yong
"""
import numpy as np
import scipy.io as scio
import pandas as pd
#%matplotlib inline
import matplotlib.pyplot as plt


dataFile = 'inputDataOHLCDaily_20120511.mat'
data = scio.loadmat(dataFile)
temp = data['syms'][0]==u'TU'
p = temp.tolist().index(True)
tday = data['tday'][:,p].astype(int)   # 转int
cl = data['cl'][:,p]
## tday, cl 转为series
clseries = pd.Series(index=tday, data=cl)

lookback=250;
holddays=25;
## 过去250天收益为正，做多；为负，做空
longs_log = clseries > clseries.shift(lookback)
shorts_log = clseries < clseries.shift(lookback)
## logical转int
longs = longs_log.astype(int)
shorts = shorts_log.astype(int)

pos = np.zeros(len(cl), dtype=np.int)

for h in range(holddays):
    long_lag = longs.shift(h)
    long_lag[np.isnan(long_lag)] = False
    long_lag = long_lag.astype(bool)

    short_lag = shorts.shift(h)
    short_lag[np.isnan(short_lag)] = False
    short_lag = short_lag.astype(bool)

    pos[long_lag.values] = pos[long_lag.values] + 1
    pos[short_lag.values] = pos[short_lag.values] - 1

position = pd.Series(index=tday, data=pos,dtype=int)
ret = position.shift(1)*clseries.pct_change()/holddays
ret = ret.fillna(0)

cumret = (1+ret).cumprod()

## TODO 精细化画图（时间序列显示）
plt.plot(cumret.values)