# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# > Author     : lunar
# > Email       : lunar_ubuntu@qq.com
# > Create Time: Fri 11 Sep 2020 03:54:48 PM CST

# C题第一题属于典型分类问题
# 目前可用的方法包括:
# 1. 决策树
# 2. 朴素贝叶斯算法
# 3. 支持向量机
# 4. 随机森林
# 5. KNN算法

# 数据处理代码
import csv


filename = ""

# 企业信誉评级和是否违约
def repulation_degree():
    with open(filename) as f:
        reader = csv.reader(f)
        for row in reader:


