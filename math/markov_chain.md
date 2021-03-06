---
author: lunar
date: Sun 06 Sep 2020 03:33:06 PM CST
---

## 马尔科夫链模型

### 马尔科夫链定义

现实中有这样的现象: 某一系统在已知现在情况的条件下, 其未来时刻的状态就只与现在有关, 而与未来无关. 比如在已知超市当前累积营业额的情况下, 未来的任一时刻的累计营业额都与现在以前的任一时刻的营业额无关.  我们描述这类随机现象的数学模型为**马尔科夫链模型**, 简称**马氏模型**.

**定义1**: 设$\{\xi_n, n=1,2,\cdots \}$是一个随机序列, 状态空间E为有限或可列集, 对于任意的正整数$m,n$, 若$i,j.i_k\in E(k=1,\dots,n-  1)$, 有
$$
P\{\xi_{n+1}=j|\xi_n=i,\xi_{n-1}=i_{n-1},\dots,\xi_1=i_1\} = P\{\xi_{n+m} = j|\xi_n = i\}\tag{1}
$$
则称该随机序列为**马尔科夫链**, 式(1)称为**马氏性**.

**定义2**: 对于一个马氏链, 如果等式(1)右边的条件概率与n无关, 即
$$
 P\{\xi_{n+m} = j|\xi_n = i\} = p_{ij}(m)\tag{2}
$$
则称$\{\xi_n, n = 1,2,\cdots\}$为**时齐**的马尔科夫链.                              称$p_{ij}(m)$为系统由状态i经过m个时间间隔转移到状态j的概率.

### 转移概率

对于一个马尔科夫链, 称以m步转移概率$p_{ij}(m)$为元素的矩阵$P(m) = p_{ij}(m)$为马尔科夫链的m步转移矩阵.

**定理1**: 设$\{\xi_n = 1,2,\dots\}$是一个马尔科夫链, 则对任意正整数m,n有
$$
p_{ij}(m+n) = \sum_{k\in E}p_{ik}(n)p_{kj}(m)
$$

**定理2**: 设P是一个马氏链转移矩阵(P的行向量是概率向量), $P^{(0)}$是初始分布行向量, 则第n步的概率向量为
$$
P^{(n)} = P^{(0)}P^n
$$

### 转移概率的渐近性质---极限概率分布

随着步数的增加, 转移概率矩阵越来越趋向于某个固定矩阵. 

**定义3**: 一个马氏链的转移矩阵P是正则的, 当且仅当存在正整数k, 是$P^k$的每一个元素都是正数.

若P是一个马氏链的正则矩阵, 则P存在一个不动点向量W. P的n次幂随着n的增加而趋向于矩阵$\overline W$, $\overline W$的每一行向量均等于不动点向量W.

在知晓转移矩阵P的情况下, 我们可以通过下面的方法来求不动点向量W.

记
$$
W = \begin{bmatrix}p_1\\p_2\\\vdots\\p_n\end{bmatrix}
$$

则有
$$
\overline W = \begin{bmatrix} W^T\\W^T\\\vdots\\W^T\end{bmatrix}\\
\overline W\cdot p = W
\sum_{i=1}W_i = 1
$$

便可求得不动点向量W.

从不动点向量可以看出该系统未来的发展趋势, 比如三家公司未来的市场份额占比.

### 吸收链

若马氏链存在一种状态, 这种状态只有向自己转变的可能. 则称这种状态为**吸收状态**.

如果马氏链至少含有一种吸收状态, 并且从每一种状态出发, 都可以到达吸收状态, 则称该马氏链为**吸收链**.

具有r个吸收状态的吸收链, 它的$n\times n$转移矩阵的标准形式为
$$
P = \begin{bmatrix}
I_r & O\\
R & S
\end{bmatrix}\tag{4}
$$

从(4)式得
$$
P^n = \begin{bmatrix}
I_r & O\\
Q & S^n\\
\end{bmatrix}
$$

在吸收链中, 令$F = (I - S)^{-1}$, 则$F$称为**基矩阵**.

**定理**: 基矩阵F中的每一个元素, 表示从一个非吸收状态出发, 过程到达每个非吸收状态的平均转移次数.

**定理**: 设$N = FC, C = \begin{bmatrix}1&1&\cdots&1\end{bmatrix}^T$. 则N的每个元素表示从非吸收状态出发, 到达某个吸收状态之前的平均转移次数.

**定理**: 设$B = FR = (b_{ij})$, 其中F为基矩阵, R为(4)中的子矩阵. 则$b_{ij}$表示从非吸收状态i出发, 被吸收状态j吸收的概率.


