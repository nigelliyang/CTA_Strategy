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
def runstrategy(filename,start=False,end=False,m=0.35,n=0.07,l=0.25):
    # 回测开始
    start_time = time.time()
    #df = pd.read_csv('../ts_data/J00.DCE.csv',index_col=0)
    df = pd.read_csv(filename,index_col=0)
    # 设置回测周期
    # 统一转换字符串为datatime
    if start:
        start = datetime.strptime(start,'%Y-%m-%d').date()
    if end:
        end = datetime.strptime(end,'%Y-%m-%d').date()
    df['datetime'] = df['datetime'].to_datetime()
    bars = df[(df['datetime']>=start) & (df['datetime']<=end)]

    # 以首日开盘价为初始资金
    InitialE = bars['close'][0]
    # 仓位 Pos = 1 多头1手; Pos = 0 空仓; Pos = -1 空头一手
    Pos = np.zeros(len(bars))
    # 账户权益记录
    Account = np.zeros(len(bars))
    # 交易记录
    Openorder = np.zeros(len(bars),dtype=dict)
    Closeorder = np.zeros(len(bars),dtype=dict)
    # 交易时间设置
    StartTime = datetime.strptime('9:05',"%H:%M").time()
    ExTime = datetime.strptime('14:55',"%H:%M").time()
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

    ###-------------------------------------------------------------------------
    # 开始循环
    for t, bar in enumerate(bars):
        """跳过第一天，并且在交易时间内交易"""
        if bar['datetime'].date() > start:
            if StartTime <= bar['datetime'].time() < ExTime:
                """计算当日内最高价，最低价"""
                if bar['datetime'].time() == StartTime:
                    todayhigh = bar['high']
                    todaylow = bar['low']
                else:
                    todayhigh = max(bars['high'].values[t],bars['high'].values[t-1])
                    todaylow = min(bars['low'].values[t],bars['low'].values[t-1])
                ###-----------------------------------------------------------------
                """没有信号"""
                # 每日盈亏计算
                if Pos[t-1] == 1:
                    Pos[t] = 1
                    Account[t] = (bars['close'].values[t]-bars['close'].values[t-1])*Pos[t-1]
                if Pos[t-1] == -1:
                    Pos[t] = -1
                    Account[t] = (bars['close'].values[t]-bars['close'].values[t-1])*Pos[t-1]
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
                # 先判断平仓，后判断开仓，以防止信号闪烁
                # 防止反复开仓
                flag1 = 0
                flag2 = 0

                revershorts = todayhigh >= views and bars['low'][t] < reves
                if revershorts:
                    ## 开仓做空
                    if Pos[t-1] == 0 and flag1 == 0:
                        Pos[t] = -1
                        entryprice = bar['bid1']
                        Openorder[t] = dict('Type': -1,
                                            'Openpos':entryprice,
                                            'Vol':1,
                                            'Time': bar.index)
                        Account[t] = (bar['close']-entryprice)*Pos[t]
                        flag1 = 1
                    ## 先平多，再做空
                    if Pos[t-1] == 1 and flag1 == 0:
                        Pos[t] ＝ -1
                        entryprice = bar['bid1']
                        Closeorder[t] = dict('Type': -1,
                                            'Closepos':entryprice,
                                            'Vol':1,
                                            'Time': bar.index)
                        Openorder[t] = dict('Type': -1,
                                            'Openpos':entryprice,
                                            'Vol':1,
                                            'Time': bar.index)
                        Account[t] = (bar['close']-entryprice)*Pos[t]
                        flag1 = 1
                reverlongs = todaylow >= viewb and bars['high'][t] > reveb
                if reverlongs:
                    ## 开仓做多
                    if Pos[t-1] == 0 and flag1 == 0:
                        Pos[t] = 1
                        entryprice = bar['ask1']
                        Openorder[t] = dict('Type': 1,
                                            'Openpos':entryprice,
                                            'Vol':1,
                                            'Time': bar.index)
                        Account[t] = (bar['close']-entryprice)*Pos[t]
                        flag1 = 1
                    ## 先平空，再做多
                    if Pos[t-1] == -1 and flag1 == 0:
                        Pos[t] = 1
                        entryprice = bar['ask1']
                        Closeorder[t] = dict('Type': 1,
                                            'Closepos':entryprice,
                                            'Vol':1,
                                            'Time': bar.index)
                        Openorder[t] = dict('Type': 1,
                                            'Openpos':entryprice,
                                            'Vol':1,
                                            'Time': bar.index)
                        Account[t] = (bar['close']-entryprice)*Pos[t]
                        flag1 = 1
                if Pos[t-1] == 0 and flag1 == 0 and flag2 == 0:
                    longs = bar['high'] >= breab
                    ## 空仓做多
                    if longs:
                        Pos[t] = 1
                        entryprice = bar['ask1']
                        Openorder[t] = dict('Type': 1,
                                            'Openpos':entryprice,
                                            'Vol':1,
                                            'Time': bar.index)
                        Account[t] = (bar['close']-entryprice)*Pos[t]
                        flag2 = 1
                    ## 空仓做空
                    shorts = bar['low'] <= breas
                    if shorts:
                        Pos[t] = -1
                        entryprice = bar['bid1']
                        Openorder[t] = dict('Type': -1,
                                            'Openpos':entryprice,
                                            'Vol':1,
                                            'Time': bar.index)
                        Account[t] = (bar['close']-entryprice)*Pos[t]
                        flag2 = 1
            if bar['datetime'].time() == ExTime:
                ## 收盘平仓
                if Pos[t-1] == 1:
                    Pos[t] = 0
                    entryprice = bar['bid1']
                    Openorder[t] = dict('Type': -1,
                                        'Openpos':entryprice,
                                        'Vol':1,
                                        'Time': bar.index)
                    # 收盘没有仓位！
                    #Account[t] = (bar['close']-entryprice)*Pos[t]
                if Pos[t-1] == -1:
                    Pos[t] = 0
                    entryprice = bar['ask1']
                    Openorder[t] = dict('Type': 1,
                                        'Openpos':entryprice,
                                        'Vol':1,
                                        'Time': bar.index)
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
    Accountsummny = runstrategy('../../ts_data/1min/RB.SHF.1MIN_PLUS.csv',0.35, 0.07, 0.25)
