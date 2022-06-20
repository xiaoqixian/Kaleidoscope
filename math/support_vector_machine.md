---
author: lunar
date: Mon 07 Sep 2020 07:09:54 PM CST
---

## 支持向量机(Support Vector Machine, SVM)

支持向量机是数据挖掘中的一项新技术, 是借助于最优化方法来解决机器学习问题的新工具.

### 支持向量机的基本原理

根据给定的训练集
$$
T = \{(x_1,y_1),(x_2,y_2),\cdots,(x_i,y_i)\} \in (X\times Y)^i
$$

其中$x_i\in X=R^n$为输入空间, 输入空间的每一个点都由n个属性值组成, $y_i\in T = \{-1,1\},i=1,\cdots,l$. 寻找$R^n$上的一个实值函数$g(x)$, 以便用分类函数
$$
f(x) = \sgn(g(x))
$$

推断任意一个模式$x$相对应$y$值的问题为分类问题.

#### 线性可支持向量分类机

对于训练集T, 使得存在$\omega\in R^n, b\in R, \varepsilon\in R^+$, 对于所有使得$y_i = 1$的下标i有$(\omega\cdot x_i) + b\ge \varepsilon$, 而对于所有使得$y_i = -1$的下标i有$(\omega\cdot x_i)+b\le -\varepsilon$. 则称相应的分类问题是**线性可分**的.

太难了, 学不下去了.
