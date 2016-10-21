# -*- coding: utf-8 -*-
"""
Created on Thu Oct 20 15:39:18 2016

@author: zhao yong
"""
from WindPy import w
import pandas as pd
import datetime
w.start()


symlist = ["AU00.SHF","CF00.CZC", "CU00.SHF", "J00.DCE",
           "L00.DCE","P00.DCE", "RB00.SHF","RU00.SHF",
           "SR00.CZC","M00.DCE"]
# 取数据的命令如何写可以用命令生成器来辅助完成
for sym in symlist:
    w_data=w.wsd(sym, "open,high,low,close,volume,amt",
             "2012-09-20", "2016-10-20", "Fill=Previous")
    #演示如何将api返回的数据J00.DCE装入Pandas的DataFrame
    fm=pd.DataFrame(w_data.Data,index=w_data.Fields,columns=w_data.Times)
    fm=fm.T #将矩阵转置
    # 存为csv格式
    fm.to_csv('winddata/'+sym+'.csv')
    print sym +'is done'
print 'Congratulations, all data is loaded'