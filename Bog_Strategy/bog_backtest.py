#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2016-10-21 13:09:19
# @Author  : zhao yong

import os
import numpy as np
import scipy.io as scio
import pandas as pd
from datetime import datetime

###----------------------------------------------------------------------
"""加载数据"""
def loaddata(filename):
  data = scio.loadmat(filename)
  temp = data['syms'][0]==u'FSTX'
  p = temp.tolist().index(True)
  tday = data['tday'][:,p].astype(int).astype(str)   # 转str
  cl = data['cl'][:,p]
  op = data['op'][:,p]
  hi = data['hi'][:,p]
  lo = data['lo'][:,p]
  ## 数据打包
  df = pd.DataFrame(index=tday, data=np.array([cl,op,hi,lo]).T,
                    columns=['CLOSE','OPEN','HIGH','LOW'])
  return df

###----------------------------------------------------------------------

"""加载wind数据"""
def loadwdata(file):
  df = pd.read_csv(file, index_col=0)
  return df
###----------------------------------------------------------------------

"""开始回测"""
def backtest(m, n, file):

  ### 输入：两个参数，为计算辅助参数zscore与计算波动率窗口
  ### 输出：收益率, 价格
  ### 先加载数据
  #df = loaddata('inputDataOHLCDaily_20120517.mat')
  df = loadwdata(file)

  entryZscore=m
  stddays=n

  dailyret = df['CLOSE'].pct_change()
  movingstd = dailyret.rolling(n).std().shift()

  ## 观测开盘价，过高或过低

  longs = df['OPEN'] <= df['LOW'].shift()*(1-entryZscore*movingstd)
  shorts = df['OPEN'] >= df['HIGH'].shift()*(1+entryZscore*movingstd)

  pos = np.zeros(len(df['CLOSE']))
  pos[longs.values] = 1
  pos[shorts.values] = -1

  ret=pos*(df['CLOSE']-df['OPEN'])/df['OPEN']
  ret = ret.fillna(0)


  return ret, df['CLOSE'].values

###----------------------------------------------------------------------

if __name__ == '__main__':
  backtest(0.1, 90, '../winddata/J00.DCE.csv')