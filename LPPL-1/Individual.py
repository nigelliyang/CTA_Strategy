# -*- coding: utf-8 -*-
"""
Created on Wed Nov 16 15:59:12 2016

@author: zhaoyong
"""



import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import fmin_tnc
import random

import pandas as pd
import pandas.io.data
import datetime

def lppl(t,x): #return fitting result using LPPL parameters
    a = x[0]
    b = x[1]
    tc = x[2]
    m = x[3]
    c = x[4]
    w = x[5]
    phi = x[6]
    return a + (b*np.power(tc - t, m))*(1 + (c*np.cos((w *np.log(tc-t))+phi)))

def func(x):
    delta = [lppl(t,x) for t in DataSeries[0]] #生成lppl时间序列
    delta = np.subtract(delta, DataSeries[1]) #将生成的lppl时间序列减去对数指数序列
    delta = np.power(delta, 2)
    return np.sum(delta) #返回拟合均方差


class Individual:
    'base class for individuals'

    def __init__ (self, InitValues):
        self.fit = 0
        self.cof = InitValues

    def fitness(self): #
        try:
            cofs, nfeval, rc = fmin_tnc(func, self.cof, fprime=None,approx_grad=True, messages=0) #基于牛顿梯度下山的寻找函数最小值
            self.fit = func(cofs)
            self.cof = cofs
        except:

            #does not converge
            return False
    def mate(self, partner): #交配
        reply = []
        for i in range(0, len(self.cof)): # 遍历所以的输入参数
            if (random.randint(0,1) == 1): # 交配，0.5的概率自身的参数保留，0.5的概率留下partner的参数，即基因交换
                reply.append(self.cof[i])
            else:
                reply.append(partner.cof[i])

        return Individual(reply)
    def mutate(self): #突变
        for i in range(0, len(self.cof)-1):
            if (random.randint(0,len(self.cof)) <= 2):
                #print "Mutate" + str(i)
                self.cof[i] += random.choice([-1,1]) * .05 * i #突变

    def PrintIndividual(self): #打印结果
        #t, a, b, tc, m, c, w, phi
        cofs = "A: " + str(round(self.cof[0], 3))
        cofs += "B: " + str(round(self.cof[1],3))
        cofs += "Critical Time: " + str(round(self.cof[2], 3))
        cofs += "m: " + str(round(self.cof[3], 3))
        cofs += "c: " + str(round(self.cof[4], 3))
        cofs += "omega: " + str(round(self.cof[5], 3))
        cofs += "phi: " + str(round(self.cof[6], 3))

        return "fitness: " + str(self.fit) +"\n" + cofs
        #return str(self.cof) + " fitness: " + str(self.fit)
    def getDataSeries(self):
        return DataSeries
    def getExpData(self):
        return [np.exp(lppl(t,self.cof)) for t in DataSeries[0]]
    def getActSerise(self):
        return date_close


def fitFunc(t, a, b, tc, m, c, w, phi):
    return a + (b*np.power(tc - t, m))*(1 + (c*np.cos((w *np.log(tc-t))+phi)))

#SP = pd.io.data.get_data_yahoo('^GSPC', start=datetime.datetime(2012, 5, 1),end=datetime.datetime(2015, 5, 23))
HS = pd.read_csv('HS300.csv', index_col=0)
HS['datetime'] = HS.index.to_datetime()

time = np.linspace(0, len(HS)-1, len(HS))
close = [np.log(HS.CLOSE[i]) for i in range(len(HS.CLOSE))]
#close = SP.Close.values
global DataSeries
DataSeries = [time[:-160], close[:-160]]
global date_close
date_close = [HS['datetime'].values, HS.CLOSE.values]
