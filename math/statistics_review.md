---
author: lunar
date: Tue 08 Sep 2020 11:11:21 PM CST
---

# 大学概率论复习

> 为了一次数学建模啊, 大学高数, 线性代数, 概率论都得复习一遍. 不过没关系, 反正考研得再复习一遍.

## 随机事件与概率

第一章挺好懂, 就两个公式记一下. 条件概率什么的简单.

全概率公式:
$$
P(B) = \sum_{i=1}^nP(A_i)P(B|A_i);
$$

表示某一个事件发生的概率等于所有与之相关的事件发生的条件概率之和.

贝叶斯公式:
$$
P(A_i|B) = \frac{P(A_i)P(B|A_i)}{sum_{j=1}^nP(A_j)P(B|A_j)}, i = 1,\cdots,n
$$

我们发现分子其实就是$P(A_i)P(B)$, 分母利用全概率公式其实就是$P(B)$. 所以贝叶斯公式其实就是一个条件概率计算公式的简单代换. 

利用贝叶斯公式我们可以根据在多种A情况下B发生的概率, 来计算已知B发生后具体属于A中的哪个情况的概率. 在机器学习经常用来做分类问题. 因为分类就是告诉程序哪一类都具有哪些特征, 然后经过训练之后判断具有某个特征的事物属于哪一类.

## 离散型随机变量及其分布

**定义**: 将随机变量X的取值映射到其发生概率上的函数称为**概率函数**. 概率函数也常称为该随机变量的**分布**. 后者更用的多一点.

### 常见的离散型随机变量

#### 二项分布

在n次贝努利实验中, 发生n次事件A的概率.
$$
P(x = k) = \begin{pmatrix}n\\k\end{pmatrix}p^k(1-p)^{n-k}
$$

记作$X~B(n, p)$

#### 超几何分布

在N件商品中有M件不合格品, 从中随机抽取n件进行检查,发现有X件不合格品的概率
$$
P(X = k) = \frac{\begin{pmatrix}M\\k\end{pmatrix}\begin{pmatrix}N-M\\n-k\end{pmatrix}}{\begin{pmatrix}N\\n\end{pmatrix}}, k = 0,1,\cdots,n.
$$

相较于贝努利实验属于不放回抽样.

#### 泊松分布

记$\lambda = np_n$

$$
\lim_{n\rightarrow\infty}\begin{pmatrix}n\\k\end{pmatrix}p_n^k(1-p_n)^{n-k} = e^{-\lambda}\cdot \frac{\lambda^k}{k!}
$$

称随机变量X服从参数为$\lambda$的泊松分布, $X~P(\lambda)$

#### 几何分布

不停地进行贝努利实验, 直到得到想要的结果.

### 二维随机变量及其分布

本质上是每个样本点与一对有序实数之间的对应关系.

### 随机分布的独立性与条件分布

如果两个随机变量同时发生某个事件的概率等于分别发生的概率之积, 则称这两个随机变量**相互独立**.

相互独立的两个分布具有**可加性**.

## 连续型随机变量及其分布

定义
$$
F(x) = P(X\le x),-\infty < x < \infty
$$
为随机变量X的**分布函数**.

定义
$$
F(x,y) = P(X\le x, Y\le y)
$$
为X与Y的**联合分布函数**.

### 概率密度函数

$$
F(x) = \int_{-\infty}^xf(t)dt
$$

### 常用连续型随机分布

#### 指数分布

如果密度函数满足
$$
f(x) = \begin{cases} \lambda e^{-\lambda x},x>0\\0, 其余\end{cases}
$$
称为指数分布.
记作$X~E(\lambda)$

#### 正态分布

密度函数满足
$$
f(x) = \frac1{\sqrt{2\pi}\sigma}e^{-\frac{(x-\mu)^2}{2\sigma^2}}
$$

非标准正态分布与标准正态分布之间存在于一个重要的转换公式:
$$
F(x) = \Phi(\frac{x-\mu}\sigma)
$$

然后通过查标准正态分布的表就可以求得非标准正态分布的值.

#### 二维随机变量正态分布

