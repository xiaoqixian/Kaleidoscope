---
author: lunar
date: Sat 05 Sep 2020 11:50:41 AM CST
---

## 微分方程的解法

### 微分方程的线性与非线性, 齐次与非齐次

线性与齐次这两个词经常被各种组合用来描述微分方程的特征. 那么它们表示方程的什么性质呢?

#### 齐次与非齐次

齐次方程很好理解, 对于一个微分方程, 如果可以用$v = \frac yx$代替方程内所有的x和y, 则该方程为**齐次方程.**

齐次微分方程的特点就是其右端项是以$\frac yx$为变元的连续函数.

齐次微分方程一般可通过变量代换, 化为可分离变量微分方程来求解.

#### 线性与非线性

在线性代数中有一个**线性变换**的概念. 当变换D满足以下条件时, 为一个线性变换:
- 可加性: $D(f(x) + g(x)) = D(f(x)) + D(g(x))$
- 齐次性: $D(a(f)) = aD(f(x))

进一步的, D的多项式组合或者说线性组合, 也是一种线性变换.

对于微分方程来说, 如果$y, y^{'}, y^{''},\cdots$都是一次的, 则为线性微分方程.

通常一阶线性微分方程的通式为:
$$
y^{'} + p(x)y + q(x) = 0
$$

### 一阶微分方程解法

一阶微分方程可以分为以下几类:
1. 可分离变量方程 Separable Equations
2. 齐次方程 Homogeneous Equations
3. 恰当方程 Exact Equations
4. 线性方程 Linear Equations
5. 伯努利方程 Bernoulli Equations

#### 1. 可分离变量方程 Separable Equations

基本形式为
$$
M(x)dx + N(y)dy = 0\tag{1}
$$

直接两端积分得
$$
\int M(x)dx + \int N(y)dy = C\tag{2}
$$

#### 2. 齐次方程 Homogeneous Equations

齐次微分方程的基本形式为
$$
\frac{dy}{dx} = f(x,y)\tag{3}
$$

所谓齐次方程, 应满足下面这个性质:
$$
f(tx, ty) = f(x,y)\tag{4}
$$

则令$y = vx$, 可以将其转化为可分离变量的微分方程而求得$v$, 从而求得$y$.

#### 3. 恰当方程 Exact Equations

对于下列形式的微分方程:
$$
M(x, y)dx + N(x,y)dy = 0\tag{5}
$$

则最后要确定的函数满足
$$
dg(x,y) = M(x,y)dx + N(x,y)dy\tag{6}
$$

如果M和N都是连续函数且在xy平面上具有一阶连续偏导, 则下式成立时原方程为恰当方程:
$$
\frac{\partial M(x,y)}{\partial y} = \frac{\partial N(x,y)}{\partial x}\tag{7}
$$

#### 4. 线性微分方程 Linear Equations

一阶线性微分方程具有下列形式:
$$
y^{'} + p(x)y = q(x) \tag{8}
$$

一种方式是直接将$y$构造为两个关于$x$的函数: $y = u\cdot v$

直接给出结果为
$$
y = u\cdot v = \left[\int e^{(\int P(x)dx)}\cdot Q(x)\cdot dx + C \right]\cdot e^{(-\int P(x)dx)}
$$
