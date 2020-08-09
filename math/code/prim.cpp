/**********************************************
  > File Name		: prim.cpp
  > Author			: lunar
  > Email			: lunar_ubuntu@qq.com
  > Created Time	: Fri 07 Aug 2020 05:42:24 PM CST
 **********************************************/

#include <iostream>
using namespace std;

/*
 * Prim算法C++实现
 *
 * 1. 从某个点开始，遍历当前点可以到达的所有边
 * 2. 找到端点还未访问的最小边，将端点加入集合，记录添加的边
 * 3. 寻找当前当前集合可以访问的所有边，重复2的过程
 * 4. 所有节点访问后所有边构成的树就是最小生成树
 *
 */

#include <vector>
#define INF 0x7f7f7f7f

class Prim {
private:
    vector<vector<int>> graph;

public:
    Prim(vector<vector<int>> graph) {
        this->graph = graph;
    }

    //最小生成树将以二维vector的形式给出
    vector<vector<int>> prim() {
        int nodeNum = graph.size() - 1;
        int start = 0;//初始节点
        int minEdge, minEdgeNode, startNode;

        vector<vector<int>> res(graph.size());
        vector<int> viewedNodes;
        vector<bool> viewed(graph.size(), false);
        viewedNodes.push_back(start);
        viewed[start] = true;
        
        while (nodeNum) {
            cout << "------------------------" << endl;
            minEdge = INF;
            for (int i = 0; i < viewedNodes.size(); i++) {
                int node = viewedNodes[i];
                for (int j = 0; j < graph[node].size(); j++) {
                    if (!viewed[j] && graph[node][j] != 0 && minEdge > graph[node][j]) {
                        minEdge = graph[node][j];
                        minEdgeNode = j;
                        startNode = node;
                    }
                }
            }
            cout << "minEdge: " << minEdge << endl;
            cout << "minEdgeNode: " << (char)(minEdgeNode+'A') << endl;
            cout << "startNode: " << (char)(startNode+'A') << endl;
            viewed[minEdgeNode] = true;
            viewedNodes.push_back(minEdgeNode);
            nodeNum--;
            res[startNode].push_back(minEdgeNode);
            res[minEdgeNode].push_back(startNode);
        }
        return res;
    }
};

int main() {
    vector<vector<int>> graph = {
        {0,7,0,5,0,0,0},
        {7,0,8,9,7,0,0},
        {0,8,0,0,5,0,0},
        {5,9,0,0,15,6,0},
        {0,7,5,15,0,8,9},
        {0,0,0,6,8,0,11},
        {0,0,0,0,9,11,0}
    };
    Prim p(graph);
    vector<vector<int>> res = p.prim();
    for (int i = 0; i < res.size(); i++) {
        for (int j = 0; j < res[i].size(); j++) {
            cout << (char)(i+'A') << " -> " << (char)(res[i][j]+'A') << endl;
        }
    }
    return 0;
}
