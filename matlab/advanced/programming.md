---
author: lunar
date: Thu 20 Aug 2020 11:32:57 PM CST
---

## MATLAB求解规划问题

### MATLAB解决线性规划问题

在MATLAB中通过`linprog`函数求解线性规划问题。

现在通过一个例子进行说明

![](../screenshots/matlab6.png)

求解的MATLAB程序为

```matlab
f=[-2,-3,5]'
A=[-2,5,-1;1,3,1];  b=[-10;12];
Aeq=[1,1,1];    beq=7;
[x,fval]=linprog(f,A,b,Aeq,beq,zeros(3,1));
x
fval=-fval
```

这里的`zeros(3,1)`是为了产生一个3行1列的矩阵，对应三个决策变量大于等于0

所以`linprog`函数的使用格式为
`[x,fval] = linprog(f, A, b, Aeq, beq, lb, ub)`

最广泛的解决形似与
$$
\min f^Tx such that\begin{cases}A\cdot x\le b\\Aeq\cdot x=beq\\lb\le x\le ub \end{cases}
$$


### MATLAB求解整数规划

MATLAB提供`intlinprog`函数求解整数规划问题

以下题为例

![](https://img2020.cnblogs.com/blog/996313/202006/996313-20200608085524057-766954037.png)

相应的MATLAB代码为
```matlab
clc,clear;
c = [-40;-90];
A = [9 7;7 20];
b = [56;70];
lb = zeros(2,1);
[x,fval]= intlinprog(c,1:2,A,b,[],[],lb);
fval = -fval
x
```

### MATLAB求解非线性规划问题

如果目标函数或约束条件中包含非线性函数，就称这种规划问题为非线性规划问题。非线性规划问题目前还没有适合各种问题的一般算法，各个方法都有自己的适用范围。

MATLAB提供的解决非线性规划的函数为`fmincon`

`x = fmincon(fun, x0, A, B, Aeq, Beq, LB, UB, NONLCON, OPTIONS)`

它的返回值是向量x，其中fun 是用M 文件定义的函数f(x)；X0 是x
的初始值；A,B,Aeq,Beq 定义了线性约束A\* X ≤ B, Aeq \* X = Beq ，如果没有线性约束，则A=[],B=[],Aeq=[],Beq=[]；LB 和UB 是变量x的下界和上界，如果上界和下界没有约束，则LB=[]，UB=[]，如果x无下界，则LB 的各分量都为-inf，如果x无上界，则UB的各分量都为inf；NONLCON 是用M 文件定义的非线性向量函数C(x),Ceq(x)；OPTIONS定义了优化参数，可以使用Matlab 缺省的参数设置。

#### 求解二次规划

如果某非线性规划的目标函数是自变量的二次函数，而约束条件全为线性的。就称这种规划为二次规划。MATLAB提供了更加合适的函数解决这类问题。

二次规划的数学模型可以表示为
$$
\min \frac12x^THx + f^Tx,\\
s.t.\quad \begin{cases}Ax\le b\\Aeq\cdot x=beq \end{cases}
$$

求解二次规划的函数为`quadprog`,语法格式为
`[x,fval] = quadprog(H,f,A,b,Aeq,beq,LB,UB,X0,OPTIONS)`


