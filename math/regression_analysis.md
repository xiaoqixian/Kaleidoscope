---
author: lunar
date: Wed 26 Aug 2020 10:46:04 AM CST
---

## 回归分析

回归分析是对拟合问题作的一个统计分析。

具体来说，回归分析在一组数据的基础上研究这样几个问题：
1. 建立因变量y与自变量$x_1,x_2,\dots,x_m$之间的回归模型;
2. 对回归模型的可信度进行检验;
3. 判断每个变量$x_i$对y的影响是否显著;
4. 诊断回归模型是否适合这组数据;
5. 利用回归模型对y进行预报或控制;

在正式学习回归分析之前需要先学习一下协方差的概念

#### 协方差

在统计学中，方差是用来度量单个随机变量的离散程度，而协方差则一般用来刻画两个随机变量的相似程度。

方差的计算公式为
$$
a_x^2 = \frac1{n-1}\sum_{i=1}^n(x_i-\overline x)^2
$$

而协方差的计算公式为
$$
\delta(x,y) = \frac1{n-1}\sum_{i=1}^n(x_i-\overline x)(y_i-\overline y)
$$

易知方差为协方差的两个变量相同时的特殊情况。

对于具有n个随机变量的样本。我们可以将两两之间的协方差表示为一个协方差矩阵
$$
\Sigma = \begin{pmatrix}
\delta(x_1,x_1) & \dots & \delta(x_1,x_d)\\
\vdots & \ddots & \vdots\\
\delta(x_d, x_1) & \dots & \delta(x_d,x_d)
\end{pmatrix} \in \R^{d\times d}
$$

#### 样本空间

如果有m个变量，对它们分别进行了n次采样，得到n个样本点

一个样本点可表示为$e_i = (x_{i1}, x_{i2},\dots,x_{im})^T$, $e_i$被称为第i个样本点。

则样本协方差矩阵及样本相关系数矩阵分别为
$$
C_1 = (t_{ij})_{m\times m} \frac1{n-1}\sum_{k=1}^n(e_k - \overline x)(e_k - \overline x)^T\\
C_2 = (r_{ij})_{m\times m} = \left(\frac{t_{ij}}{\sqrt{t_{ii}t_{jj}}} \right)
$$

$t_{ij}$即表示变量i和j的协方差

#### 数据的标准化处理

**数据的中心化处理**

即通过平移变化使得样本的均值变为0而不改变样本之间的相对位置

$$
x^*_{ij} = x_{ij} - \overline x_j, i = 1,2,\dots,n; j = 1,2,\dots,m
$$

**数据的无量纲化处理**

数据分析中常用的消除量纲的方法，是对不同的变量进行所谓的压缩处理，即使每个变量的方差均变成1
$$
x^*_{ij} = x_{ij} / s_j\\
s_j = \sqrt{\frac1{n-1}\sum_{i=1}^n(x_{ij}-\overline x_j)^2}
$$

$s_j$即为标准差

### 一元线性回归

一元线性回归的模型为
$$
y = \beta_0 + \beta_1 x + \varepsilon
$$

$\beta_0$和$\beta_1$为回归系数，$\varepsilon$是随机误差项，总是假设$\varepsilon ~ N(0, \delta^2)$

#### 最小二乘法估计回归系数

当n个自变量与因变量的观测值符合线性回归模型时，需要对两个回归系数进行估计。

记
$$
Q(\beta_0, \beta_1) = \sum_{i=1}^n(y_i - \beta_0 - \beta_1x_i)^2
$$
求一组估计值$\hat{\beta_0},\hat{\beta_1}$使得
$$
Q(\hat{\beta_0},\hat{\beta_1}) = \min Q(\beta_0,\beta_1)
$$

分别求导=0可得
$$
\begin{cases}
\hat{\beta_1} = \frac{\sum_{i=1}^n(x_i-\overline x)(y_i-\overline y)}{\sum_{i=1}^n(x+i - \overline x)^2}\\
\hat{\beta_0} = \overline y - \hat{\beta_1}\overline x
\end{cases}
$$

#### 其它性质

用最小二乘法拟合的回归方程还有一些值得注意的性质：
1. 残差和为零
2. 你何止$\hat y_i$的平均值等于观测值$y_i$的平均值
3. 最小二乘回归线总是通过观测数据的中心$(\overline x,\overline y)$

### 拟合效果分析

#### 残差的样本方差

残差
$$
e_i = y_i - \hat{y}_i, i = 1,2,\dots,n
$$

一个好的拟合方程，其残差总和应该越小越好。

残差的离散范围越小，拟合的模型就越准确。


