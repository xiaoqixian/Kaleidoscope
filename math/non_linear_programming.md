---
author: lunar
date: Tue 01 Sep 2020 04:31:18 PM CST
---

## 非线性规划

如果目标函数中包含非线性函数, 就称这种规划问题为非线性规划问题.

目前解决非线性规划还没有一种通用方法.

#### 线性规划和非线性规划的区别

如果线性规划的最优解存在, 其最优解只能在其可行域的边界上达到(特别是可行域的顶点上达到); 而非线性规划的最优解**可能在可行域的任意一点达到**.

### 非线性规划的MATLAB解法

首先可以将非线性规划表示为如下形式:
$$
\min f(x)\\
\begin{cases}
Ax\le B\\
Aeq\dot x = Beq\\
C(x) \le 0\\
Ceq(x) = 0
\end{cases}
$$

C(x), Ceq(x)是非线性向量函数.

MATLAB计算非线性规划的函数为
`x = fmincon(fun, x0, A, B, Aeq, Beq, LB, UB, NONLCON, OPTIONS)`

`fun`是用.m文件定义的目标函数; x0表示决策变量的初始值; NONLCON是用.m文件定义的非线性向量函数; OPTIONS定义了优化参数; 其余参数与线性规划一致.

#### 示例

求解下列非线性规划问题
$$
\min f(x) = x_1^2 + x_2^2 + x_3^2 + 8\\
\begin{aligned}
s.t.\quad &x_1^2 - x_2 + x_3^2 \ge 0\\
&x_1 + x_2^2 + x_3^2 \le 20\\
-x_1 - x_2^2 + 2 = 0\\
x_2 + 2x_3^2 = 3\\
x_1, x_2, x_3 \ge 0
\end{aligned}
$$

用MATLAB代码求解为

编写目标函数的.m文件target.m
```matlab
function f = target(x);
f = sum(x.^2) + 8;
```

编写非线性约束条件的.m文件nonlinear.m
```matlab
function [g,h] = nonlinear(x);
g = [-x(1)^2 + x(2) - x(3)^2 
     x(1) + x(2)^2 + x(3)^3 - 20
    ]; %非线性不等式约束
f = [
     -x(1) - x(2)^2 + 2 
     x(2) + 2x(3)^2 - 3
    ]; %非线性等式约束
```

主程序文件main.m
```matlab
options = optimset('largescale', 'off');
[x, y] = fmincon('target', rand(3,1), [], [], [], [], zeros(3,1),[], 'nonlinear', options)
```

### 求解非线性规划的基本迭代格式(难点)

由于线性规划的目标函数为线性函数, 可行域为凸集, 所以求出的最优解就是整个可行域上的最优解. 非线性规划则不然, 有时求出的解虽然是一部分可行域上的极值点, 但不一定是整个可行域上的全局最优解.

对于非线性规划模型(NP), 可以采用迭代方法求最优解. 基本思想为: 从一个选定的初始点出发, 按照一个特定的迭代规则产生一个点列{x^k^}; 使得当{x^k^}是有穷点列时, 其最后一个点是(NP)的最优解; 为无穷点列时, 它有极限点, 并且极限点是(NP)的最优解;

设$x^k\in R^n$是某迭代方法的第k轮迭代点, $x^{k+1}\in R^n$是第n+1轮迭代点, 记
$$
x^{k+1} = x^k + t_kp^k\\
t_k\in R^1, p^k\in R^n, \lvert p^k\rvert = 1
$$

通常将基本迭代格式中的$p^k$称为第k轮搜索方向, $t_k$为沿$p^k$方向的步长. 有机器学习那味儿了.

对于向量p, 如果存在$t\in (0, +\infty)$使得
$$
f(\overline x + tp) < f(\overline x)\\
\overline x + tp \in K
$$

K即为可行域, 则称p为$\overline x$关于K的可行方向.

### 凸函数, 凸规划

凸函数的定义为: 若对区间(0,1)内的任何实数$\alpha$, 恒有
$$
f(\alpha x_1 + (1-\alpha)x_2) \le \alpha f(x_1) + (1-\alpha)f(x_2)
$$
的函数为定义在R上的严格凸函数.

目标函数为凸函数, 约束函数也为凸函数的非线性规划为凸规划.

