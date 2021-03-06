---
author: lunar
date: Sun 18 Oct 2020 04:50:31 PM CST
---

## 进程调度

进程可以被分为 I/O 密集型和处理器密集型。这里说的 I/O 是指任何类型的可阻塞资源，包括磁盘I/O，外设输入，网络 I/O等。多数用户图形界面程序都属于 I/O 密集型。

Linux为了保证交互式应用和桌面系统的性能，所以对进程的响应做了优化，更倾向于优先调度 I/O 密集型进程。

### 调度策略

#### 进程优先级

Linux采用两种不同的优先级范围。nice值和实时优先级。

nice值范围为-20到19，nice值越大表示优先级越低。

实时优先级范围为0到99，任何实时进程的优先级都高于普通进程。

### Linux调度算法

![](https://pic2.zhimg.com/80/v2-c45c9dc70e5cd01404ae4a04ddd0e9a1_720w.jpg)

如图，调度器根据不同的进程依次遍历不同的调度策略，找到进程对应的调度策略。

-   CFS(Completely Fair Schedule): CFS遵循所有进程占用CPU处理的时间应该一致，当某个I/O密集型进程就绪时，调度器会查看其处理器占用时间，发现其大部分时间都在等待I/O，则其优先级就自然高于占用了大部分处理器时间的处理器密集型进程。nice值在CFS中被作为进程获得的处理器运行比的权重，即调度器认为的处理器占用时间对比并不是相对于不同的进程而言，而是特定的一个进程其已经使用的处理器时间和理论上可分配的时间片之比。

    但是这样也会带来一个问题，当可运行任务趋于无限时，各自获得的处理器使用比将趋于0，这将带来难以接受的进程上下文切换的消耗。CFS引入了每个进程可获得的时间片底线，默认为1ms。

-   FIFO队列：比CFS调度的优先级更高，只要处于可执行状态就选择该策略。

-   RR(Round-Robin): 在耗尽被分配的时间片之后就不会被执行

### Linux调度的实现

#### 时间记账

**调度器结构体**

![image-20201018204118514](https://raw.githubusercontent.com/xiaoqixian/Tiara/master/img/image-20201018204118514.png)

调度器结构体作为一个名为se的成员变量，嵌在struct task_struct中。

**虚拟实时**

vruntime变量存放进程的虚拟运行时间，以ns为单位，用来记录一个程序已经运行了多长时间以及还可以运行多长时间。

vruntime变量是已经被标准化了的，具有最小vruntime的进程就是下一个被运行的进程。

#### 进程选择

从一系列进程中选择一个具有最小vruntime的进程，这是一个很典型的算法题。Linux内部使用红黑树来组织可运行进程队列。

关于红黑树这种数据结构可以查看我的这篇[文章](https://www.cnblogs.com/lunar-ubuntu/p/13843155.html)

在红黑树中，vruntime最小的节点对应的就是最左边的那个叶子节点。但是调度器不会每次都去寻找，而是已经将其指针缓存在了数据结构中，可以通过指针直接找到。

#### 调度器入口

进程调度的主要入口点是函数schedule()，schedule()通常都需要和一个具体的调度类相关联，schedule()函数内调用pick_next_task()，pick_next_task()会以优先级为序，依次检查每个调度类，并从最高优先级的调度类中选择最高优先级的进程。

#### 睡眠和唤醒

进程的休眠有多种原因，但肯定都是为了等待某个事件，大部分都是等待I/O。不管是什么原因，内核的操作都是相同的：将进程标识为休眠状态，从可执行红黑树中移除，放入等待队列。

而唤醒进程时，执行的是相反的操作：将进程标识为可运行状态，从等待队列移动到可执行红黑树中。

### 抢占和上下文切换

上下文切换，就是从一个可执行进程切换到另一个可执行进程，由定义在 kernel/sched.c 中的 context_switch() 函数负责处理，其负责两项基本工作：

-   调用 switch_mm()，该函数负责把虚拟内存从上一个进程映射切换到新进程中
-   调用 switch_to()，负责从上一个进程的处理器状态切换到下一个进程的处理器状态。这包括保存、恢复栈信息和寄存器信息。

内核提供了一个need_resched 标志来表明是否需要重新执行一次调度。当某个进程应该被抢占时，scheduler_tick() 就会设置这个标志；当一个优先级高的进程进入可执行状态时，try_to_wake_up() 也会设置标志，内核检查其标志，调用 schedule() 来切换到一个新的进程。

#### 用户抢占

#### 内核抢占

内核抢占是指一个在内核态运行的进程，可能在执行内核函数期间被另一个进程取代。

在不支持抢占的内核中，内核代码可以一直执行直到完成为止。但是如果内核代码要执行一些等待I/O的操作，就非常影响系统速度。在Linux2.6版的内核之后，内核引入了抢占式，只要**重新调度是安全**的，内核就可以在任何时间抢占正在执行的任务。

至于什么时候重新调度是安全的：只要没有持有锁，内核就可以进行抢占，锁是非抢占区域的标志。

为了支持抢占式内核，Linux为每个进程的thread_info 引入 preempt_count计数器。计数器初始值为0，每当使用锁数值就加1。当计数器的数值为0时，内核就可以进行抢占。

当中断返回内核空间的时候，内核就会检查need_resched和preempt_count的值。如果need_resched被设置并且preempt_count的值为0，就说明有一个更重要的任务需要完成，内核就可以实行抢占。

如果内核中欧给你的进程被阻塞了，或者它显示调用了 schedule()，内核抢占也会显式地发生。

所以内核抢占会发生在：

-   中断处理程序正在执行，且返回内核空间之前；
-   内核代码再一次具有可抢占性的时候；
-   内核代码显式调用schedule()；
-   内核任务阻塞。

#### 内核抢占的实现

linux内核在 thread_info 结构体添加了一个自旋锁标识 `preempt_count` ，称为抢占计数器。

`preempt` > 0，表示禁止内核抢占；=0可以开启内核抢占，<0说明内核出现错误。

### 实时调度策略

Linux提供了两种实时调度策略：SCHED_FIFO 和 SCHED_RR，而普通的、非实时的调度策略是 SCHED_NORMAL。

SCHED_FIFO 实现了一种简单的、先入先出的调度算法，其不使用时间片，**处于可运行状态的 SCHED_FIFO 级进程会比任何 SCHED_FIFO 级的进程先得到调度。**直到它自己收到阻塞或显式地释放处理器。当然，更高级别的 SCHED_FIFIO 和 SCHED_RR 级进程还是可以抢占该进程。

SCHED_RR可以认为是带有时间片的SCHED_FIFO，这是一种实时轮流调度算法。当 SCHED_RR 任务耗尽它的时间片时，在**同一优先级**的其他实时进程被轮流调度。

对于 SCHED_FIFO 进程，高优先级总是抢占低优先级，但是低优先级进程决不能抢占 SCHED_RR 任务，即便它的时间片耗尽。

### 与调度相关的系统调用

![image-20201021135837679](https://raw.githubusercontent.com/xiaoqixian/Tiara/master/img/image-20201021135837679.png)

#### 与处理器绑定有关的系统调用

Linux调度程序提供强制的处理器绑定 (processor affinity) 机制。在 task_struct 的 cpus_allowed 的位掩码标志中，每一位对应一个系统可用的处理器，用户可以通过 sched_setaffinity() 设置不同的一个或几个位组合的位掩码。

#### 放弃处理器时间

Linux 通过 sched_yield() 系统调用，提供了一种让进程显式地将处理器时间让给其他等待执行进程的机制。它是通过将进程从活动队列移动到过期队列中完成的——这样就能确保进程在一段时间内都不会被执行了。

实时进程属于例外，它们只会被放置到优先级队列的末尾。