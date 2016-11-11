#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2016-10-20 11:34:54
# @Author  : zhao yong

import os
import numpy as np
import pandas as pd
from datetime import datetime
##绘图库
import matplotlib
from matplotlib.font_manager import FontProperties
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_style('whitegrid')

###-----------------------------------------------------------------------------

"""计算指标"""
def MaxDD(cumret):
    ### 计算最大回撤
    highwatermark=np.zeros(len(cumret))
    drawdown=np.zeros(len(cumret))
    drawdownduration=np.zeros(len(cumret))

    for t in range(1,len(cumret)):
        highwatermark[t] = max(highwatermark[t-1], cumret[t])
        drawdown[t] = (1+cumret[t])/(1+highwatermark[t])-1  # drawdown on each day
        if drawdown[t] == 0:
            drawdownduration[t] = 0
        else:
            drawdownduration[t] = drawdownduration[t-1]+1
    maxDD = -min(drawdown) # maximum drawdown
    maxDDD = int(max(drawdownduration)) # maximum drawdown duration
    #drawdownList = drawdown
    return maxDD, maxDDD, drawdown

###-----------------------------------------------------------------------------
"""--收益分析--"""
def stratanalyz(Accountsummny,TradingCost=0.0,save = False):
    ### 转换时间戳,
    ##  TODO: 判断时间格式
    '''
    if type(ret.index.values[0]) is str:
        tdate = map(lambda x:datetime.strptime(x[:-4],
                    '%Y-%m-%d %H:%M:%S').date(),
                    ret.index.values)
    '''
    ret = Accountsummny['Account']/Accountsummny['AccountCum'].shift()
    ret = ret.fillna(0)
    cumret = (1+ret).cumprod()-1

    # 日度数据  TODO:判断时间回测时间周期
    APR = np.prod(1+ret)**(252./len(ret))-1
    Avg_Ann_Ret = 252*ret.mean()
    Ann_Volatility = np.sqrt(252)*ret.std()
    Sharpe_ratio = np.sqrt(252)*ret.mean()/ret.std()
    [maxDD,maxDDD,_]=MaxDD(cumret)
    """--交易分析--"""
    Openorder = Accountsummny['Openorder']
    Closeorder = Accountsummny['Closeorder']
    '''
    #TODO:考虑是否成交！！
    buyCrossPrice = self.bar.low        # 若买入方向限价单价格高于该价格，则会成交
    sellCrossPrice = self.bar.high      # 若卖出方向限价单价格低于该价格，则会成交
    buyBestCrossPrice = self.bar.open   # 在当前时间点前发出的买入委托可能的最优成交价
    sellBestCrossPrice = self.bar.open  # 在当前时间点前发出的卖出委托可能的最优成交价

    # 判断是否会成交
    buyCross = order.direction==DIRECTION_LONG and order.price>=buyCrossPrice
    sellCross = order.direction==DIRECTION_SHORT and order.price<=sellCrossPrice
    if buyCross or sellCross:
    # 推送成交数据
        self.tradeCount += 1            # 成交编号自增1
        tradeID = str(self.tradeCount)
        trade = VtTradeData()
        trade.vtSymbol = order.vtSymbol
        trade.tradeID = tradeID
        trade.vtTradeID = tradeID
        trade.orderID = order.orderID
        trade.vtOrderID = order.orderID
        trade.direction = order.direction
        trade.offset = order.offset

        # 以买入为例：
        # 1. 假设当根K线的OHLC分别为：100, 125, 90, 110
        # 2. 假设在上一根K线结束(也是当前K线开始)的时刻，策略发出的委托为限价105
        # 3. 则在实际中的成交价会是100而不是105，因为委托发出时市场的最优价格是100
        if buyCross:
            trade.price = min(order.price, buyBestCrossPrice)
            self.strategy.pos += order.totalVolume
        else:
            trade.price = max(order.price, sellBestCrossPrice)
            self.strategy.pos -= order.totalVolume

        trade.volume = order.totalVolume
        trade.tradeTime = str(self.dt)
        trade.dt = self.dt
        self.strategy.onTrade(trade)

        self.tradeDict[tradeID] = trade
    '''

    Opentrade = np.array([t[0] for t in Openorder[Openorder != 0]])
    Closetrade = np.array([t[0] for t in Closeorder[Closeorder != 0]])
    CostSeries = np.zeros(len(Closetrade))
    NetMargin = np.zeros(len(Closetrade))
    RateOfReturn = np.zeros(len(Closetrade))
    #净利润和收益率
    for i in range(len(Closetrade)):
        Lots = Opentrade[i]['Vol']
        #交易成本(建仓+平仓)
        CostSeries[i]=(Opentrade[i]['Openpos']+Closetrade[i]['Closepos'])*Lots*TradingCost

        #净利润
        #多头建仓时
        if Closetrade[i]['Type'] == -1:
            NetMargin[i]=(Closetrade[i]['Closepos']-Opentrade[i]['Openpos'])*Lots-CostSeries[i]

        #空头建仓时
        if Closetrade[i]['Type'] == 1:
            NetMargin[i]=(Opentrade[i]['Openpos']-Closetrade[i]['Closepos'])*Lots-CostSeries[i]
        #收益率
        RateOfReturn[i]=NetMargin[i]/(Opentrade[i]['Openpos']*Lots)

    # 累计净利
    CumNetMargin = NetMargin.cumsum()
    # 累计盈利
    cumpay = NetMargin[NetMargin > 0].cumsum()[-1]
    # 累计亏损
    cumoff = NetMargin[NetMargin < 0].cumsum()[-1]
    #累计收益率
    CumRateOfReturn = RateOfReturn.cumsum()
    # 后边计算每笔收益需要用
    Pnl = NetMargin
    #交易手数
    trades = len(Closetrade)
    # 盈亏比
    payoff = float(cumpay)/-cumoff
    # 胜率
    Winrate = float(len(RateOfReturn[RateOfReturn>0]))/len(Closetrade)

    pf = dict((['APR', format(APR,'.4%')],
                ['Ann_Ann_Ret',format(Avg_Ann_Ret,'.2%')],
                ['Ann_Volatility', format(Ann_Volatility,'.2%')],
                ['Sharpe_ratio', Sharpe_ratio],
                ['maxDD', format(maxDD,'.2%')],
                ['maxDDD', maxDDD],
                ['trades', trades],
                ['payoff', payoff],
                ['Winrate', format(Winrate,'.2%')]))
    performance = pd.DataFrame.from_dict(pf, orient="index")
    performance = performance.rename(columns={0: 'Performance'})
    ## 保存结果
    if save == True:
        performance.to_csv('perfornamc_summry.csv')
    return performance,Pnl

