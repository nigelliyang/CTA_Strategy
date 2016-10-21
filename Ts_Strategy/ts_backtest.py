#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2016-10-20 13:34:47
# @Author  : zhao yong

import os
import numpy as np
import scipy.io as scio
import pandas as pd
from datetime import datetime

###----------------------------------------------------------------------
"""加载数据"""
def loaddata(file):
  data = scio.loadmat(file)
  temp = data['syms'][0]==u'TU'
  p = temp.tolist().index(True)
  tday = data['tday'][:,p].astype(int).astype(str)   # 转str
  cl = data['cl'][:,p]
  ## tday, cl 转为series
  clseries = pd.Series(index=tday, data=cl)
  return tday, cl, clseries

###----------------------------------------------------------------------

"""加载wind数据"""
def loadwdata(file):
  df = pd.read_csv(file, index_col=0)
  clseries = df.CLOSE
  tday = clseries.index.values
  cl = clseries.values
  return tday, cl, clseries
###----------------------------------------------------------------------

"""开始回测"""
def backtest(m,n,file):

  ### 输入：两个参数，为回望周期与持有周期
  ### 输出：收益率, 价格
  ### 先加载数据
  #tday, cl, clseries = loaddata('inputDataOHLCDaily_20120511.mat')
  # RB00,J00
  #tday, cl, clseries = loadwdata('winddata/rb00.csv')
  tday, cl, clseries = loadwdata(file)
  lookback=m
  holddays=n

  ## 过去250天收益为正，做多；为负，做空

  longs_log = clseries > clseries.shift(lookback)
  shorts_log = clseries < clseries.shift(lookback)

  ## logical转int

  longs = longs_log.astype(int)
  shorts = shorts_log.astype(int)

  pos = np.zeros(len(cl))

  for h in range(holddays):
      long_lag = longs.shift(h)
      long_lag[np.isnan(long_lag)] = False
      long_lag = long_lag.astype(bool)

      short_lag = shorts.shift(h)
      short_lag[np.isnan(short_lag)] = False
      short_lag = short_lag.astype(bool)

      pos[long_lag.values] = pos[long_lag.values] + 1
      pos[short_lag.values] = pos[short_lag.values] - 1
  position = pd.Series(index=tday, data=pos,dtype=int)
  ret = position.shift(1)*clseries.pct_change()/holddays
  ret = ret.fillna(0)
  return ret, cl

###----------------------------------------------------------------------

if __name__ == '__main__':
  backtest(250, 25, '../winddata/J00.DCE.csv')