---
author: lunar
date: Mon 07 Sep 2020 11:28:36 PM CST
---

## 数据的统计描述和分析

### 统计的基本概念



#### 方差计算

当已知X服从某个分布, 设该分布的期望为$\mu$.

对该分布进行一系列采样, 样本的方差计算方式为:

1. 若已知该分布的期望$\mu$, 则方差为
$$
S^2 = \frac1n\sum_{i=1}^n(X_i - \mu)^2
$$
2. 否则通过样本均值估计方差, 计算方式为
$$
S^2 = \frac1{n-1}\sum_{i=1}^n(X_i - \overline X)^2
$$

#### 
