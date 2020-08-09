/**********************************************
  > File Name		: dijkstra.cpp
  > Author			: lunar
  > Email			: lunar_ubuntu@qq.com
  > Created Time	: Fri 07 Aug 2020 10:42:57 AM CST
 **********************************************/

#include <iostream>
using namespace std;

/*
 * Dijkstra算法的C++实现
 *
 * 所谓Dijstra算法，是用来求从图中的一个点出发到达另一个点的权重和最小的
 * 路径的算法。
 *
 * Dijkstra算法采用一种贪心的策略，声明一个数组来保存源点到各个顶点的最
 * 短距离dis，以及一个保存已经找到了最短令的顶点的集合T。
 *
 * 在初始时，集合T中只有起始顶点。遍历所有与起始节点相连的节点，更新dis中
 * 的距离。这些距离都是未确定的暂时的最短距离。然后在这些距离选择一个最短
 * 距离，我们就可以断定这个就是起始节点到该节点的最短距离。然后我们遍历与
 * 该节点相连的节点并更新距离，然后再从dis中找到一个未定的最短的距离。重复
 * 上述步骤。
 *
 */

#include <vector>
#include <stack>

#define INF 0x7f7f7f7f

class Dijkstra {
    public:
        //通过邻接矩阵来表示图, graph[i][j]不为0表示节点i和j
        //相连，并且该值就表示这条边的权重，并且graph[i][j] = graph[j][i]
        vector<vector<int>> graph;

        Dijkstra(vector<vector<int>> graph) {
            this->graph = graph;
        }

        //如果在调用方法时指定了end，则说明只要找到start和end之间的最短距离。
        //否则就计算start到所有节点的最短距离
        vector<int> findShortestPath(int start, int end = -1) {
            int viewedNum = graph.size() - 1;
            vector<int> dis(graph.size(), INF);
            vector<bool> viewed(graph.size(), false);
            int minDis, minDisNode;

            dis[start] = 0;
            viewed[start] = true;
            while (viewedNum) {
                minDis = INF;
                for (int i = 0; i < graph.size(); i++) {
                    if (!viewed[i] && graph[start][i] != 0) {
                        if (dis[i] > graph[start][i] + dis[start]) {
                            dis[i] = graph[start][i] + dis[start];
                        }
                    }
                }
                //找到最短距离
                for (int i = 0; i < graph.size(); i++) {
                    if (!viewed[i] && minDis > dis[i]) {
                        minDis = dis[i];
                        minDisNode = i;
                    }
                }
                viewed[minDisNode] = true;
                start = minDisNode;
                viewedNum--;
            }
            return dis;
        }
};

int main() {
    vector<vector<int>> graph = {
        {0,0,10,0,30,100},
        {0,0,5,0,0,0},
        {10,5,0,50,0,0},
        {0,0,50,0,20,10},
        {30,0,0,20,0,60},
        {100,0,0,10,60,0}
    };
    
    Dijkstra dij(graph);
    vector<int> dis = dij.findShortestPath(0);
    for (int i = 0; i < dis.size(); i++) {
        cout << dis[i] << ", ";
    }
    cout << endl;
}
