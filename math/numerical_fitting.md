---
author: lunar
date: Fri 21 Aug 2020 04:06:01 PM CST
---

### MATLAB数据拟合

#### 线性最小二乘法

数据拟合又叫曲线拟合，已知一组（二维）数据，即平面上的n个点，寻求一个函数$y=f(x)$，使得$f(x)$在某种准则下与所有数据点最为接近，则曲线拟合得最好。

线性最小二乘法是解决曲线拟合最常用的方法，拟合准则是使得所有数据点与拟合曲线的距离的平方和最小，称为最小二乘准则。

令
$$
f(x) = a_1r_1(x) + a_2r_2(x) + \cdots + a_mr_m(x)
$$

记
$$
J(a_1, \cdots, a_m) = \sum_{i=1}^n\delta^2_i = \sum_{i=1}^n[f(x_i) - y_i]^2
$$

求$J(a_1,\cdots,a_m)$的最小值就是使得J对于任何$a_i$求导都等于0

则有
$$
\sum_{i=1}^nr_j(x_i)[\sum_{k=1}^ma_kr_k(x_i) - y_i] = 0,\quad (j=1,\cdots,m)
$$
即
$$
\sum_{k=1}^na_k[\sum_{i=1}^nr_j(x_j)r_k(x_i)] = \sum_{i=1}^nr_j(x_i)y_i,\quad (j=1,\cdots,m) \tag{13}
$$

记
$$
R = \begin{bmatrix}
r_1(x_1) & \dots & r_m(x_1)\\
\vdots & \vdots & \vdots\\
r_1(x_n) & \dots & r_m(x_n)
\end{bmatrix}_{n\times m}\\
A = [a_1,\dots, a_m]^T, Y = (y_1,\dots,y_n)^T \tag{14}
$$

则方程组13可以表示为
$$
R^TRA = R^TY
$$
当${r_1(x),\dots,r_m(x)}$线性无关时，R列满秩，于是方程组14有唯一解
$$
A = (R^TR)^{-1}R^TY
$$

#### 函数$r_k(x)$的选取

函数$r_k(x)$的选取至关重要。

可以通过作图$(x_i,y_i)，直观地判断应该用怎样的曲线去作图

#### MATLAB实现


