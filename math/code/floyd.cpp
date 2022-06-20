/**********************************************
  > File Name		: floyd.cpp
  > Author			: lunar
  > Email			: lunar_ubuntu@qq.com
  > Created Time	: Fri 07 Aug 2020 03:41:43 PM CST
 **********************************************/

#include <iostream>
using namespace std;

/*
 * Floyd算法
 *
 * 核心思想是在两个顶点之间插入一个或一个以上的中转点，比较经过
 * 与不经过中转点的距离哪个更短。
 *
 * 为此需要引入两个矩阵，一个邻接矩阵D，表示相邻点之间的距离
 * 一个矩阵P，表示中间点的代数，如P[i][j]表示i与j之间的中间点代数
 *
 * 性能问题：相比于Dijkstra算法，Floyd算法的性能不足，复杂度为O(n^3)
 * 所以这里只做简单介绍
 * 给出一个核心部分代码
 */

//核心代码如下
for (int k = 0; k < n; k++) {
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {
            if (d[i][j] > d[i][k] + d[k][j]) {
                d[i][j] = d[i][k] + d[k][j];
            }
        }
    }
}

/*
 * 可以看出Floyd算法就是粗暴地对于每条边都遍历所有的中转点，
 * 找到一个更适合的中转路线。效率自然不高
 */

