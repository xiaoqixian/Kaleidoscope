/*
 * Ford-Fulkerson算法的BFS实现和DFS实现
 */

#define inf 0x7f7f7f
//flow[u][v]表示u到v的流量，cap[u][v]表示u到v的容量
int flow[maxn][maxn], cap[maxn][maxn];
int pre[maxn];

int fordFulkersonBFS(int s, int t) {
    int res[maxn];
    queue<int> q;
    int maxflow = 0;
    while (true) {
        memset(res, 0, sizeof(res));
        q.push(s);
        while (!q.empty()) {
            int u = q.front();
            q.pop();
            for (int v = 0; v < maxn; v++) {
                if (!res[v] && cap[u][v] > flow[u][v]) {
                    res[v] = min(res[u], cap[u][v] - flow[u][v]);
                    pre[u] = v;
                    q.push(v);
                }
            }
        }
        if (res[t] == 0) return maxflow;
        for (int u = t; u != s; u = pre[u]) {
            flow[u][pre[u]] -= res[t];
            flow[pre[u]][u] += res[t];
        }
        maxflow += res[end];
    }
}

//DFS实现Ford-Fulkerson算法
int fordFulkersonDFS(int start, int end) {
    int res[maxn];
    stack<int> s;
    int maxflow = 0;
    while (true) {
        memset(res, 0, sizeof(res));
        res[start] = inf;
        s.push(start);
        while (!s.empty()) {
            int u = s.top();
            s.pop();
            for (int v = 0; v < end; v++) {
                if (!res[v] && flow[u][v] < cap[u][v]) {
                    res[v] = min(res[u], cap[u][v] - flow[u][v]);
                    pre[v] = u;
                    s.push(v);
                }
            }
        }
        if (res[end] == 0) return maxflow;
        for (int u = end; u != start; u = pre[u]) {
            flow[u][pre[u]] -= res[end];
            flow[pre[u]][u] += res[end];
        }
        maxflow += res[end];
    }
}
