#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
 @Date    : 2016-11-04 15:43:02
 @Author  : Zhao Yong
'''

import os
import numpy as np
import pandas as pd
import time
from datetime import datetime
from collections import OrderedDict
from itertools import product
import multiprocessing
# 加载策略
from Rb_test import *


#----------------------------------------------------------------------
def runOptimization(filename,optimizationSetting):
    """优化参数"""
    # 获取优化设置
    settingList = optimizationSetting.generateSetting()
    targetName = optimizationSetting.optimizeTarget

    # 遍历优化
    resultList = []
    for setting in settingList:
        Accountsummny = runstrategy(filename,setting)
        _,_,d = stratanalyz(Accountsummny)
        targetValue = d[targetName]
        resultList.append(([str(setting)], targetValue))

    # 显示结果
    resultList.sort(reverse=True, key=lambda result:result[1])
    print ('-' * 30)
    print (u'优化结果：')
    for result in resultList:
        print (u'%s: %s' %(result[0], result[1]))
    return result
#----------------------------------------------------------------------
'''
def runParallelOptimization(self, strategyClass, optimizationSetting):
    """并行优化参数"""
    # 获取优化设置
    settingList = optimizationSetting.generateSetting()
    targetName = optimizationSetting.optimizeTarget

    # 检查参数设置问题
    if not settingList or not targetName:
        self.output(u'优化设置有问题，请检查')

    # 多进程优化，启动一个对应CPU核心数量的进程池
    pool = multiprocessing.Pool(multiprocessing.cpu_count())
    l = []
    for setting in settingList:
        l.append(pool.apply_async(optimize, (strategyClass, setting,
                                             targetName, self.mode,
                                             self.startDate, self.initDays, self.endDate,
                                             self.slippage, self.rate, self.size,
                                             self.dbName, self.symbol)))
    pool.close()
    pool.join()

    # 显示结果
    resultList = [res.get() for res in l]
    resultList.sort(reverse=True, key=lambda result:result[1])
    self.output('-' * 30)
    self.output(u'优化结果：')
    for result in resultList:
        self.output(u'%s: %s' %(result[0], result[1]))


'''
########################################################################
class OptimizationSetting(object):
    """优化设置"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        self.paramDict = OrderedDict()

        self.optimizeTarget = ''        # 优化目标字段

    #------------------------------------------------------------------
    def addParameter(self, name, start, end, step):
        """增加优化参数"""
        if end <= start:
            print u'参数起始点必须小于终止点'
            return

        if step <= 0:
            print u'参数布进必须大于0'
            return

        l = []
        param = start

        while param <= end:
            l.append(param)
            param += step

        self.paramDict[name] = l

    #-------------------------------------------------------------------
    def generateSetting(self):
        """生成优化参数组合"""
        # 参数名的列表
        nameList = self.paramDict.keys()
        paramList = self.paramDict.values()

        # 使用迭代工具生产参数对组合
        productList = list(product(*paramList))

        # 把参数对组合打包到一个个字典组成的列表中
        settingList = []
        for p in productList:
            d = dict(zip(nameList, p))
            settingList.append(d)

        return settingList

    #----------------------------------------------------------------------
    def setOptimizeTarget(self, target):
        """设置优化目标字段"""
        self.optimizeTarget = target
#----------------------------------------------------------------------
if __name__ == '__main__':

    from Opt import *
    setting = OptimizationSetting()
    setting.setOptimizeTarget(u'夏普率')            # 设置优化排序的目标是策略净盈利
    setting.addParameter('m', 0.1, 0.2, 0.01)    # 增加第一个优化参数atrLength，起始11，结束12，步进1
    setting.addParameter('n', 0.3, 0.4, 0.01)        # 增加第二个优化参数atrMa，起始20，结束30，步进1
    setting.addParameter('l', 0.1, 0.2, 0.01)
    import time
    start = time.time()

    result = runOptimization('../../ts_data/1min/RB.SHF.1MIN_PLUS.csv',setting)
    print u'耗时：%s' %(time.time()-start)

