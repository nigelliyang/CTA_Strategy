# -*- coding: utf-8 -*-
"""
Created on Mon Oct 24 15:43:43 2016

@author: zhaoyong
"""

import os
import numpy as np
import scipy.io as scio
import pandas as pd
import statsmodels.api as sm
from statsmodels.tsa.stattools import coint
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_style('whitegrid')
def loaddata(filename='inputData_ETF'):
  #filename = 'inputData_ETF'
  data = scio.loadmat(filename)

  idxA=data['syms'][0] == u'EWA'
  idxC=data['syms'][0] == u'EWC'

  pA = idxA.tolist().index(True)
  pB = idxC.tolist().index(True)
  ## 收盘价序列
  clA = data['cl'][:,pA]
  clB = data['cl'][:,pB]
  return clA, clB
def plotpairs(clA,clB):
  clA,clB = loaddata()
  # 绘图展示
  plt.figure(1)
  plt.plot(clA,label='EWA',color='b')
  plt.plot(clB,label='EWC',color='g')
  plt.legend()

  plt.figure(2)
  plt.scatter(clA,clB)
  ## 线性回归
  clA = sm.add_constant(clA)
  regression_result = sm.OLS(clB, clA).fit()
  hedgeRatio = regression_result.params[1]
  ## 确定对冲比例
  # 先还原clA
  clA = clA[:,1]
  clC = clB-hedgeRatio*clA
  plt.figure(3)
  plt.plot(clC)
  ## 检验协整
  results = coint(clA,clB)
  """
  发现t值与matlab计算的不一样， matlab的t值为：-3.64346635
  可能是计算方法导致的
  (-4.266081385013182,
   0.0028902799760024737,
   array([-3.43471702, -2.86346876, -2.56779685]))
  """
  ## 没有找到johansen检验
if __name__ == '__main__':
  from pairs_trading_test import *
  plotpairs()



