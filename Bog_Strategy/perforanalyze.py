#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2016-10-20 11:34:54
# @Author  : zhao yong

import os
import numpy as np
import scipy.io as scio
import pandas as pd
from datetime import datetime

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

def stratanalyz(ret,save = False):
    ### 转换时间戳,
    ##  TODO: 判断时间格式
    '''
    if type(ret.index.values[0]) is str:
        tdate = map(lambda x:datetime.strptime(x[:-4], '%Y-%m-%d %H:%M:%S').date(),
                    ret.index.values)
    '''
    cumret = (1+ret).cumprod()-1

    APR = np.prod(1+ret)**(252./len(ret))-1
    Avg_Ann_Ret = 252*ret.mean()
    Ann_Volatility = np.sqrt(252)*ret.std()
    Sharpe_ratio = np.sqrt(252)*ret.mean()/ret.std()
    [maxDD,maxDDD,_]=MaxDD(cumret)
    trades = len(ret[ret != 0])
    payoff = ret[ret > 0].mean()/-ret[ret < 0].mean()
    Winrate = float(sum(ret > 0))/len(ret)

    pf = dict((['APR', format(APR,'.4%')],
                        ['Avg_Ann_Ret', format(Avg_Ann_Ret,'.2%')],
                        ['Ann_Volatility', format(Ann_Volatility,'.2%')],
                        ['Winrate', format(Winrate,'.2%')],
                        ['Sharpe_ratio', Sharpe_ratio],
                        ['maxDD', format(maxDD,'.2%')],
                        ['maxDDD', maxDDD],
                        ['trades', trades],
                        ['payoff', payoff]))
    performance = pd.DataFrame.from_dict(pf, orient="index")
    performance = performance.rename(columns={0: 'Performance'})
    ## 保存结果
    if save == True:
        performance.to_csv('perfornamc_summry.csv')
    return performance

###-----------------------------------------------------------------------------
"""绘图保存"""
import matplotlib
from matplotlib.font_manager import FontProperties
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_style('whitegrid')

def ploter(price, ret, save=False):
    name = matplotlib.matplotlib_fname()
    font = FontProperties(fname = name)
    if len(ret.index.values[0]) >= 12:
        tdate = map(lambda x:datetime.strptime(x[:-4], '%Y-%m-%d %H:%M:%S').date(),
                    ret.index.values)
    else:
        tdate = map(lambda x:datetime.strptime(x, '%Y%m%d').date(),
                    ret.index.values)
    cumret = (1+ret).cumprod()-1

    Fig = plt.figure(figsize=(20,10))
    pcumret = plt.subplot(3,1,1)
    pcumret.plot(tdate, cumret.values, label='Cumret', color='b', )
    pcumret.legend(loc=2)
    pcumret.set_ylabel('Cumret', fontsize=16)
    pcumret.set_title(u'Blue is Cumret, red is Price',fontsize=16)
    pprice=plt.twinx()

    ###创建公用的y坐标轴
    pprice.plot(tdate,price, label='Price',color='r')
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
    pPnl = plt.subplot(3, 1, 3)
    pPnl.set_ylabel("Pnl",fontsize=16)
    pPnl.bar(tdate, ret, width=3.5 ,color='b')
    pPnl.set_title(u'PnL',fontsize=16)
    plt.show()
    if save == True:
        plt.savefig('Record.png')

###-----------------------------------------------------------------------------
if __name__ == '__main__':
    # 输入：每笔收益率，资产价格，type：pd.Serise
    # 输出：回测指标(type: pd.Dataframe)，图片

    pf = stratanalyz(ret)
    ploter(price, ret)
