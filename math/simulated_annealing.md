---
author: lunar
date: Mon 03 Aug 2020 03:28:35 PM CST
tag: 问题优化
---

### **模拟退火算法**

#### 物理上的退火

热力学上的退火（annealing）现象是指物体逐渐降温的物理现象，温度越低，物理的能量状态就会越低。温度足够低时，液体就会开始冷凝与结晶，在结晶状态时，系统的能量状态最低。但是当物体的温度下降过快时，物体来不及形成最低能量状态的晶体。

#### 模拟退火（Simulate Anneal）

考虑一种求函数最小值的策略，如果使用贪心算法，那么可能在到达函数的一个局部最小值后就无法前进。显然这样是无法保证求出全局最小值的。

退火算法也是一种贪心算法，但是它在搜索过程中加入了随机因素，以一定的概率来接受一个比当前解法更差的解，因此有可能跳出局部最优解。

如果用E来表示物体内能，k表示玻尔兹曼常数。则物体温度变化的概率为：
$$
p = \begin{cases}
1,\quad if\quad E(t_{new}) < E(t_{old})\\
exp(-\frac{E(t_{new})-E(t_{old})}{kT}), if\quad E(t_{new})\ge E_{t_{old}}
\end{cases}
$$
也就是说，如果物体内能可以下降，则温度变化的概率看做是1。如果物体内能上升，则物体温度变化的概率也不是没有。而是根据下面那个式子进行计算。并且，**温度越低，出现降温的概率就越小。**

#### 模拟退火算法解决TSP（Traveling Salesman Problem）问题

问题描述：假设有一个商人要拜访n个城市，他必须选择要走的路径，路径的限制是每个城市只能拜访一次，而且最后要回到原来触发的城市。路径的选择目标是要求总的路程最小。

其实这是一个典型的图论问题。但是我们可以将其转化为模拟退火算法可以做的形式。

1. 产生一条新的遍历路径$P_{i+1}$，计算新的路径的长度L

2. 如果小于原来的路径，则直接接受。否则计算计算接受的概率，根据事先设置的可以接受的概率门槛，再决定是否接受作为新的路径。

3. 产生新的路径有很多方法。如果图中每个节点都是彼此相连的话，则可以随意交换两个节点的顺序来产生新的路径。

   如果不是任意相连的话还要考虑路径的可行性。

4. 模拟退火算法毕竟不是遍历图中所有路径的可能性，所以还需要事先给出遍历的次数。所以才称最优解的近似解。因为最优解可能藏在没有被遍历到的路径里面。
