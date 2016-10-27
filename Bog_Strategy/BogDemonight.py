# -*- coding: utf-8 -*-
"""
Created on Tue Oct 25 21:22:03 2016

@author: zhaoyong
"""

import os
import numpy as np
import scipy.io as scio
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt

###----------------------------------------------------------------------
"""加载wind数据"""

def loadwdata(filename):
    #filename = 'winddata/min60/J00.DCEmin60.csv'
    #不能有filenpath！！
    df = pd.read_csv(filename, index_col=0)
    print "加载数据完成"
    return df

###----------------------------------------------------------------------

"""策略逻辑部分"""

def runstrategy(filename,m,n):

    InitialE = 100000
    #scale = 300
    #bars = df
    bars = loadwdata(filename)
    # 仓位 Pos = 1 多头1手; Pos = 0 空仓; Pos = -1 空头一手
    Pos = np.zeros(len(bars))
    # 账户权益记录
    Account = np.zeros(len(bars))
    #交易记录
    Openorder = np.zeros(len(bars),dtype=dict)
    Closeorder = np.zeros(len(bars),dtype=dict)

    entryZscore=m
    stddays=n

    close_time = [i[11:19] == '15:00:00' for i in bars.index]
    df_close = bars[np.array(close_time)].fillna(method='backfill')
    open_time = [i[11:19] == '21:05:00' for i in bars.index]
    df_open = bars[np.array(open_time)].fillna(method='backfill')

    dailyret = df_close['close'].pct_change()
    movingstd = dailyret.rolling(n).std().shift()



    ## 观测开盘价，过高或过低

###--------------------------------------------------------------------------
# 开始循环
    for t in range(stddays*112-1, len(bars)):
        ## 判断bar为当日开盘价
        # 没有信号
        # 盈亏计算
        if Pos[t-1] == 1:
            Pos[t] = 1
            Account[t] = (bars['close'].values[t]-bars['close'].values[t-1])*Pos[t-1]
        if Pos[t-1] == -1:
            Pos[t] = -1
            Account[t] = (bars['close'].values[t]-bars['close'].values[t-1])*Pos[t-1]
        if Pos[t-1] == 0:
            Pos[t] = 0
            Account[t] = 0
        # 判断开盘
        if bars.index[t][11:19] == '21:05:00':

            Signalbuy = bars['open'][t] <= bars['low'][t-113:t-1].min()*(1-entryZscore*movingstd[t/112])

            Signalsell = bars['open'][t] >= bars['high'][t-113:t-1].max()*(1+entryZscore*movingstd[t/112])

            if Signalbuy:
                # 开仓做多，前一个Bar为前一天收盘前的最后一个bar，仓位会平掉，所以不用判断仓位
                print bars.index[t],'buy'
                Pos[t] = 1
                Openorder[t] = [{'Type': 1,'Openpos':bars['open'].values[t],'Vol':1, 'Time': bars.index[t]}]
            if Signalsell:
                print bars.index[t], 'sell'
                Pos[t] = -1
                Openorder[t] = [{'Type': -1,'Openpos':bars['open'].values[t],'Vol':1, 'Time': bars.index[t]}]
        # 判断收盘
        if bars.index[t][11:19] == '15:00:00' and Pos[t-1] != 0:
            # 以收盘价平仓
            if Pos[t-1] == 1:
                print bars.index[t],'colse'
                Pos[t] = 0
                Closeorder[t] = [{'Type': -1,'Closepos':bars['close'].values[t],'Vol':1, 'Time': bars.index[t]}]
                Account[t] = (bars['close'].values[t]-bars['close'].values[t-1])*Pos[t-1]
            if Pos[t-1] == -1:
                print bars.index[t], 'close'
                Pos[t] = 0
                Closeorder[t] = [{'Type': 1,'Closepos':bars['close'].values[t],'Vol':1, 'Time': bars.index[t]}]
                Account[t] = (bars['close'].values[t]-bars['close'].values[t-1])*Pos[t-1]
###----------------------------------------------------------------------
# 汇总账户数据
    AccountCum = Account.cumsum()
    AccountCum = AccountCum + InitialE

    Record = np.array([bars['close'].values,Pos,Account,AccountCum,Openorder,Closeorder]).T
    Accountsummny = pd.DataFrame(index = bars.index,data=Record,
                                columns=['Close','Pos','Account','AccountCum','Openorder','Closeorder'])
    print "回测结束"
    return Accountsummny
    ###-----------------------------------------------------------------------------
if __name__ == '__main__':
    from BogDemo import *
    pf, Accountsummny = runstrategy('../winddata/min60/J00.DCEmin60.csv',0.1,90)






