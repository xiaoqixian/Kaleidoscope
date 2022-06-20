# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# > Author     : lunar
# > Email       : lunar_ubuntu@qq.com
# > Create Time: Tue 04 Aug 2020 10:53:33 AM CST

tasks = []
task_num = 100

nodes = []
node_num = 10

task_length_range = [10, 100]
node_speed_range = [10, 100]

time_matrix = []

iterate_num = 100

chromosome_num = 10

adaptability = []

selection_probability = []

chromosome_copy_rage = 0.2

crossover_mutation_num

result_data = []

# 初始化遗传算法
def init_ga(task_num, node_num, iterate_num, chromosome_num, chromosome_copy_rage):
    tasks = init_random_array(task_num, task_length_range)

    nodes = init_random_array(node_num, node_speed_range)

    ga()

def init_random_array(num, _range):
    res = []
    for i in range(num):
        res.append(random.randint(_range[0], _range[1]))
    return res

def ga():
    # 初始化执行任务时间矩阵
    init_time_matrix(tasks, nodes, time_matrix)

    # 迭代搜索
    ga_search(iterate_num, chromosome_num)

def init_time_matrix(tasks, nodes, time_matrix):
    time_matrix = [i for i in range(len(tasks))]
    random.shuffle(time_matrix)

def ga_search(iterate_num, chromosome_num):
    # 初始化第一代染色体
    chromosome_matrix = create_generation()

    for i in range(iterate_num):
        cal_adapatability(chromosome_matrix)

        cal_selection_probability(adaptability)

        chromosome_matrix = create_generation(chromosome_matrix)

def cal_adapatability(chromosome_matrix):
    adaptability = []

    for chromosome_index in range(chromosome_num):
        max_length = float("inf")
        for node_index in range(node_num):
            sum_length = 0
            for task_index in range(task_num):
                if chromosome_matrix[chromosome_index][task_index] == node_index:
                    sum_length += time_matrix[task_index][node_index]

if __name__ == '__main__':
    init_ga(100, 10, 100, 0.2)


