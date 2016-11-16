# -*- coding: utf-8 -*-
"""
Created on Wed Nov 16 15:59:12 2016

@author: zhaoyong
"""



import Population
import Individual
from matplotlib import pyplot as plt
import datetime
import numpy as np
import pandas as pd
import seaborn as sns
sns.set_style('whitegrid')

#t, a, b, tc, m, c, w, phi
inf = 2000.0
# 对初值很敏感！
#limits = ([0, 3], [.1, 1], [520, 850], [1, 2], [-1,1], [.1,2], [-1, 1])
limits = ([7.0, 9.0], [-1, -0.1], [300, 400], [.1,.9], [-1,1], [12,18], [0, 2*np.pi])
x = Population.Population(limits, 20, 0.3, 1.5, .05, 4)
for i in range(2):
    x.Fitness()
    x.Eliminate()
    """
    values = x.BestSolutions(3)
    for j in values:
        print j.PrintIndividual()
    """
    x.Mate()
    x.Mutate()

x.Fitness()
values = x.BestSolutions(3)
for x in values:
    print x.PrintIndividual()
"""
print "var dump"
try:
	print values[0].cof
except:
	print "nothing"

"""
x = values[0]
plt.figure(figsize=(16,8))
plt.plot(x.getActSerise()[0], x.getActSerise()[1])
#预测线
plt.plot(x.getActSerise()[0][:-160], x.getExpData())

plt.show()
