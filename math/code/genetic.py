# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# > Author     : lunar
# > Email       : lunar_ubuntu@qq.com
# > Create Time: Mon 03 Aug 2020 07:41:40 PM CST

import random

# 定义最大迭代次数
ITERATE_NUM = 100
TASK_NUM = 100
SERVER_NUM = 100

# 初始化任务节点，服务器节点，时间矩阵
# 返回一个包含了三个数组的元组
def init(task_num, server_num):
    tasks = []
    servers = []
    time_matrix = [i for i in range(task_num)]
    for i in range(task_num):
        tasks.append(random.randint(10, 100))
        servers.append(random.randint(10, 100))
    random.shuffle(time_matrix)
    return (tasks, servers, time_matrix)

# 计算染色体适应度，也就是处理时间
def calc_process_time(tasks, servers, time_matrix):
    res = []
    for i in len(time_matrix):
        res.append(tasks[i]/servers[time_matrix[i]])
    res.sort()
    return res

# 根据处理时间计算适应度
def calc_adaptability(time_matrix):


