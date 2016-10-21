# -*- coding: utf-8 -*-
"""
Created on Wed Oct 19 19:45:01 2016

@author: zhao yong
"""

import numpy as np
import scipy.io as scio
import pandas as pd
from scipy.stats import pearsonr
from ts_backtest import *


### 先加载数据
#tday, cl, clseries = loaddata('inputDataOHLCDaily_20120511.mat')
### wind data
tday, cl, clseries = loadwdata('winddata/rb00.csv')
lookback=[1, 5, 10, 25, 60, 120, 250]
holddays=[1, 5, 10, 25, 60, 120, 250]

###-----------------------------------------------------------------------------

"""相关性检验，输出pearsonr相关系数及p值"""
def t_test(lookback, holddays):
    r_P = []
    for i in lookback:
        for j in holddays:
            ret_lag = clseries.pct_change(i)
            ret_fut = clseries.pct_change(j).shift(-j)
            ret_all = pd.concat([ret_lag, ret_fut], axis=1).dropna()

            if (i >= j):
                indepSet = np.arange(1,len(ret_all),j)
            else:
                indepSet = np.arange(1,len(ret_all),i)
            ret_data = ret_all.iloc[indepSet,:]
            r,p=pearsonr(ret_data.iloc[:,0].values, ret_data.iloc[:,1].values)
            #print i, j, r, p
            r_P.append([i,j,r,p])
    df = pd.DataFrame(r_P, columns=['Lookback', 'Holddays',
                                    'Correlation coefficient','p-value'])
    return df
df = t_test(lookback, holddays)
## 转为csv后，可以在表格里“条件格式-色阶”
#df.to_csv('t_test.csv')

###-----------------------------------------------------------------------------

"""Hurst exponent"""
def hurst(ts):
    """Returns the Hurst Exponent of the time series vector ts"""
    # Create the range of lag values
    lags = range(2, 100)
    # Calculate the array of the variances of the lagged differences
    tau = [np.sqrt(np.std(np.subtract(ts[lag:], ts[:-lag]))) for lag in lags]
    # Use a linear fit to estimate the Hurst Exponent
    poly = np.polyfit(np.log(lags), np.log(tau), 1)
    # Return the Hurst exponent from the polyfit output
    return poly[0]*2.0
h = hurst(np.log(cl))

#h=1 means rejection of random walk hypothesis, 0 means it is a random walk

## TODO:  Variance ratio test

