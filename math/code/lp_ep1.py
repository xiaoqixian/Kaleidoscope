# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# > Author     : lunar
# > Email       : lunar_ubuntu@qq.com
# > Create Time: Thu 27 Aug 2020 06:09:21 PM CST

# 整数规划例题1

import numpy as np
from scipy import optimize

# 使用蒙特卡罗法进行整数规划的求解
def mente(x):
    f = -x[0] - x[1]
    g = np.array([x[0] + 9/14*x[1] - 51/14,
            -2*x[0] + x[1] - 1/3
        ])
    return f,g

def main():
    res = 1000
    for i in range(100000):
        x = np.random.rand(2)
        x1 = np.ceil(x)
        x2 = np.floor(x)
        f,g = mente(x1)
        if res > f and np.sum(g <= 0) == 2:
            res = f
            x0 = x1
        f,g = mente(x2)
        if res > f and np.sum(g <= 0) == 2:
            res = f
            x0 = x2
    return res,x0

# 分枝定界法
# 先使用线性规划求出一个最优解
# 任选一个非整数变量，作为分枝的标准
# 然后分成两个整数规划问题进行求解
# 用递归比较好做
def branch():
    c = np.array([-1,-1])
    A = np.array([[1,9/14], [-2, 1]])
    b = np.array([51/14, 1/3])
    global f
    f = 1000
    global x0
    x0 = None
    global traverse_times
    traverse_times = 0
    traverse(c, A, b, 0)
    return f, x0

def traverse(c, A, b, times):
    res = optimize.linprog(c, A, b)
    print()
    print("第", times, "次递归")
    print("线性规划解: ")
    print(res)
    # 如果没有可行解,直接返回
    if not res.success:
        print("本次线性规划无可行解")
        return
    global f,x0, traverse_times
    if res.fun > f:
        # 失去希望的分支
        return
    for i in range(res.x.size):
        x = res.x[i]
        if 0.01 < x % 1 < 0.99: # 因为会有轻微的精度影响，所以不能写余数为0
            print("b向量: ", b)
            print("系数矩阵A: ", A)
            print("------")
            # 向下取整
            x1 = np.floor(x)
            # 向上取整
            x2 = np.ceil(x)
            print("分支: x%d <= %d or x%d >= %d" % (i+1, x1, i+1, x2))
            # 给系数矩阵扩容
            A.resize((A.shape[0]+1, A.shape[1]), refcheck=False)
            new_constraint = np.zeros(A.shape[1])
            new_constraint[i] = 1.0
            A[-1] = new_constraint

            # 给b扩容
            b.resize(b.size+1, refcheck=False)
            b[-1] = x1
            traverse(c, A, b, times+1)
            A.resize((A.shape[0]-1, A.shape[1]), refcheck=False)
            b.resize(b.size-1, refcheck=False)

            A.resize((A.shape[0]+1, A.shape[1]), refcheck=False)
            new_constraint = np.zeros(A.shape[1])
            new_constraint[i] = -1.0
            A[-1] = new_constraint
            b.resize(b.size + 1, refcheck=False)
            b[-1] = -x2
            traverse(c, A, b, times+1)
            A.resize((A.shape[0]-1, A.shape[1]), refcheck=False)
            b.resize(b.size-1, refcheck=False)

            return
    # 说明已达到整数解
    print("找到一个当前最优整数解: ", res.x)
    f = res.fun
    x0 = res.x

if __name__ == '__main__':
    res, x0 = branch()
    print("-------")
    print("最终结果: ")
    print("最优值: ", res)
    print("最优解: ", x0)
