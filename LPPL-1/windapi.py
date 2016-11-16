# -*- coding: utf-8 -*-
"""
Created on Wed Nov 16 14:29:37 2016

@author: zhaoyong
"""

from WindPy import w
import pandas as pd
import datetime
w.start()

w_data = w.wsd("000001.SH", "close", "2014-01-17", "2016-01-15", "")

#演示如何将api返回的数据J00.DCE装入Pandas的DataFrame
fm=pd.DataFrame(w_data.Data,index=w_data.Fields,columns=w_data.Times)
fm=fm.T #将矩阵转置
# 存为csv格式
fm.to_csv('HS300.csv')
