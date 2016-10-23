# -*- coding: utf-8 -*-
"""
Created on Sun Oct 23 01:00:29 2016

@author: zhao yong
"""

import os
import numpy as np
import scipy.io as scio
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt

###----------------------------------------------------------------------

"""加载测试数据"""
def loaddata(file):

    #file = 'IF888-2011.mat'

    data = scio.loadmat(file)
    # 只有cprice
    global IFdata
    IFdata = pd.DataFrame(data['IF888'][:,1],index=data['IF888'][:,0],columns=['Close'])
    return IFdata

###----------------------------------------------------------------------

"""加载wind数据"""

def loadwdata(filename):
    #filepath = '../winddata/J00.DCE.csv'
    #不能有filename！！
    df = pd.read_csv(filename, index_col=0)
    return df

###----------------------------------------------------------------------

"""策略逻辑部分"""

def runstrategy(filename,m,n):

    InitialE = 100000
    #scale = 300

    bars = loadwdata(filename)
    # 仓位 Pos = 1 多头1手; Pos = 0 空仓; Pos = -1 空头一手
    Pos = np.zeros(len(bars))
    # 账户权益记录
    Account = np.zeros(len(bars))
    #交易记录
    Openorder = np.zeros(len(bars),dtype=dict)
    Closeorder = np.zeros(len(bars),dtype=dict)

    # 选择短期5日均线、长期20日均线
    ShortLen = m
    LongLen = n
    ma5 = bars['CLOSE'].rolling(ShortLen).mean().values
    ma20 = bars['CLOSE'].rolling(LongLen).mean().values

    ma5[:ShortLen-1] = bars['CLOSE'].values[:ShortLen-1]
    ma20[:LongLen-1] = bars['CLOSE'].values[:LongLen-1]

###--------------------------------------------------------------------------
# 开始循环
    for t in range(LongLen-1, len(bars)):

        # 买入信号 : 5日均线上穿20日均线
        Signalbuy = ma5[t]>ma5[t-1] and ma5[t]>ma20[t] and ma5[t-1]>ma20[t-1] and ma5[t-2]<=ma20[t-2]


        # 卖出信号 : 5日均线下破20日均线
        Signalsell = ma5[t]<ma5[t-1] and ma5[t]<ma20[t] and ma5[t-1]<ma20[t-1] and ma5[t-2]>=ma20[t-2]
        # 没有信号
        # 每日盈亏计算
        if Pos[t-1] == 1:
            Pos[t] = 1
            Account[t] = (bars['CLOSE'].values[t]-bars['CLOSE'].values[t-1])*Pos[t-1]
        if Pos[t-1] == -1:
            Pos[t] = -1
            Account[t] = (bars['CLOSE'].values[t]-bars['CLOSE'].values[t-1])*Pos[t-1]
        if Pos[t-1] == 0:
            Pos[t] = 0
            Account[t] = 0

        if Signalbuy:
        # 空仓开多头1手  ## TODO:仓位改为大于1！！
            if Pos[t-1] == 0:
                Pos[t] = 1
                Openorder[t] = [{'Type': 1,'Openpos':bars['CLOSE'].values[t],'Vol':1, 'Time': bars.index[t]}]
                #continue
            # 平空头开多头1手
            if Pos[t-1] == -1:
                Pos[t] = 1
                Closeorder[t] = [{'Type': 1,'Closepos':bars['CLOSE'].values[t],'Vol':1, 'Time': bars.index[t]}]
                Openorder[t] = [{'Type': 1,'Openpos':bars['CLOSE'].values[t],'Vol':1, 'Time': bars.index[t]}]
                Account[t] = (bars['CLOSE'].values[t]-bars['CLOSE'].values[t-1])*Pos[t-1]
                #continue
        # 卖出条件
        elif Signalsell:
            # 空仓开空头1手
            if Pos[t-1] == 0:
                Pos[t] = -1
                Openorder[t] = [{'Type': -1,'Openpos':bars['CLOSE'].values[t],'Vol':1, 'Time': bars.index[t]}]
                #continue
            # 平多头开空头1手
            if Pos[t-1] == 1:
                Pos[t] = -1
                Closeorder[t] = [{'Type': -1,'Closepos':bars['CLOSE'].values[t],'Vol':1, 'Time': bars.index[t]}]
                Openorder[t] = [{'Type': -1,'Openpos':bars['CLOSE'].values[t],'Vol':1, 'Time': bars.index[t]}]
                Account[t] = (bars['CLOSE'].values[t]-bars['CLOSE'].values[t-1])*Pos[t-1]
                #continue
        # 最后一个交易日如果还有持仓，进行平仓
        elif t == len(bars)-1 and Pos[t-1] != 0:
            if Pos[t-1] == 1:
                Pos[t] = 0
                Closeorder[t] = [{'Type': -1,'Closepos':bars['CLOSE'].values[t],'Vol':1, 'Time': bars.index[t]}]
                Account[t] = (bars['CLOSE'].values[t]-bars['CLOSE'].values[t-1])*Pos[t-1]
            if Pos[t-1] == -1:
                Pos[t] = 0
                Openorder[t] = [{'Type': 1,'Closepos':bars['CLOSE'].values[t],'Vol':1, 'Time': bars.index[t]}]
                Account[t] = (bars['CLOSE'].values[t]-bars['CLOSE'].values[t-1])*Pos[t-1]

###----------------------------------------------------------------------
# 汇总账户数据
    AccountCum = Account.cumsum()
    AccountCum = AccountCum + InitialE

    Record = np.array([bars['CLOSE'].values,Pos,Account,AccountCum,Openorder,Closeorder]).T
    Accountsummny = pd.DataFrame(index = bars.index,data=Record,
                                columns=['Close','Pos','Account','AccountCum','Openorder','Closeorder'])
    return Accountsummny

###-----------------------------------------------------------------------------
if __name__ == '__main__':
    from BacktestDemo import *
    Accountsummny = runstrategy('..winddata/J00.DCE.csv',5,20)
