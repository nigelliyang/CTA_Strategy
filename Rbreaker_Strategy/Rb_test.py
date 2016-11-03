# -*- coding: utf-8 -*-
"""
Created on Wed Nov 02 15:44:05 2016

@author: zhaoyong
"""

import os
import numpy as np
import pandas as pd
import time
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_style('whitegrid')

###--------------------------------------------------------------------------
# 读取数据
def runstrategy(filename,start=False,end=False,tradingcost = 0.0,m=0.35,n=0.07,l=0.25):
    # 回测开始
    start_time = time.time()
    #filename = '../../ts_data/1min/RB.SHF.1MIN_PLUS.csv'
    df = pd.read_csv(filename,index_col=0)
    df['datetime'] = df.index.to_datetime()
    # 设置回测周期
    # 统一转换字符串为datatime
    if start:
        start = datetime.strptime(start,'%Y-%m-%d').date()
        df = df[df['datetime']>=start]
    if end:
        end = datetime.strptime(end,'%Y-%m-%d').date()
        df = df[df['datetime']<=end]

    # 交易时间设置
    StartTime = datetime.strptime('9:35',"%H:%M").time()
    noontime = datetime.strptime('14:00',"%H:%M").time()
    ExTime = datetime.strptime('14:45',"%H:%M").time()
    # 直接在这里把夜盘时间排除
    bars = df[[StartTime <= i.time() <= ExTime for i in df['datetime']]]


    # 以首日开盘价为初始资金
    InitialE = bars['close'][0]
    # 考虑手续费
    # tradingcost = 0.0
    # 仓位 Pos = 1 多头1手; Pos = 0 空仓; Pos = -1 空头一手
    Pos = np.zeros(len(bars))
    # 账户权益记录
    Account = np.zeros(len(bars))
    # 交易记录
    Openorder = np.zeros(len(bars),dtype=dict)
    Closeorder = np.zeros(len(bars),dtype=dict)


    Lhigh = bars['Lhigh'].values
    Lclose = bars['Lclose'].values
    Llow = bars['Llow'].values
    # 参数设置
    f1 = m
    f2 = n
    f3 = l
    """
    观察卖出价,观察买入价,反转卖出价
    反转买入价,突破买入价,突破卖出价
    """
    views = Lhigh + f1 * (Lclose - Llow)
    viewb = Llow - f1 * (Lhigh - Lclose)
    reves = (1+f2) * (Lhigh + Llow)/2 - f2 * Llow
    reveb = (1+f2) * (Lhigh + Llow)/2 - f2 * Lhigh
    breab = views + f3 * (views - viewb)
    breas = viewb - f3 * (views - viewb)

    highp = bars['high'].values
    lowp = bars['low'].values
    openp = bars['open'].values
    closep = bars['close'].values
    bid1 = bars['bid1'].values
    ask1 = bars['ask1'].values

    ###-------------------------------------------------------------------------
    # 开始循环
    for t, bar in enumerate(bars['datetime']):
        """跳过第一天，并且在交易时间内交易"""
        firstday = bars['datetime'][0].date()
        if bar.date() > firstday:
            if StartTime <= bar.time() < ExTime:
                """计算当日内最高价，最低价"""
                if bar.time() == StartTime:
                    todayhigh = highp[t]
                    todaylow = lowp[t]
                if bar.time() > StartTime:
                    todayhigh = max(highp[t],todayhigh)
                    todaylow = min(lowp[t],todaylow)
                ###-----------------------------------------------------------------
                """没有信号"""
                # 每日盈亏计算
                if Pos[t-1] == 1:
                    Pos[t] = 1
                    Account[t] = (closep[t]-closep[t-1])*Pos[t]
                if Pos[t-1] == -1:
                    Pos[t] = -1
                    Account[t] = (closep[t]-closep[t-1])*Pos[t]
                if Pos[t-1] == 0:
                    Pos[t] = 0
                    Account[t] = 0
                ###-----------------------------------------------------------------
                """开仓"""
                """
                1) 当日内最高价超过观察卖出价后,盘中价格出现回落,
                且进一步跌破反转卖出价构成的支撑线时,采取反转策略,即在该点位(反手、开仓)做空;
                2) 当日内最低价低于观察买入价后,盘中价格出现反弹,
                且进一步超过反转买入价构成的阻力线时,采取反转策略,即在该点位(反手、开仓)做多;
                3) 在空仓的情况下,如果盘中价格超过突破买入价,则采取趋势策略,即在该点位开仓做多;
                4) 在空仓的情况下,如果盘中价格跌破突破卖出价,则采取趋势策略,即在该点位开仓做空。
                """
                ### TODO:盘中价格指的是什么？这里理解成的是每个bar的收盘价。
                # 防止反复开仓
                flag1 = 0
                #flag2 = 0
                revershorts = todayhigh >= views[t] and lowp[t] <= reves[t]-30 and bar.time() <= noontime
                if revershorts and bid1[t] != 0:
                    ## 先平多，再做空
                    if Pos[t-1] == 1:
                        Pos[t] = -1
                        entryprice = bid1[t]
                        Closeorder[t] = {'Type':-1,'Closepos':entryprice,'Vol':1,'Time':bar}
                        Openorder[t] = {'Type':-1,'Openpos':entryprice,'Vol':1,'Time':bar}
                        Account[t] = (closep[t]-entryprice)*Pos[t]-entryprice*(Openorder[t]['Vol']+Closeorder[t]['Vol'])*tradingcost
                        #flag1 = 1
                    ## 开仓做空
                    if Pos[t-1] == 0 and flag1 == 0:
                        Pos[t] = -1
                        entryprice = bid1[t]
                        Openorder[t] = {'Type':-1,'Openpos':entryprice,'Vol':1,'Time':bar}
                        Account[t] = (closep[t]-entryprice)*Pos[t]-entryprice*Openorder[t]['Vol']*tradingcost
                        flag1 = 1

                reverlongs = todaylow >= viewb[t] and highp[t] >= reveb[t]+30 and bar.time() <= noontime
                if reverlongs and ask1[t] != 0:
                    ## 先平空，再做多
                    if Pos[t-1] == -1:
                        Pos[t] = 1
                        entryprice = ask1[t]
                        Closeorder[t] = {'Type': 1,'Closepos':entryprice,'Vol':1,'Time': bar}
                        Openorder[t] = {'Type': 1,'Openpos':entryprice,'Vol':1,'Time': bar}
                        Account[t] = (closep[t]-entryprice)*Pos[t]-entryprice*(Openorder[t]['Vol']+Closeorder[t]['Vol'])*tradingcost
                        #flag1 = 1
                    ## 开仓做多
                    if Pos[t-1] == 0 and flag1 == 0:
                        Pos[t] = 1
                        entryprice = ask1[t]
                        Openorder[t] = {'Type': 1,'Openpos':entryprice,'Vol':1,'Time': bar}
                        Account[t] = (closep[t]-entryprice)*Pos[t]-entryprice*Openorder[t]['Vol']*tradingcost
                        flag1 = 1
                if Pos[t-1] == 0:
                    longs = highp[t] >= breab[t] and bar.time() <= noontime
                    ## 空仓做多
                    if longs and ask1[t] != 0 and flag1 == 0:
                        Pos[t] = 1
                        entryprice = ask1[t]
                        Openorder[t] = {'Type': 1,'Openpos':entryprice,'Vol':1,'Time': bar}
                        Account[t] = (closep[t]-entryprice)*Pos[t]-entryprice*Openorder[t]['Vol']*tradingcost
                        flag1 = 1
                    ## 空仓做空
                    shorts = lowp[t] <= breas[t] and bar.time() <= noontime
                    if shorts and bid1[t] != 0 and flag1 == 0:
                        Pos[t] = -1
                        entryprice = bid1[t]
                        Openorder[t] = {'Type': -1,'Openpos':entryprice,'Vol':1,'Time': bar}
                        Account[t] = (closep[t]-entryprice)*Pos[t]-entryprice*Openorder[t]['Vol']*tradingcost
                        flag1 = 1
            if bar.time() == ExTime:
                ## 收盘平仓
                if Pos[t-1] == 1:
                    Pos[t] = 0
                    entryprice = openp[t]
                    Closeorder[t] = {'Type': -1,'Closepos':entryprice,'Vol':1,'Time': bar}
                    Account[t] = -entryprice*Closeorder[t]['Vol']*tradingcost
                    # 收盘没有仓位！
                    #Account[t] = (bar['close']-entryprice)*Pos[t]
                if Pos[t-1] == -1:
                    Pos[t] = 0
                    entryprice = openp[t]
                    Closeorder[t] = {'Type': 1,'Closepos':entryprice,'Vol':1,'Time': bar}
                    Account[t] = -entryprice*Closeorder[t]['Vol']*tradingcost
                ## 未设止盈止损

    ###----------------------------------------------------------------------
    # 汇总账户数据
    AccountCum = Account.cumsum()
    AccountCum = AccountCum + InitialE

    Record = np.array([bars['close'].values,Pos,Account,AccountCum,Openorder,Closeorder]).T
    Accountsummny = pd.DataFrame(index = bars.index,data=Record,
                                    columns=['Close','Pos','Account','AccountCum','Openorder','Closeorder'])

    #print "回测结束"
    finish_time = time.time()
    print u'回测结束，共用时：' + str(finish_time-start_time) + ' seconds.'
    return Accountsummny

###-----------------------------------------------------------------------------

if __name__ == '__main__':
    from Rb_test import *
    Accountsummny = runstrategy('../../ts_data/1min/RB.SHF.1MIN_PLUS.csv')
