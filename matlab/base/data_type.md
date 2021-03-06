---
author: lunar
date: Wed 19 Aug 2020 12:05:16 PM CST
---

### MATLAB数据类型

MATLAB提供了15种数据类型，每种数据类型存储矩阵或数组形式的数据。

![](../screenshots/matlab1.png)

MATLAB还提供了大量的数据类型转换函数。

![](../screenshots/matlab2.png)

数据类型确定相关的函数

![](../screenshots/matlab3.png)

### MATLAB算术运算符

MATLAB有两种不同类型的算术运算，矩阵算术运算和数组算术运算。

矩阵运算与线性代数中的定义相同，数组运算则是逐个元素执行数组运算。矩阵运算符和数组运算符由句点符号(`.`)区分。对于加法和减法，矩阵运算和数组运算都是一样的，所以不做区分。

|运算符|描述说明|
|------|--------|
|*|矩阵乘法|
|.*|数组乘法，数组中的元素逐个相乘。要求两个数组具有相同的大小，除非其中一个是标量|
|^|矩阵X的p次幂。如果p是整数，则通过重复平方来计算幂值。如果整数为负，则X先倒置。对于p的其它值，不管|
|.^|阵列幂值，计算的两个阵列必须具有相同的大小，除非之一是标量|
