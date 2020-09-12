---
author: lunar
date: Sat 12 Sep 2020 07:51:43 PM CST
---

## Linux 内存分类

Linux用户内存有两类比较重要: 匿名内存和File-backed内存; Active和Inactive内存.

- 匿名内存: 用来存储用户进程计算过程中间的数据, 与物理磁盘的文件没有关系;
- File-backed内存: 用作磁盘的高速缓存, 与物理磁盘上的文件相对应, 会定时写入磁盘.
- Active: 包含刚被使用过的数据的内存空间;
- Inactive: 包含长时间未使用的数据的内存空间;

### Linux 的内存占用率为什么经常看起来非常高

Linux使用的资源肯定是少于Windows的, 但是我在转到Linux后发现内存占用率经常会高于Windows下的内存占用率. 后来才发现Linux会利用几乎所有的内存用作文件缓冲区.

使用`free`命令查看内存占用率. 发现free一栏的内存特别少, 但这不是真实的内存占用率. 

真实的内存占用率的计算方式为:
$$
(free + shared + buffers + cached) / Total
$$

buffer栏: 用于块设备I/O;
cached栏: 用于文件系统缓存