可以证明, **凸规划的可行域为凸集, 其局部最优解即为全局最优解, 而且其最优解的集合形成一个凸集. 当凸规划的目标函数f(x)为严格凸函数时, 其最优解必定唯一.**

## 无约束问题

无约束问题即没有约束条件的问题, 即求解函数极小值的问题

### 一维搜索方法

当用迭代法求函数的极小点时, 常常用到一维搜索, 即沿一**已知方向**求目标函数的极小点.

一种比较一个区间上两端函数值的方法, 原理非常简单, 不讲了.

但是这种方法一般只能用于单极值区间, 对于一个多极值的函数. 可以尝试先画出函数图, 然后找出所有只有单个极值的区间分别求解.

#### 斐波那契法

上面那种方法本是随机选取区间的两个点, 斐波那契法能够保证区间按照按照斐波那契数进行缩小.

即
$$
t_1 = a + \frac{F_{n-1}}{F_n}(b-a),t_2 = a + \frac{F_{n-2}}{F_n}(b-a)
$$

根据需要求解的精度$\delta$, 确定迭代次数的方式
$$
\frac{b-a}{F_n} \le \delta
$$

也可以用黄金比例数代替斐波那契数列.

### 二次插值法

对极小化问题, 当f(t)在[a,b]上连续时, 可以考虑用多项式插值来进行一维搜索. 基本思想为: 在搜索区间内, 不断用低次(不超过三次)多项式来近似目标函数, 并逐步用插值多项式的极小点来逼近极小化问题的最优解.

### 无约束问题的解法

#### 梯度下降法

总是朝着梯度下降最快的方向前进

#### 牛顿法

首先需要了解一下什么是[黑塞矩阵](Hesse_matrix.md)

考虑目标函数f在$x^k$处的二次逼近式
$$
f(x)\approx Q(x) = f(x^k) + \nabla f(x^k)^T(x-x^k) + \frac12(x-x^k)^T\nabla^2f(x^k)(x-x^k)
$$

假设黑塞矩阵
$$
\nabla^2 f(x^k) = \begin{bmatrix}
\frac{\partial^2 f(x^k)} & \dots & \frac{\partial^2 f(x^k)}{\partial x_1\partial x_n}\\
\vdots & \dots & \vdots \\
\frac{\partial f(x^k)}{\partial x_n\partial x_1} & \dots & \frac{\partial^2 f(x^k)}{\partial x_n^2}
\end{bmatrix}
$$
正定

由于$\nabla^2 f(x^k)$正定, 函数Q的驻点$x^{k+1}$是Q(x)的极小点. 令
$$
\nabla Q(x^{k+1}) = \nabla f(x^k) + \nabla^2 f(x^k)(x^{k+1} - x^k) = 0
$$

解得
$$
x^{k+1} = x^k - [\nabla^2 f(x^k)]^{-1}\nabla f(x^k)
$$

所以从$x^k$出发的搜索方向为
$$
p^k = -[\nabla^2 f(x^k)]^{-1}\nabla f(x^k)
$$

牛顿法的优点是收敛速度快; 缺点是有时不好用而需采取改进措施, 当维度很高时, 计算矩阵的逆矩阵计算量将会很大.

#### 变尺度法

变尺度法由于能够避免计算二阶导数矩阵及其逆矩阵, 对于高纬度问题具有显著的优越性.

为了不计算二阶导数矩阵$[\nabla^2 f(x^k)]$及其逆矩阵, 我们设法构造另一个矩阵, 来逼近二阶导数矩阵, 这一类也称为**拟牛顿法(Quasi-Newton Method)**.

当f(x)是二次函数时, 任两点$x^k$和$x^{k+1}$的梯度之差为
$$
\nabla f(x^{k+1}) - \nabla f(x^k) = A(x^{k+1} - x^k)
$$

因此, 我们构造黑塞矩阵的第k+1次近似$\overline H^{k+1}$满足关系式
$$
x^{k+1} - x^k = \overline H^{(k+1)}[\nabla f(x^{(k+1)}) - \nabla f(x^k)]
$$

这就是**拟牛顿条件**.

令
$$
\begin{cases}
\Delta G^{(k)} = \nabla f(x^{k+1}) - \nabla f(x^k)\\
\Delta x^k = x^{k+1} - x^k
\end{cases}
$$

记
$$
\Delta \overline H^{(k)} = \overline H^{(k+1)} - \overline H^{(k)}
$$
称为**校正矩阵**.

