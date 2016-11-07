# -*- coding: utf-8 -*-
"""
Created on Mon Nov 07 11:28:08 2016

@author: zhaoyong
"""

import os
import numpy as np
import pandas as pd
import time
from datetime import datetime
import winsound
from WindPy import w
w.start()

"""先读取昨日数据"""
ldata = w.wsd("RU1701.SHF", "open,high,low,close,volume,amt", "2016-11-04", "2016-11-04", "")
fm=pd.DataFrame(ldata.Data,index=ldata.Fields,columns=ldata.Times)
fm=fm.T

Lhigh = fm['HIGH'].values[0]
Lclose = fm['CLOSE'].values[0]
Llow = fm['LOW'].values[0]
Lopen = fm['OPEN'].values[0]

# 参数设置
f1 = 0.35
f2 = 0.07
f3 = 0.25
stoploss = 0.005  # 止损参数
div = 3   # 反转参数
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

#------------------------------------------------------------------------------

# 价格序列
lastprice = []
# 初始化仓位
Pos = [0]
# 交易记录
Openorder = []
Closeorder = []

# 交易时间设置
StartTime = datetime.strptime('9:35',"%H:%M").time()
noontime = datetime.strptime('14:00',"%H:%M").time()
ExTime = datetime.strptime('14:45',"%H:%M").time()
flag2 = 0
#------------------------------------------------------------------------------
"""开始循环"""
def runstrategy():
    """设定波幅过滤"""
    shouldopen = abs(float(Lopen - Lclose)/Lopen) > 0.0001
    """读取行情数据"""
    wdata = w.wsq("RU1701.SHF",
    "rt_date,rt_time,rt_open,rt_high,rt_low,rt_last,rt_last_amt,rt_last_vol,rt_latest,rt_vol,rt_amt,rt_bid1,rt_ask1")
    bar = pd.DataFrame(wdata.Data,index=wdata.Fields,columns=wdata.Times)
    bar = bar.T
    if StartTime <= bar.index[0].time() < ExTime and shouldopen:
        lastprice.append(bar['RT_LAST'].values[0])   # 存行情数据
        todayhigh = max(lastprice)
        todaylow = min(lastprice)
        # 防止反复开仓
        flag1 = 0
        global flag2
        revershorts = todayhigh > views and bar['RT_LAST'].values[0] < reves+(todayhigh-views)/3
        if revershorts and bar['RT_BID1'].values[0] != 0 and bar.index[0].time() <= noontime and flag2 == 0:
            ## 先平多，再做空
            if Pos[-1] == 1:
                Pos.append(-1)
                entryprice = bar['RT_BID1'].values[0]
                Closeorder.append({'Type':-1,'Closepos':entryprice,'Vol':1,'Time':bar.index[0].time()})
                Openorder.append({'Type':-1,'Openpos':entryprice,'Vol':1,'Time':bar.index[0].time()})
                print ("Closeorder:" , Closeorder[-1])
                print ("Openorder:" , Openorder[-1])
                winsound.PlaySound('SystemHand', winsound.SND_ASYNC)
            ## 开仓做空
            if Pos[-1] == 0 and flag1 == 0:
                Pos.append(-1)
                #entryprice = min(openp[t],reves[t]+(todayhigh-views[t])/3)
                entryprice = bar['RT_BID1'].values[0]
                Openorder.append({'Type':-1,'Openpos':entryprice,'Vol':1,'Time':bar.index[0].time()})
                print ("Openorder:" , Openorder[-1])
                winsound.PlaySound('SystemHand', winsound.SND_ASYNC)
                flag1 = 1
        reverlongs = todaylow < viewb and bar['RT_LAST'].values[0] > reveb-(viewb-todaylow)/3
        if reverlongs and bar['RT_ASK1'].values[0] != 0 and bar.index[0].time() <= noontime and flag2 == 0:
            ## 先平空，再做多
            if Pos[-1] == -1:
                Pos.append(1)
                #entryprice = max(openp[t],reveb[t]-(viewb[t]-todaylow)/3)
                entryprice = bar['RT_ASK1'].values[0]
                Closeorder.append({'Type': 1,'Closepos':entryprice,'Vol':1,'Time': bar.index[0].time()})
                Openorder.append({'Type': 1,'Openpos':entryprice,'Vol':1,'Time': bar.index[0].time()})
                print ("Closeorder:" , Closeorder[-1])
                print ("Openorder:" , Openorder[-1])
                winsound.PlaySound('SystemHand', winsound.SND_ASYNC)
            ## 开仓做多
            if Pos[-1] == 0 and flag1 == 0:
                Pos.append(1)
                #entryprice = max(openp[t],reveb[t]-(viewb[t]-todaylow)/3)
                entryprice = bar['RT_ASK1'].values[0]
                Openorder.append({'Type': 1,'Openpos':entryprice,'Vol':1,'Time': bar.index[0].time()})
                print ("Openorder:" , Openorder[-1])
                winsound.PlaySound('SystemHand', winsound.SND_ASYNC)
                flag1 = 1
        if Pos[-1] == 0:
            longs = bar['RT_LAST'].values[0] > breab and bar.index[0].time() <= noontime and flag2 == 0
            ## 空仓做多
            if longs and bar['RT_ASK1'].values[0] != 0 and flag1 == 0:
                Pos.append(1)
                #entryprice = max(openp[t],breab[t])
                entryprice = bar['RT_ASK1'].values[0]
                Openorder.append({'Type': 1,'Openpos':entryprice,'Vol':1,'Time': bar.index[0].time()})
                print ("Openorder:" , Openorder[-1])
                winsound.PlaySound('SystemHand', winsound.SND_ASYNC)
                flag1 = 1
            ## 空仓做空
            shorts = bar['RT_LAST'].values[0] < breas and bar.index[0].time() <= noontime and flag2 == 0
            if shorts and bar['RT_BID1'].values[0] != 0 and flag1 == 0:
                Pos.append(-1)
                #entryprice = min(openp[t],breas[t])
                entryprice = bar['RT_BID1'].values[0]
                Openorder.append({'Type': -1,'Openpos':entryprice,'Vol':1,'Time': bar.index[0].time()})
                print ("Openorder:" , Openorder[-1])
                winsound.PlaySound('SystemHand', winsound.SND_ASYNC)
                flag1 = 1
        # 止损平仓
        if Pos[-1] == 1:
        #openposprice = Openorder[:t][Openorder[:t] != 0][-1]['Openpos']
            if bar['RT_LAST'].values[0] <= Openorder[-1]['Openpos']*(1-stoploss):
                Pos.append(0)
                entryprice = bar['RT_BID1'].values[0]
                Closeorder.append({'Type': -1,'Closepos':entryprice,'Vol':1,'Time': bar.index[0].time()})
                print ("Closeorder:" , Closeorder[-1])
                winsound.PlaySound('SystemQuestion', winsound.SND_ASYNC)
                # 加个止损标志，以防止今天再次开仓
                flag2 = 1
        if Pos[-1] == -1:
            #openposprice = Openorder[:t][Openorder[:t] != 0][-1]['Openpos']
            if bar['RT_LAST'].values[0] >= Openorder[-1]['Openpos']*(1+stoploss):
                Pos.append(0)
                entryprice = bar['RT_ASK1'].values[0]
                Closeorder.append({'Type': 1,'Closepos':entryprice,'Vol':1,'Time': bar.index[0].time()})
                print ("Closeorder:" , Closeorder[-1])
                winsound.PlaySound('SystemQuestion', winsound.SND_ASYNC)
                flag2 = 1
    if bar.index[0].time() >= ExTime:
        ## 收盘平仓
        if Pos[-1] == 1:
            Pos.append(0)
            entryprice = bar['RT_OPEN'].values[0]
            Closeorder.append({'Type': -1,'Closepos':entryprice,'Vol':1,'Time': bar.index[0].time()})
            print ("Closeorder:" , Closeorder[-1])
            winsound.PlaySound('SystemQuestion', winsound.SND_ASYNC)
        if Pos[-1] == -1:
            Pos.append(0)
            entryprice = bar['RT_OPEN'].values[0]
            Closeorder.append({'Type': 1,'Closepos':entryprice,'Vol':1,'Time': bar.index[0].time()})
            print ("Closeorder:" , Closeorder[-1])
            winsound.PlaySound('SystemQuestion', winsound.SND_ASYNC)
    print ('now is:',bar.index[0].time())

if __name__ == '__main__':
    from Rb_papertrading import *
    print ("start run")
    while True:
        runstrategy()
        time.sleep(60)