$(X,Y)~N(\mu_1,\mu_2,\sigma_1^2,\sigma_2^2,\rho)$

X和Y相互独立的充要条件为$\rho=0$

### 二维随机变量的密度函数

重点讨论$Z = X+Y$的情况.

#### 卷积公式

当X与Y相互独立时, 有
$$
f_Z(z) = \int_{-\infty}^{\infty}f_X(x)f_Y(z-x)dx
$$

### 正态分布的可加性

设X与Y相互独立, $X+Y ~ N(\mu_1+\mu_2, \sigma_1^2+\sigma_2^2)$

## 随机变量的数字特征

### 数学期望

期望与我们一般说的样本均值不一致, 这一点在后面样本抽查时尤为重要.

对于一个离散型随机变量, 其**所有**可能的值乘以相应的概率等于期望. 而样本中所有数据的算术平均值只能叫做样本均值. 因为样本中每个数据发生的概率可以近似看做在样本中出现的频率.

对于连续型随机变量, 数学期望为
$$
E(X) = \int_{-\infty}^{\infty}xf(x)dx
$$

### 常见随机分布的数学期望

#### 二项分布

$$
E(X) = \sum_{k=0}^nk\begin{pmatrix}n\\k\end{pmatrix}p^k(1-p)^{n-k} = np
$$

#### 泊松分布

$$
E(X) = \sum_{k=0}^\infty ke^{-\lambda}\frac{\lambda^k}{k!} = \lambda
$$

#### 指数分布

$$
E(X) = \int_0^\infty x\lambda e^{-\lambda x}dx = \frac1{\lambda}
$$

### 期望计算的线性性质

期望具有线性函数的性质.

当X和Y相互独立时, $E(XY) = E(X) + E(Y)$

### 方差与标准差

我们将随机变量X与其期望$E(X)$的平方差看做一个新的随机变量, 该随机变量的期望被定义为**方差**.

即X的方差
$$
D(X) = E\{[X - E(X)]^2\} = E(X^2) - [E(X)]^2
$$

#### 方差的性质

- $D(kX + c) = k^2D(X)$
- $D(X \pm Y) = D(X) + D(Y) \pm 2E\{[X-E(X)][Y - E(Y)]\}$
- when X and Y are independent, $D(X\pm Y) = D(X) + D(Y)$

#### 中心化随机变量与标准化随机变量

### 协方差与相关系数

**定义**
$$
cov(X,Y) = E\{[X-E(X)][Y-E(Y)]\} = E(XY) - E(X)E(Y)
$$
为X与Y的**协方差**.

**定义**
$$
\rho(X,Y) = \frac{cov(X,Y)}{\sqrt{D(X)D(Y)}}
$$
为X与Y的**相关系数**.

当$|\rho(X,Y)| = 1$时, 表明X与Y**线性相关**. The smaller the absolute value of the **coreleation coefficient** of X and Y, the less releavant X and Y are.

### 矩与协方差矩阵

$E(X^k)$为X的k阶**原点矩**.

#### 重要结论

若$X~N(0,1)$
$$
E(X^k) = \begin{cases}(k-1)(k-3)\cdots1,当k是偶数\\
0, 当k是奇数
\end{cases}
$$

#### 变异系数

在工程技术中, 常使用**变异系数**来消除不同量纲带来的影响.

$$
\delta_X = \frac{\sqrt{D(X)}}{|E(X)|}
$$

### 两个重要不等式

#### 切比雪夫不等式

设X是任意一个随机变量, $E(X) = \mu, D(X) = \sigma^2$, 对任意一个$\varepsilon > 0$. 存在
$$
P(|X - \mu| \ge \varepsilon) \le \frac{\sigma^2}{\varepsilon^2}
$$

这个不等式表述了服从某个分布的随机变量的值出现在区间$[\mu-\varepsilon,\mu+\varepsilon]$区间之外的概率可以控制在什么范围内.

通过该不等式同样可以推出$3\sigma$准则.

#### 柯西-许瓦兹不等式

$$
[E(XY)]^2 \le E(X^2)E(Y^2)
$$

根据判别式小于等于0得来.

