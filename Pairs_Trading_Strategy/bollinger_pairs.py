# -*- coding: utf-8 -*-
"""
Created on Tue Oct 25 13:26:24 2016

@author: zhaoyong
"""


import os
import numpy as np
import scipy.io as scio
import pandas as pd
from datetime import datetime

import statsmodels.api as sm
from statsmodels.tsa.stattools import coint
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_style('whitegrid')


##-----------------------------------------------------------------------------
"""加载测试数据"""
def loaddfdata(symname):
    filename = 'inputData_ETF'
    data = scio.loadmat(filename)

    idx = data['syms'][0] == symname
    p = idx.tolist().index(True)
    temp = data['tday'].astype(int).astype(str)   # 转str
    tday = np.array([i[0] for i in temp])
    cl = data['cl'][:,p]
    op = data['op'][:,p]
    hi = data['hi'][:,p]
    lo = data['lo'][:,p]
    ## 数据打包
    df = pd.DataFrame(index=tday, data=np.array([cl,op,hi,lo]).T,
                    columns=['CLOSE','OPEN','HIGH','LOW'])
    return df

###------------------------------------------------------------------------------

"""加载wind数据"""
def loadwdata(file):
    df = pd.read_csv(file, index_col=0)
    return df

###----------------------------------------------------------------------

"""开始回测"""
def runstrategy(window,filenameA,filenameB):
    #filename = 'inputData_ETF'

    #dfA = loaddfdata(u'GLD')
    #dfB = loaddfdata(u'USO')
    dfA = loadwdata(filenameA)
    dfB = loadwdata(filenameB)
    x = dfA['CLOSE']
    y = dfB['CLOSE']

    ## 滚动回归
    window = 30
    beta = np.zeros(len(x)-window)
    for t in range(1,len(x)-window+1):
        x = sm.add_constant(x)
        results = sm.OLS(y[t:t+window], x[t:t+window]).fit()
        x = x['CLOSE']
        b = results.params['CLOSE']
        beta[t-1] = b
    rolling_beta = pd.Series(beta,index=x[window:].index)

    yport = y-x*rolling_beta
    yport = yport.dropna()   ## 空缺值填0
    y2 = np.array([x,y]).T


    # 回归到0出场，非最优
    entryZscore = 1.0
    exitZscore = 0.0  # exitZscore is -1 better!
    MA10 = yport.rolling(10).mean()
    MA30 = yport.rolling(window).mean()
    MSTD = yport.rolling(window).std()

    zScore=(MA10-MA30)/MSTD ### TODO:可以改为双均线的zscore

    longsEntry = zScore <= -entryZscore  # a long position means we should buy EWC
    longsExit = zScore >= -exitZscore

    shortsEntry = zScore >= entryZscore
    shortsExit = zScore <= exitZscore


    poslongs = np.ones(len(yport))*100   ## TODO:需要想出一个办法，matlab可以用nan
    posshorts = np.ones(len(yport))*100
    # 初始仓位为0
    poslongs[0] = 0
    posshorts[0] = 0
    poslongs[longsEntry.values] = 1
    poslongs[longsExit.values] = 0 ## 出场时间不一样，仓位不一样
    posshorts[shortsEntry.values] = -1
    posshorts[shortsExit.values] = 0

    ## 思路是如果没有出场信号，那么仓位跟上一个入场保持一致。
    for i in range(1,len(poslongs)):
        if poslongs[i] >= 10:
            poslongs[i] = poslongs[i-1]

    for i in range(1,len(posshorts)):
        if posshorts[i] >= 10:
            posshorts[i] = posshorts[i-1]

    pos = poslongs+posshorts
    two_pos = pd.DataFrame(data=np.array([pos,pos]).T,
                           index=rolling_beta.index,columns=['x','y'])
    #positions=repmat(numUnits, [1 size(y2, 2)]).*[-hedgeRatio ones(size(hedgeRatio))].*y2
    two_asset = pd.concat([-rolling_beta*x[window:],-y[window:]],axis=1)
    positions = two_asset.values*two_pos

    two_prices = pd.DataFrame(data=y2[window:,:],index=rolling_beta.index,columns=['x','y'])
    two_ret = two_prices.pct_change()
    two_ret = two_ret.fillna(0)
    two_money = positions.shift(1)*two_ret
    pnl = two_money.sum(axis=1)


    ret = pnl/(positions.shift(1).abs().sum(axis=1))
    ret = ret.fillna(0)

    #cumret = (1+ret).cumprod()-1
    closeprice = x+y
    return ret, closeprice[window:]

###----------------------------------------------------------------------

if __name__ == '__main__':
    from bollinger_pairs import *
    ret, price = runstrategy(20,'../winddata/P00.DCE.csv',
                                '../winddata/SR00.CZC.csv')
