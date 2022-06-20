# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# > Author     : lunar
# > Email       : lunar_ubuntu@qq.com
# > Create Time: Sat 15 Aug 2020 05:23:01 PM CST

# Python数值拟合函数
# 数值拟合是数学建模中非常有用的技能
# 在scipy库中提供了根据数据点得出拟合函数的函数
# 拟合的基本步骤为：
# 1. 提供一个初始函数。拟合函数本质上是修改目标函数的参数，并不能
#    根据数据得出一个函数。所以初期需要根据数据点初步拟合一个函数
#    函数的参数包括自变量和系数
# 2. 利用scipy.optimize提供的curve_fit函数进行拟合
#    三个参数分别为拟合的函数，自变量，数据点
#    返回的两个结果分别为拟合后的参数和误差
# 3. curve_fit函数还可以对与拟合的参数进行范围限制。限制的参数为bounds=(down, up)，down和up为两个列表，列表长度均与拟合参数数量一致。分别表示上限和下限。


#Header
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

#Define a function(here a exponential function is used)
def func(x, a, b, c):
    return a * np.exp(-b * x) + c

#Create the data to be fit with some noise
xdata = np.linspace(0, 4, 50)
y = func(xdata, 2.5, 1.3, 0.5)
np.random.seed(1729)
y_noise = 0.2 * np.random.normal(size=xdata.size)
ydata = y + y_noise
plt.plot(xdata, ydata, 'bo', label='data')

#Fit for the parameters a, b, c of the function func:
popt, pcov = curve_fit(func, xdata, ydata)
print(popt) #output: array([ 2.55423706, 1.35190947, 0.47450618])
print(pcov)
plt.plot(xdata, func(xdata, *popt), 'r-',
 label='fit: a=%5.3f, b=%5.3f, c=%5.3f' % tuple(popt))

#In the case of parameters a,b,c need be constrainted
#Constrain the optimization to the region of
#0 <= a <= 3, 0 <= b <= 1 and 0 <= c <= 0.5
popt, pcov = curve_fit(func, xdata, ydata, bounds=(0, [3., 1., 0.5]))
popt #output: array([ 2.43708906, 1. , 0.35015434])
plt.plot(xdata, func(xdata, *popt), 'g--',
 label='fit: a=%5.3f, b=%5.3f, c=%5.3f' % tuple(popt))

#Labels
plt.title("Exponential Function Fitting")
plt.xlabel('x coordinate')
plt.ylabel('y coordinate')
plt.legend()
leg = plt.legend()  # remove the frame of Legend, personal choice
leg.get_frame().set_linewidth(0.0) # remove the frame of Legend, personal choice
#leg.get_frame().set_edgecolor('b') # change the color of Legend frame
plt.show()