## 5. 随机变量序列的极限

### 5.1 大数定律

我们对随机变量序列引入**收敛性**的定义.

如果存在一个常数c, 使得对任意一个$\varepsilon > 0$, 总有
$$
\lim_{n\rightarrow\infty}P(|X_n-c| < \varepsilon) = 1
$$
则称该随机序列**依概率收敛**于c, $X_n\stackrel{P}{\rightarrow} c$.

使得频率的稳定性有了严谨的数学描述.

#### 切比雪夫大数定律

设$X_1,X_2,\cdots,X_n$是**两两不相关**的随机变量序列, 如果存在常数c, 使得$D(X)\le c$, 则有
$$
\frac1n\sum_{i=1}^nX_i-\frac1n\sum_{i-1}^nE(X_i) \stackrel{P}{\longrightarrow}0.
$$
只要方差有穷, 则根据切比雪夫不等式右侧等于0.

#### 独立同分布情形下的大数定律

用语言表述一下: 独立同分布的随机变量序列依概率收敛于数学期望.

### 5.2 中心极限定理

人们在长期实践中发现, 只要n足够大, 对于任意分布, 总是可以认为$\sum_{i=1}^nX_i$近似地服从正态分布. 关于这方面的结论被称为**中心极限定理**.

$\Phi(x)$是$N(0,1)$的分布函数.

则有
$$
\lim_{n\rightarrow\infty}P\left(\frac{\sum_{i=1}^nX_i - n\mu}{\sqrt n\sigma}\le x \right) = \Phi(x)\\
\sum_{i=1}^nX_i \thicksim N(n\mu, n\sigma^2)
$$
应用场景: 若$X_i$表示每次测量的误差, $\sum_{i=1}^nX_i$表示最终的总误差. 在测量次数足够多的情况下, 可以认为总误差服从正态分布. 则根据中心极限定理计算出总误差保持在某个范围内的概率, 从而判断测量结果可不可信.

## 6. 现代概率论简介

未学

## 7. 数理统计

### 统计量

样本方差 
$$
S^2 = \frac1{n-1}\sum_{i-1}^n(X_i-\overline X)^2
$$
为什么分母变成了n-1可以看一下这篇[文章](https://www.matongxue.com/madocs/607/).

这篇文章主要解释了两点:

- 为什么可以用样本的方差来近似随机变量的方差?
- 为什么分母变成了n-1?

对于第一个问题, 可以求得 $E[\frac1n\sum_{i=1}^n(X_i-\mu)^2] = \sigma^2$, 利用中心极限定理得 $S^2$会服从$\mu = \sigma^2$的正态分布, 所以可以将$S^2$ 作为 $\sigma^2$ 的无偏估计.

对于第二个问题, 可以计算得
$$
E[S^2] = \sigma^2 - E[(\overline X - \mu)^2]\\
E[(\overline X - \mu)^2] = \frac1n\sigma^2
$$
所以相当于样本低估了$\frac1n\sigma^2$

#### 定理

- $E(\overline X) = \mu, D(\overline X) = \frac{\sigma^2}n$
- $E(S^2) = \sigma^2, E(S^2_n) = \frac{n-1}n\sigma^2$

### 三个常用分布

#### 卡方分布

$X\sim N(0,1)$, 称随机变量
$$
Y = \sum_{i=1}^nX_i^2
$$
为服从自由度为n的$\chi^2$分布, 记作$Y\sim \chi^2(n)$
$$
E(Y) = n, D(Y) = 2n
$$
卡方分布具有可加性.

#### t分布

$X\sim N(0,1), Y\sim\chi^2(n)$ 
$$
T = \frac{X}{\sqrt{\frac Yn}}
$$
$T\sim t(n)$

t分布的密度函数是**偶函数**, 且当$n \ge 2$时, $E(T) = 0$.

#### F分布

X与Y相互独立, $X\sim\chi^2(m), Y\sim\chi^2(n)$.
$$
F = \frac{\frac Xm}{\frac Yn}
$$
$F\sim F(m,n)$
$$
F\sim F(m,n)\Rightarrow \frac1F\sim F(n,m)
$$
