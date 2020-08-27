# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# > Author     : lunar
# > Email       : lunar_ubuntu@qq.com
# > Create Time: Thu 27 Aug 2020 05:41:41 PM CST

# 使用Python求解线性规划问题
# python Scipy数学库已经实现了线性规划的函数
# 使用方法与 MATLAB 并无不同

from scipy import optimize
import numpy as np

c = np.array([-1,-1]) # c表示目标函数系数
A = np.array([[1, 9/14], [-2, 1]]) # 约束方程组的系数矩阵
b = np.array([51/14, 1/3]) # 约束值向量

res = optimize.linprog(c, A, b)

# 最终输出结果只需要关注第一个和最后一个
# 第一个表示最优值，最后一个表示最优解
print(res)
