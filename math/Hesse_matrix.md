---
author: lunar
date: Wed 02 Sep 2020 10:52:12 AM CST
---

## 黑塞矩阵(Hessian Matrix)

黑塞矩阵是一个多元函数的**二阶偏导数**构成的方阵, 描述了函数的**局部曲率**.

黑塞矩阵常用语[牛顿法](non_linear_programming.md)解决优化问题, 利用黑塞矩阵可判定多元函数的极值问题. 在实际工程问题的优化设计中, 所列的目标函数往往很复杂, 为了使问题简化, 常常将目标函数在某点邻域展开成泰勒多项式来逼近原函数, 此时函数在某点泰勒展开式的矩阵形式中会设计到黑塞矩阵.

二维函数$f(x_1, x_2)$在$X^{(0)}(x_1^{(0)}, x_2^{(0)})$处的泰勒展开式为
$$
\begin{aligned}
f(x_1, x_2) = &f(x_1^{(0)}, x_2^{(0)}) + \frac{\partial f}{\partial x_1}\Delta x_1 + \frac{\partial f}{\partial x_2}\Delta x_2 +\\ &\frac12\left[\frac{\partial^2 f}{\partial x_1^2}\Delta x_1^2 + 2\frac{\partial^2 f}{\partial x_1\partial x_2}\Delta x_1\Delta x_2 + \frac{\partial^2 f}{\partial x_2^2}\Delta x_2^2 \right] + \dots
\end{aligned}
$$

表示成矩阵形式即为
$$
f(X) = f(X^0) + \begin{pmatrix}\frac{\partial f}{\partial x_1}&\frac{\partial f}{\partial x_2}\end{pmatrix} \begin{pmatrix}\Delta x_1\\\Delta x_2\end{pmatrix} + \frac12\begin{pmatrix}\Delta x_1&\Delta x_2\end{pmatrix}\begin{pmatrix}\frac{\partial^2 f}{\partial x_1^2} & \frac{\partial^2 f}{\partial x_1\partial x_2}\\ \frac{\partial^2 f}{\partial x_1\partial x_2} & \frac{\partial^2 f}{\partial x_2^2}\end{pmatrix}\begin{pmatrix}\Delta x_1\\ \Delta x_2\end{pmatrix} + \dots
$$

其中, 记
$$
G(X^{(0)}) = \begin{pmatrix}\frac{\partial^2 f}{\partial x_1^2} & \frac{\partial^2    f}{\partial x_1\partial x_2}\\ \frac{\partial^2 f}{\partial x_1\partial x_2} & \frac{\partial^2 f}{\partial x_2^2}\end{pmatrix}
$$

$G(X^{(0)})$即为$f(x_1,x_2)$在$X^{(0)}$处的黑塞矩阵.

将结论扩展到多元函数:
1. $\nabla f(X^{(0)}) = \left[\frac{\partial f}{\partial x_1}, \frac{\partial f}{\partial x_2},\dots,\frac{\partial f}{\partial x_n}\right]$, 为$f(X)$在$X^{(0)}$处的**梯度**.
2. $G(X^{(0)}) = \begin{bmatrix}\frac{\partial^2 f}{\partial x_1^2} & \frac{\partial^2 f}{\partial x_1\partial x_2} & \dots & \frac{\partial^2 f}{\partial x_1\partial x_n}\\ \frac{\partial^2 f}{\partial x_2\partial x_1} & \frac{\partial^2 f}{\partial x^2_2} & \dots & \frac{\partial^2 f}{\partial x_2\partial x_n} \\ \vdots & \vdots && \ddots && \vdots\\ \frac{\partial^2 f}{\partial x_n\partial x_1} & \frac{\partial^2 f}{\partial x_n\partial x_2} & \dots & \frac{\partial^2 f}{\partial x_n^2}\end{bmatrix}_{X^{(0)}}$ 为函数$f(X)$在$X^{(0)}$处的**黑塞矩阵**.

### 利用黑塞矩阵判断多元函数的极值

当多元函数$f(x_1, x_2, \dots, x_n)$在点$M_0(a_1, a_2, \dots, a_n)$的邻域内存在连续二阶偏导数且满足:
$$
\left.\frac{\partial f}{\partial x_j}\right|_{(a_1,a_2,\dots,a_n)} = 0, j = 1,2,\dots, n
$$

且有

$$
A = \begin{bmatrix}\frac{\partial^2 f}{\partial x_1^2} & \frac{\partial^2 f}{\partial x_1\partial x_2} & \dots & \frac{\partial^2 f}{\partial x_1\partial x_n}\\ \frac{\partial^2 f}{\partial x_2\partial x_1} & \frac{\partial^2 f}{\partial x^2_2} & \dots & \frac{\partial^2 f}{\partial x_2\partial x_n} \\ \vdots & \vdots & \ddots & \vdots\\ \frac{\partial^2 f}{\partial x_n\partial x_1} & \frac{\partial^2 f}{\partial x_n\partial x_2} & \dots & \frac{\partial^2 f}{\partial x_n^2}\end{bmatrix}_{X^{(0)}}
$$

则有
1. 当A为[正定矩阵](positive_definite_matrix.md)时, f在$M_0$为极小值;
2. 当A为负定矩阵时, f在$M_0$存在极大值;
3. 当A为[不定矩阵](https://baike.baidu.com/item/%E4%B8%8D%E5%AE%9A%E7%9F%A9%E9%98%B5)时, $M_0$不是极值点.
4. 当A为[半正定矩阵](https://baike.baidu.com/item/%E5%8D%8A%E6%AD%A3%E5%AE%9A%E7%9F%A9%E9%98%B5)或半负定矩阵时, $M_0$是"可疑"极值点.