###-----------------------------------------------------------------------------
"""绘图保存"""

def ploter(Accountsummny, save=False):
    price = Accountsummny['Close']
    ret = Accountsummny['Account']/Accountsummny['Close'].shift()
    ret = ret.fillna(0)

    cumret = (1+ret).cumprod()-1

    name = matplotlib.matplotlib_fname()
    font = FontProperties(fname = name)
    if len(ret.index.values[0]) >= 12:
        tdate = map(lambda x:datetime.strptime(x[:-4], '%Y-%m-%d %H:%M:%S').date(),
                    ret.index.values)
    else:
        tdate = map(lambda x:datetime.strptime(x, '%Y%m%d').date(),
                    ret.index.values)

    Fig = plt.figure(figsize=(20,10))
    pcumret = plt.subplot(3,1,1)
    pcumret.plot(tdate, cumret.values, label='Cumret', color='b', )
    pcumret.legend(loc=2)
    pcumret.set_ylabel('Cumret', fontsize=16)
    pcumret.set_title(u'Blue is Cumret, red is Price',fontsize=16)
    pprice=plt.twinx()

    ###创建公用的y坐标轴
    pprice.plot(tdate,price.values, label='Price',color='r')
    pprice.legend(loc=0)
    pprice.set_ylabel('Price', fontsize=16)

    ### 最大回撤
    pDD = plt.subplot(3, 1, 2)
    pDD.set_ylabel("Drawdown", fontsize=16)
    [_, _, drawdownList]=MaxDD(cumret)
    pDD.fill_between(tdate, drawdownList, color='r')
    pDD.set_title(u'Drawdown',fontsize=16)
    pdown = plt.twinx()
    pdown.plot(tdate, cumret.values, label='Cumret', color='b', )
    pdown.legend(loc=2)
    pdown.set_ylabel('Cumret', fontsize=16)
    ### 每笔收益
    _,Pnl = stratanalyz(Accountsummny)
    pPnl = plt.subplot(3, 1, 3)
    pPnl.set_ylabel("Pnl",fontsize=16)
    pPnl.bar(range(len(Pnl)),Pnl ,color='b')
    pPnl.set_title(u'PnL',fontsize=16)
    plt.show()
    if save == True:
        plt.savefig('Record.png')

###-----------------------------------------------------------------------------
if __name__ == '__main__':
    # 输入：每笔收益率，资产价格，type：pd.Serise
    # 输出：回测指标(type: pd.Dataframe)，图片
    from perforanalyze import *
    pf,Pnl = stratanalyz(Accountsummny)
    ploter(Accountsummny)
