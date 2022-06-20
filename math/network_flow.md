---
author: lunar
date: 
---

### **网络流算法**

网络流通常用于解决这样一类问题：在一个网络图中，所有的边都是有流量限制的。现有从图中一个点到另一个点的流量运输需求。要求找到一个可以满足运输需求，所有路程之和最短的线路。

#### **最大流**

同样是上面的那个问题，如果我们不计成本，要求在起点和终点之间运输尽可能多的货物，这时候就需要计算两个点之间的最大流量。

最大流最小割定力(Ford-Fulkerson, 1962)保证了在没有非负流量和非负客量限制的前提下，Ford-Fulkerson算法总是能够找到网络中的最大流。

#### **Ford-Fulkerson算法**

该算法主要包含了3个子算法思想：残差网络思想、增广路径思想、最大流最小割思想。

**残差网络$G_f$**

从u到v可以压入的额外流量就是流网络G中u,v的残留流量，容纳这些残留流量的边组成的子网络就是残差网络。残差网路的流量满足：$c_f(u,v) = c(u,v)-f(u,v)$

**增广路径**

残差网络$G_f$中从源点到汇点的一条简单路径。

增广路径的流量等于路径上所有边的残差流量的最小值

$$
c_f(p) = \min{c_f(u,v)|(u,v)\in p}
$$

**流网络的割**

在一个流网络中，它的割(S,T)将整个流网络分成两个部分，即S和T，其中T=G-S。如果存在一个流，穿过割(S,T)，即从子网络S流向子网络T，则我们称这个流为割的净流量。

最小割：一个流网络中净流量最小的割

**基本思想**

有了这三个概念，我们就可以正式通过Ford-Folkerson算法解题了

迭代算法：开始时任意找出从s到t的一条增广路p，往p上每条边的流量f加上残差流量，迭代此过程，更新每一对定点间网络流知道不存在增广路。

Ford-Fulkerson算法的上述实现被称为Edmonds-Karp算法，复杂度为O(VE^2^)。因为是通过BFS的方法寻找增广路径。

Edmonds-Karp算法的核心在于引入反向边，反向边的残差等于正向边残差的相反数。如果一条边既走了正向，又走了反向，则代表撤销之前走正向的决定。

```c++
#define maxn 220
#define INF 0x7f7f7f7f
int cap[maxn][maxn],flow[maxn][maxn];
int pre[maxn],res[maxn];//res[i] 残量
int Edmonds_Karp(int start,int end)
{
    int maxflow=0;
    memset(flow,0,sizeof(flow));
    memset(pre,0,sizeof(pre));
    queue<int> q;
    while(true)
    {
        memset(res,0,sizeof(res));
        res[start]=INF;
        q.push(start);
        while(!q.empty()) //BFS寻找增广路
        {
            int u=q.front();
            q.pop();
            for(int v=1;v<=end;v++)
                if(!res[v]&&cap[u][v]>flow[u][v])
                {
                    res[v]=min(res[u],cap[u][v]-flow[u][v]);//start-v路径上的最小残量,可以保证最后的汇点总是拿到最小的残差。
                    //记录v的父亲，并加入队列中
                    pre[v]=u;//记录父亲节点以便后面的反向残差计算
                    q.push(v);
                }
        }
        if(res[end]==0) return maxflow;//无法继续更新最大流量，则当前流已经是最大流
        for(int u=end;u!=start;u=pre[u])//从汇点往回走
        {
            flow[pre[u]][u]+=res[end];//更新正向流
            flow[u][pre[u]]-=res[end];//更新反向流
        }
        maxflow+=res[end]; //更新从s流出的总流量
    }
}
int main()
{
    //
    memset(cap,0,sizeof(cap));
    //
    for(/**/)
    {
        int u,v,s;
        scanf("%d %d %d",&u,&v,&s);
        cap[u][v]+=s;//要考虑到重边问题
    }
    //
    return 0；
}
```

同样，我们可以实现一个DFS实现的Ford-Fulkerson算法



#### **Dinic最大流算法**

Dinic算法比Edmonds-Karp算法更快，复杂度为O(EV^2^)。

**Dinic算法概述**:

1. 将残差图G初始化为给定图

2. 进行G的BFS构造一个level图，并检查是否更多的流量是可能的。一个顶点的level是该顶点到源的最短距离，以边的数量表示。

3. 如果不可能有更多的流量，则返回

4. 使用level图在G中发送多个流，直到达到阻塞流量
