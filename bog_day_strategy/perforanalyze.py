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

font = FontProperties(fname='/Library/Fonts/hwxh.ttf')  #  设置中文字体

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
    
    # 回测周期，开始结束时间
    
    startday = Accountsummny.index[0]
    endday = Accountsummny.index[-1]
    days = len(Accountsummny)
    ### TOTO:判断时间周期，252需要改
    APR = np.prod(1+ret)**(252./len(ret))-1
    Avg_Ann_Ret = 252*ret.mean()
    Ann_Volatility = np.sqrt(252)*ret.std()
    Sharpe_ratio = np.sqrt(252)*ret.mean()/ret.std()
    [maxDD,maxDDD,_]=MaxDD(cumret)
    calmar_ratio = float(APR)/maxDD
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

    Opentrade = np.array([t for t in Openorder[Openorder != 0]])
    Closetrade = np.array([t for t in Closeorder[Closeorder != 0]])
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

    pf = np.array([[u'开始时间',startday],
               [u'结束时间', endday],
               [u'回测周期', days],
                [u'年化收益率', format(APR,'.4%')],
                [u'平均每年收益',format(Avg_Ann_Ret,'.2%')],
                [u'年化波动率', format(Ann_Volatility,'.2%')],
                [u'夏普率', Sharpe_ratio],
                [u'最大回撤', format(maxDD,'.2%')],
                [u'最大回撤周期', maxDDD],
                [u'Calmar比率', calmar_ratio],
                [u'交易次数', trades],
                [u'盈亏比', payoff],
                [u'胜率', format(Winrate,'.2%')]])
    performance = pd.DataFrame(pf)
    #performance = performance.rename(columns={0: 'Performance'})
    ## 保存结果
    if save == True:
        performance.to_csv('perfornamc_summry.csv')
    return performance,Pnl

###-----------------------------------------------------------------------------
"""绘图保存"""

def ploter(Accountsummny, save=False):
    price = Accountsummny['Close']
    ret = Accountsummny['Account']/Accountsummny['AccountCum'].shift()
    ret = ret.fillna(0)

    cumret = (1+ret).cumprod()-1

    if len(ret.index.values[0]) >= 12:
        tdate = map(lambda x:datetime.strptime(x[:-4], '%Y-%m-%d %H:%M:%S').date(),
                    ret.index.values)
    else:
        tdate = map(lambda x:datetime.strptime(x, '%Y/%m/%d').date(),
                    ret.index.values)
    
    font = FontProperties(fname='/Library/Fonts/hwxh.ttf')  #  设置中文字体
    
    plt.figure(1,figsize=(16,8))
    #pcumret = plt.subplot(1,1,1)
    plt.plot(tdate, cumret.values, color='b')
    plt.legend(loc=2)
    plt.ylabel(u'累计收益率', fontproperties=font,fontsize=16)
    plt.title(u'蓝线为累计收益率，红线为标的',fontproperties=font,fontsize=16)
    pprice=plt.twinx()

    ###创建公用的y坐标轴
    pprice.plot(tdate,price.values,color='r')
    pprice.legend(loc=0)
    pprice.set_ylabel(u'标的价格', fontproperties=font,fontsize=16)
    
    ### 最大回撤
    plt.figure(2,figsize=(16,8))
    plt.ylabel(u"最大回撤", fontproperties=font,fontsize=16)
    [_, _, drawdownList]=MaxDD(cumret)
    plt.fill_between(tdate, drawdownList, color='r')
    plt.title(u"最大回撤", fontproperties=font,fontsize=16)
    pdown = plt.twinx()
    pdown.plot(tdate, cumret.values, color='b')
    pdown.legend(loc=2)
    pdown.set_ylabel(u'累计收益率', fontproperties=font,fontsize=16)
    ### 每笔收益
    _,Pnl = stratanalyz(Accountsummny)
    plt.figure(3,figsize=(16,8))
    plt.ylabel(u"每笔盈亏", fontproperties=font,fontsize=16)
    plt.bar(range(len(Pnl)),Pnl ,color='b')
    plt.title(u"每笔盈亏", fontproperties=font,fontsize=16)
    
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