省略中间过程, 可求得校正矩阵
$$
\Delta \overline H^{(k)} = \frac{\Delta x^k(\Delta x^k)^T}{(\Delta G^{(k)})^T\Delta x^k} - \frac{\overline H^{(k)}\Delta G^{(k)}(G^{(k)})^T\Delta H^{(k)}}{(\Delta G^{(k)})^T\overline H^{(k)}\Delta G^{(k)}} \tag{(17)}
$$

从而有
$$
\overline H^{(k+1)} = \overline H^{(k)} + \frac{\Delta x^k(\Delta x^k)^T}{(\Delta G^{(k)})^T\Delta x^k} - \frac{\overline H^{(k)}\Delta G^{(k)}(G^{(k)})^T\Delta H^{(k)}}{(\Delta G^{(k)})^T\overline H^{(k)}\Delta G^{(k)}} \tag{(18)}
$$

以上矩阵称为**尺度矩阵**, 取第一个尺度矩阵$\overline H^{(0)}$为单位矩阵.

由此可得DFP变尺度法的**计算步骤**为:

1. 给定初始点$x_0$以及梯度允许误差$\varepsilon > 0$
2. 若$\lvert\nabla f(x^{(0)})\rvert \le\varepsilon$, 则$x_0$为近似点, 停止迭代.否则转下一步.
3. 令
$$
\overline H^{(0)} = I (单位矩阵)\\
p^0 = -\overline H^{(0)}\nabla f(x^0)
$$
在$p^0$方向进行一维搜索, 确定最佳步长$\lambda_0$
$$
\min_\lambda f(x^0+\lambda p^0) = f(x^0 + \lambda_0p^0)
$$
于是可以得到下一个近似点
$$
x^1 = x^0 + \lambda_0p^0
$$
4. 对于近似点$x^k$, 计算其梯度, 若有
$$
\lvert\nabla f(x^k)\rvert\le \varepsilon
$$
则停止迭代, 最终解为$x^k$; 否则根据式(18)计算$\overline H^{(k)}$, 令$p^k = -\overline H^{(k)}\nabla f(x^k)$. 在$p^k$方向进行一维搜索, 得到$\lambda_k$, 从而得到下一个近似点
$$
x^{k+1} = x^k + \lambda_kp^k
$$
5. 不断重复第4步直到满足允许误差.

### 约束极值问题

带有约束条件的极值问题称为约束极值问题, 也叫规划问题.

#### 二次规划问题

目标函数为自变量的二次函数的问题称为二次规划问题.

二次规划的模型可以表述为
$$
\min \frac12x^THx + f^Tx,\\
s.t.\quad \begin{cases} Ax\le b\\Aeq\dot x = beq\\ \end{cases}
$$

MATLAB中求解二次规划的函数为
`[x, f] = quadprog(H, f, A, b, Aeq, beq, LB, UB, X0, OPTIONS)`

#### 罚函数法

利用罚函数法, 可将非线性规划问题转化为一系列无约束机制问题. 因此也称这种方法为**序列无约束最小化技术, SUMT(Sequential Unconstrained Minization Technique)**.

罚函数法的基本思想是利用问题中的约束函数作出适当的罚函数, 由此构造出带参数的增广目标函数, 把问题转化为无约束线性规划问题.

罚函数法分为外罚函数法和内罚函数法. 现在介绍外罚函数法.

对于问题:
$$
\min f(x)\\
s.t.\quad \begin{cases} g_i(x)\le 0, i = 1,\dots,r,\\ h_j(x)\ge 0, j = 1,\dots,s,\\ k_m(x) = 0, m = 1,\dots,t \end{cases}
$$

取一个充分大的正数M, 构造函数
$$
P(x, M) = f(x) + M\sum_{i=1}^r\max(g_i(x), 0) - M\sum_{i=1}^s\min(h_i(x), 0) + M\sum_{i=1}^t|k_i(x)|
$$

### MATLAB 求约束极值问题

#### fminbnd 函数

求单变量非线性函数在区间$[x_1, x_2]$上的最小值

语法格式
`[x, f] = fminbnd(fun, x1, x2, options)`

#### fminimax 函数

可以用来求解带有非线性约束条件的问题

`x = fminimax(fun, x0, A, B, Aeq, Beq, LB, UB, NONLCON)`


