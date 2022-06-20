# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# > Author     : lunar
# > Email       : lunar_ubuntu@qq.com
# > Create Time: Wed 02 Sep 2020 06:11:50 PM CST

# 牛顿法求解极值问题
# 例题: min f(x) = x_1^4 + 25x_2^4 + x_1^2x_2^2

import numpy as np

def derivation(x):
    f = x[0][0]**4 + 25*x[1][0]**4 + x[0][0]**2 * x[1][0]**2
    df = np.array([[4*x[0][0]**3 + 2*x[0][0]*x[1][0]**2], [100*x[1][0] + 2*x[0][0]**2*x[1][0]]])
    ddf = np.array([[12*x[0][0]**2 + 2*x[1][0]**2, 4*x[0][0]*x[1][0]],
        [4*x[0][0]*x[1][0], 300*x[1][0]**2 + 2*x[0][0]**2]
        ])
    return [f, df, ddf]

def main():
    x = np.array([[2],[2]], dtype=np.float)
    [f0, df, ddf] = derivation(x)
    while np.linalg.norm(df) > 0.001: # 计算矩阵范数, 暂时不懂范数啥意思
        p = -np.linalg.inv(ddf).dot(df)
        x += p
        [f0, df, ddf] = derivation(x)
    return x, f0

if __name__ == '__main__':
    x, f0 = main()
    print("最优解: ", x)
    print("最优值: ", f0)

