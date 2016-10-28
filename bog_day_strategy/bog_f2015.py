# -*- coding: utf-8 -*-
"""
Created on Wed Oct 26 16:05:58 2016

@author: zhao yong
"""

import os
import numpy as np
import scipy.io as scio
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_style('whitegrid')



###--------------------------------------------------------------------------
# 读取数据
def runstrategy(filename,m,n):

    #df = pd.read_csv('../ts_data/J00.DCE.csv',index_col=0)
    df = pd.read_csv(filename,index_col=0)
    df = df[df.index >= '2015/10/20']
#------------------------------------------------------------------------------
    InitialE = df['close'][0]
    #scale = 300
    bars = df
    #bars = loadwdata(filename)
    # 仓位 Pos = 1 多头1手; Pos = 0 空仓; Pos = -1 空头一手
    Pos = np.zeros(len(bars))
    # 账户权益记录
    Account = np.zeros(len(bars))
    #交易记录
    Openorder = np.zeros(len(bars),dtype=dict)
    Closeorder = np.zeros(len(bars),dtype=dict)

    entryZscore = m
    stddays = n

    dailyret = df['close'].pct_change()
    movingstd = dailyret.rolling(stddays).std().shift()

    ## 观测开盘价，过高或过低
    ###--------------------------------------------------------------------------
    # 开始循环
    ##起始点可以设为n的后天。
    for t in range(len(bars)):
        # 条件判断
        shorts = df['open'][t] <= df['low'][t-1]*(1-entryZscore*movingstd[t])
        longs = df['open'][t] >= df['high'][t-1]*(1+entryZscore*movingstd[t])
        # 如果没有信号，当天不开仓，权益不会发生变化
        if longs:
            #print bars.index[t],'buy'
            Pos[t] = 1
            Openorder[t] = {'Type': 1,'Openpos':bars['dayopen'].values[t],'Vol':1, 'Time': bars.index[t]}
            Closeorder[t] = {'Type': -1,'Closepos':bars['close'].values[t],'Vol':1, 'Time': bars.index[t]}
            Account[t] = (bars['close'].values[t]-bars['dayopen'].values[t])*Pos[t]
        if  shorts:
            #print bars.index[t], 'sell'
            Pos[t] = -1
            Openorder[t] = {'Type': -1,'Openpos':bars['dayopen'].values[t],'Vol':1, 'Time': bars.index[t]}
            Closeorder[t] = {'Type': 1,'Closepos':bars['close'].values[t],'Vol':1, 'Time': bars.index[t]}
            Account[t] = (bars['close'].values[t]-bars['dayopen'].values[t])*Pos[t]
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
    from bog_f2015 import *
    pf, Accountsummny = runstrategy('../ts_data/M00.DCE.addopen.csv',0.1,90)




