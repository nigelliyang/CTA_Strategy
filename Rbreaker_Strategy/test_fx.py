# -*- coding: utf-8 -*-
"""
Created on Mon Nov 07 18:53:48 2016

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
ldata = w.wsd("GBPUSD.FX", "open,high,low,close,volume,amt", "2016-11-04", "2016-11-04", "")
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

highprice = []
lowprice = []

# 交易时间设置
StartTime = datetime.strptime('9:35',"%H:%M").time()
noontime = datetime.strptime('14:00',"%H:%M").time()
ExTime = datetime.strptime('14:45',"%H:%M").time()
flag2 = 0

# 合成一分钟K线
bar = {}
bar['Minute'] = ''

#----------------------------------------------------------------------

"""收到行情TICK推送"""
def onTick():
    # 计算K线
    """读取行情数据"""

    wdata = w.wsq("GBPUSD.FX",
    "rt_date,rt_time,rt_open,rt_high,rt_low,rt_last,rt_last_amt,rt_last_vol,rt_latest,rt_vol,rt_amt,rt_bid1,rt_ask1")
    tick = pd.DataFrame(wdata.Data,index=wdata.Fields,columns=wdata.Times)
    tick = tick.T
    tickMinute = tick.index[0].minute

    print (u'bar minute:', bar['Minute'])

    if tickMinute != bar['Minute']:
        if bar['Minute']:
            print ('start strategy')
            # 执行策略
            runstrategy(bar)

        bar['open'] = tick['RT_LAST'][0]
        bar['high'] = tick['RT_LAST'][0]
        bar['low'] = tick['RT_LAST'][0]
        bar['close'] = tick['RT_LAST'][0]

        bar['date'] = tick.index[0].date()
        bar['time'] = tick.index[0].time()
        bar['datetime'] = tick.index[0]    # K线的时间设为第一个Tick的时间
        bar['Minute'] = tickMinute     # 更新当前的分钟


    else:                               # 否则继续累加新的K线
        bar['high'] = max(bar['high'], tick['RT_LAST'][0])
        bar['low'] = min(bar['low'], tick['RT_LAST'][0])
        bar['close'] = tick['RT_LAST'][0]
        bar['ask1'] = tick['RT_ASK1'][0]
        bar['bid1'] = tick['RT_BID1'][0]

#------------------------------------------------------------------------------

"""开始循环"""
def runstrategy(bar):
    """设定波幅过滤"""
    shouldopen = abs(float(Lopen - Lclose)/Lopen) > 0.0001

    if StartTime <= bar['time'] < ExTime and shouldopen:
        highprice.append(bar['high'])   # 存行情数据
        lowprice.append(bar['low'])
        todayhigh = max(highprice)
        todaylow = min(lowprice)
        # 防止反复开仓
        flag1 = 0
        global flag2
        revershorts = todayhigh > views and bar['low'] < reves+(todayhigh-views)/3
        if revershorts and bar['bid1'] != 0 and bar['time'] <= noontime and flag2 == 0:
            ## 先平多，再做空
            if Pos[-1] == 1:
                Pos.append(-1)
                entryprice = bar['bid1']
                Closeorder.append({'Type':-1,'Closepos':entryprice,'Vol':1,'Time':bar['time']})
                Openorder.append({'Type':-1,'Openpos':entryprice,'Vol':1,'Time':bar['time']})
                print ("Closeorder:" , Closeorder[-1])
                print ("Openorder:" , Openorder[-1])
                winsound.PlaySound('SystemHand', winsound.SND_ASYNC)
            ## 开仓做空
            if Pos[-1] == 0 and flag1 == 0:
                Pos.append(-1)
                #entryprice = min(openp[t],reves[t]+(todayhigh-views[t])/3)
                entryprice = bar['bid1']
                Openorder.append({'Type':-1,'Openpos':entryprice,'Vol':1,'Time':bar['time']})
                print ("Openorder:" , Openorder[-1])
                winsound.PlaySound('SystemHand', winsound.SND_ASYNC)
                flag1 = 1
        reverlongs = todaylow < viewb and bar['high'] > reveb-(viewb-todaylow)/3
        if reverlongs and bar['ask1'] != 0 and bar['time'] <= noontime and flag2 == 0:
            ## 先平空，再做多
            if Pos[-1] == -1:
                Pos.append(1)
                #entryprice = max(openp[t],reveb[t]-(viewb[t]-todaylow)/3)
                entryprice = bar['ask1']
                Closeorder.append({'Type': 1,'Closepos':entryprice,'Vol':1,'Time': bar['time']})
                Openorder.append({'Type': 1,'Openpos':entryprice,'Vol':1,'Time': bar['time']})
                print ("Closeorder:" , Closeorder[-1])
                print ("Openorder:" , Openorder[-1])
                winsound.PlaySound('SystemHand', winsound.SND_ASYNC)
            ## 开仓做多
            if Pos[-1] == 0 and flag1 == 0:
                Pos.append(1)
                #entryprice = max(openp[t],reveb[t]-(viewb[t]-todaylow)/3)
                entryprice = bar['ask1']
                Openorder.append({'Type': 1,'Openpos':entryprice,'Vol':1,'Time': bar['time']})
                print ("Openorder:" , Openorder[-1])
                winsound.PlaySound('SystemHand', winsound.SND_ASYNC)
                flag1 = 1
        if Pos[-1] == 0:
            longs = bar['high'] > breab and bar['time'] <= noontime and flag2 == 0
            ## 空仓做多
            if longs and bar['ask1'] != 0 and flag1 == 0:
                Pos.append(1)
                #entryprice = max(openp[t],breab[t])
                entryprice = bar['ask1']
                Openorder.append({'Type': 1,'Openpos':entryprice,'Vol':1,'Time': bar['time']})
                print ("Openorder:" , Openorder[-1])
                winsound.PlaySound('SystemHand', winsound.SND_ASYNC)
                flag1 = 1
            ## 空仓做空
            shorts = bar['low'] < breas and bar['time'] <= noontime and flag2 == 0
            if shorts and bar['bid1'] != 0 and flag1 == 0:
                Pos.append(-1)
                #entryprice = min(openp[t],breas[t])
                entryprice = bar['bid1']
                Openorder.append({'Type': -1,'Openpos':entryprice,'Vol':1,'Time': bar['time']})
                print ("Openorder:" , Openorder[-1])
                winsound.PlaySound('SystemHand', winsound.SND_ASYNC)
                flag1 = 1
        # 止损平仓
        if Pos[-1] == 1:
        #openposprice = Openorder[:t][Openorder[:t] != 0][-1]['Openpos']
            if bar['low'] <= Openorder[-1]['Openpos']*(1-stoploss):
                Pos.append(0)
                entryprice = bar['bid1']
                Closeorder.append({'Type': -1,'Closepos':entryprice,'Vol':1,'Time': bar['time']})
                print ("Closeorder:" , Closeorder[-1])
                winsound.PlaySound('SystemQuestion', winsound.SND_ASYNC)
                # 加个止损标志，以防止今天再次开仓
                flag2 = 1
        if Pos[-1] == -1:
            #openposprice = Openorder[:t][Openorder[:t] != 0][-1]['Openpos']
            if bar['high'] >= Openorder[-1]['Openpos']*(1+stoploss):
                Pos.append(0)
                entryprice = bar['ask11']
                Closeorder.append({'Type': 1,'Closepos':entryprice,'Vol':1,'Time': bar['time']})
                print ("Closeorder:" , Closeorder[-1])
                winsound.PlaySound('SystemQuestion', winsound.SND_ASYNC)
                flag2 = 1
    if bar['time'] >= ExTime:
        ## 收盘平仓
        if Pos[-1] == 1:
            Pos.append(0)
            entryprice = bar['open']
            Closeorder.append({'Type': -1,'Closepos':entryprice,'Vol':1,'Time': bar['time']})
            print ("Closeorder:" , Closeorder[-1])
            winsound.PlaySound('SystemQuestion', winsound.SND_ASYNC)
        if Pos[-1] == -1:
            Pos.append(0)
            entryprice = bar['open']
            Closeorder.append({'Type': 1,'Closepos':entryprice,'Vol':1,'Time': bar['time']})
            print ("Closeorder:" , Closeorder[-1])
            winsound.PlaySound('SystemQuestion', winsound.SND_ASYNC)
    print ('now is:',bar['time'])

if __name__ == '__main__':
    from test_fx import *
    print ("start run")
    while True:
        onTick()








