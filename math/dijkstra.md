### **图的最短路径——Dijkstra算法**

Dijkstra算法通过一种类似广度优先搜索的方式遍历所有的节点。

该算法首声明一个距离数组dis和一个判断是否遍历到的数组access。

dis的长度与所有的顶点数量一致，用于存放起始顶点到所有顶点的距离，无法到达的顶点距离为$\infty$。

access存放所有需要遍历的节点，假设用0表示没有访问，1表示访问了。则初始时均设为0。每次遍历前，都从该数组中找到**没有被遍历且距离起始节点最近**的那个节点进行以下操作：访问该节点所有的出度节点，如果路径：**起始节点->遍历节点->便利节点**的某出度节点的距离比之前的最短路径（或者说并没有到达过）：**起始节点->该遍历节点的出度节点**的距离要短，则将起始节点到达该出度节点的距离更新，并将该出度节点设置为未访问过。

持续如此遍历直到access数组中所有可遍历到节点已被遍历。
