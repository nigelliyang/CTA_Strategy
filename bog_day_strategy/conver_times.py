# -*- coding: utf-8 -*-
"""
Created on Wed Oct 26 17:46:35 2016

@author: zhaoyong
"""

import os
import numpy as np

import pandas as pd
from datetime import datetime

##----------------------------------------------------------------------------

# 转换时间
df1 = pd.read_csv('../ts_data/J00.DCE.night2014.csv',index_col=0)

df2 = pd.read_csv('../ts_data/J00.DCE.night2015.csv',index_col=0)

df3 = pd.concat([df1,df2])
# 读取转换后的数据
df3.to_csv('../ts_data/J00.DCE.night.csv')

open_time = [i[-4:] == '9:31' for i in df3.index]
df_open = df3[np.array(open_time)]
#输出
df_open.to_csv('../ts_data\M00.DCE.open.csv')

df_day = pd.read_csv('../ts_data/J00.DCE.csv',index_col=0)

df_open = pd.read_csv('../ts_data/J00.DCE.open.csv',index_col=0)

df_day['dayopen'] = df_day['open']
#循环
for i in range(len(df_open.index)):
    for j in range(len(df_day.index)):
        if df_day.index[j] == df_open.index[i][:-5]:
            df_day['dayopen'][j] = df_open['open'][i]
# 保存带有早九点半开盘价的数据文件
df_day.to_csv('../ts_data\J00.DCE.addopen.csv')

            
