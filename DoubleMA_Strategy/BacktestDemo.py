# -*- coding: utf-8 -*-
"""
Created on Sun Oct 23 01:00:29 2016

@author: zhao yong
"""

import os
import time
import numpy as np
import pandas as pd
import seaborn as sns
from datetime import datetime
import matplotlib.pyplot as plt
sns.set_style('whitegrid')

################################################################################

"""加载数据并初始化策略"""

def initstrategy(filename,start=False,end=False):
    # 定义为全局变量
    global df
    df = pd.read_csv(filename, index_col=0)
    df['datetime'] = df.index.to_datetime()
    # 设置回测周期
    # 统一转换字符串为datatime
    if start:
        start = datetime.strptime(start,'%Y-%m-%d').date()
        df = df[df['datetime']>=start]
    if end:
        end = datetime.strptime(end,'%Y-%m-%d').date()
        df = df[df['datetime']<=end]

################################################################################

"""策略逻辑部分"""

def runstrategy(slip=0,tradingcost=0.3/10000,m=5,n=20):

    bars = df
    InitialE = bars['close'][0]
    # 仓位 Pos = 1 多头1手; Pos = 0 空仓; Pos = -1 空头一手
    Pos = np.zeros(len(bars))
    # 账户权益记录
    Account = np.zeros(len(bars))
    #交易记录
    Openorder = np.zeros(len(bars),dtype=dict)
    Closeorder = np.zeros(len(bars),dtype=dict)

    # orderlist缓存
    buffsize = 300
    orderprice = np.zeros(buffsize)

    # 选择短期5日均线、长期20日均线
    ShortLen = m
    LongLen = n
    ma5 = bars['close'].rolling(ShortLen).mean().values
    ma20 = bars['close'].rolling(LongLen).mean().values

    ma5[:ShortLen-1] = bars['close'].values[:ShortLen-1]
    ma20[:LongLen-1] = bars['close'].values[:LongLen-1]

    highp = bars['high'].values
    lowp = bars['low'].values
    openp = bars['open'].values
    closep = bars['close'].values

###--------------------------------------------------------------------------
# 开始循环
    for t, bar in enumerate(bars['datetime']):
        # 跳过前几天
        if t >= LongLen-1:
            # 买入信号 : 5日均线上穿20日均线
            Signalbuy = ma5[t]>ma5[t-1] and ma5[t]>ma20[t] and ma5[t-1]<=ma20[t-1]
            # 卖出信号 : 5日均线下破20日均线
            Signalsell = ma5[t]<ma5[t-1] and ma5[t]<ma20[t] and ma5[t-1]>=ma20[t-1]
            # 没有信号
            # 每日盈亏计算
            if Pos[t-1] == 1:
                Pos[t] = 1
                Account[t] = (closep[t]-closep[t-1])*Pos[t-1]
            if Pos[t-1] == -1:
                Pos[t] = -1
                Account[t] = (closep[t]-closep[t-1])*Pos[t-1]
            if Pos[t-1] == 0:
                Pos[t] = 0
                Account[t] = 0

            if Signalbuy:
            # 空仓开多头1手  ## TODO:仓位改为大于1！！
                if Pos[t-1] == 0:
                    Pos[t] = 1
                    Openorder[t] = {'Type': 1,'Openpos':closep[t],'Vol':1, 'Time': bar}

                # 平空头开多头1手
                if Pos[t-1] == -1:
                    Pos[t] = 1
                    Closeorder[t] = {'Type': 1,'Closepos':closep[t],'Vol':1, 'Time': bar}
                    Openorder[t] = {'Type': 1,'Openpos':closep[t],'Vol':1, 'Time': bar}
                    Account[t] = (closep[t]-closep[t-1])*Pos[t-1]

            # 卖出条件
            if Signalsell:
                # 空仓开空头1手
                if Pos[t-1] == 0:
                    Pos[t] = -1
                    Openorder[t] = {'Type': -1,'Openpos':closep[t],'Vol':1, 'Time': bar}

                # 平多头开空头1手
                if Pos[t-1] == 1:
                    Pos[t] = -1
                    Closeorder[t] = {'Type': -1,'Closepos':closep[t],'Vol':1, 'Time': bar}
                    Openorder[t] = {'Type': -1,'Openpos':closep[t],'Vol':1, 'Time': bar}
                    Account[t] = (closep[t]-closep[t-1])*Pos[t-1]

            # 最后一个交易日如果还有持仓，进行平仓
            if t == len(bars)-1 and Pos[t-1] != 0:
                if Pos[t-1] == 1:
                    Pos[t] = 0
                    Closeorder[t] = {'Type': -1,'Closepos':closep[t],'Vol':1, 'Time': bar}
                    Account[t] = (closep[t]-closep[t-1])*Pos[t-1]
                if Pos[t-1] == -1:
                    Pos[t] = 0
                    Closeorder[t] = {'Type': 1,'Closepos':closep[t],'Vol':1, 'Time': bar}
                    Account[t] = (closep[t]-closep[t-1])*Pos[t-1]

###----------------------------------------------------------------------
# 汇总账户数据
    AccountCum = Account.cumsum()
    AccountCum = AccountCum + InitialE

    Record = np.array([bars['close'].values,Pos,Account,AccountCum,Openorder,Closeorder]).T
    Accountsummny = pd.DataFrame(index = bars.index,data=Record,
                                columns=['Close','Pos','Account','AccountCum','Openorder','Closeorder'])
    print "回测结束"
    return Accountsummny

################################################################################
if __name__ == '__main__':
    from BacktestDemo import *
    initstrategy('../../ts_data/day/RB.SHF.DAY.csv')
    Accountsummny = runstrategy()
