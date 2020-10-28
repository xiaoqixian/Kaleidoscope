---
author: lunar
date: Wed 28 Oct 2020 07:11:15 PM CST
location: Shanghai
---

## 内存管理

本章主要了解内核中的内存分配，一般操作系统书籍讲解的都是用户空间的内存分配。在内核中内存比较紧张，并且内核不能睡眠，处理内存分配错误也更加困难。

### 页

内核把物理页作为内存管理的基本单位。在32位系统上页的大小为4KB，64位系统页的大小为8KB。

#### 页的数据结构

```c
struct page {
    unsigned long flags; //页状态，总共有32种
    atomic_t _count; //页的引用次数
    atmoic_t _mapcount; 
    unsigned long private;
    struct address_space* mapping;
    pgoff_t index;
    struct list_head lru;
    void* virtual; //页的虚拟地址。有些内存并不永久地映射到内核地址空间，此时virtual为null
};
```

### 区

内核并不是对于所有的页一视同仁，有些页位于内存中特定的物理地址上，用于执行一些特定的任务。因此，内核把页划分为不同的区（zone）。

linux必须处理由于硬件缺陷而引起的两类内存寻址问题：

-   一些硬件只能用某些特定的内存地址来执行DMA（Direct Memory Access）
-   一些体系结构内存的物理地址范围大于虚拟地址的寻址范围，导致一些物理内存永远无法使用。

因此，内核使用四种区：

-   ZONE_DMA：该区的页可以执行DMA操作
-   ZONE_DMA32：这些页与上一个类似，但是只能被32位设备访问
-   ZONE_NORMAL：包含正常映射的页
-   ZONE_HIGHEM：包含“高端内存”，其中的页永远不能映射到内核地址空间

![image-20201028195501430](https://raw.githubusercontent.com/xiaoqixian/Tiara/master/img/image-20201028195501430.png)

32位x86的体系结构下，各个区的内存范围如图所示。32位系统支持的最大内存为4GB，其中内核地址空间占1GB。