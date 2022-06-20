---
author: lunar
date: Fri 23 Oct 2020 02:27:09 PM CST
---

## 下半部和推后执行的工作

下半部的任务就是执行与中断处理密切相关但中断处理程序本身并不执行的工作。

### 下半部

#### 下半部的实现

在2.6以后版本的内核中，下半部主要有三种实现机制：

-   工作队列
-   软中断（softirq）
-   tasklet

### 软中断

#### 软中断特性

-   产生后不是马上执行，必须等待内核的调度。软中断不能被自己打断，只能被硬件中断打断；
-   可以并发运行在多个CPU上，所以软中断必须设计为可重入的函数（即只使用栈变量，即便使用全局变量也要加锁的函数）。

#### 软中断的实现

软中断是在编译期间静态分配的，不像tasklet那样可以动态注册和注销。软中断由以下结构体表示

```c
struct softirq_action {
    void (*action)(struct softirq_action*);
};
```

当内核执行一个软中断处理程序时，就会执行这个action函数。

一个软中断不会抢占另外一个软中断，唯一可以抢占软中断的是中断处理程序，其他的软中断（包括同类型的软中断）可以在其他处理器上同时执行，说明软中断是可以并发运行的，所以才要求软中断函数可重入。

在内核中定义有一个包含32个该结构体的数组softirq_vec。

**执行软中断**

软中断在do_softirq() 中被执行，

执行 do_softirq() 有两个先决条件：

1.  不在中断中（硬件中断、软中断和 NMI）
2.  有软中断处于 pending状态

其核心代码如下：

```c
// 用局部变量pending保存local_softirq_pending() 宏的返回值，是一个32位整数，第n位被置1,就代表第n为对应类型的中断需要处理
u32 pending;
pending = local_softirq_pending();

//遍历32位，如果相应位被置1,则执行相应的处理程序
if (pending) {
    struct softirq_action* h;
    
    //重设待处理的位图
    set_softirq_pending(0);
    h = softirq_vec;
    do {
        if (pending & 1) {
            h->action(h);
        }
        h++;
        pending >>= 1;
    } while (pending);
}
```

不得不说程序设计地非常巧妙。

#### 软中断内核线程

`ksoftirqd` 内核线程是系统为每个处理器创建的协助处理软中断的线程。当内核中出现大量软中断时，这些内核线程就会协助处理它们。这些线程运行在最低的优先级，避免与其它重要的任务抢夺资源，但是总归会运行。

这组线程主要有两个大循环，外层的循环处理有软中断就处理，没有就休眠。内循环每次试探一次是否占用CPU时间过长，如果是就释放CPU给其他进程。

```c
//代码来源与参考[1]
    set_current_state(TASK_INTERRUPTIBLE);
    //外层大循环。
    while (!kthread_should_stop()) {
        preempt_disable();//禁止内核抢占，自己掌握cpu
        if (!local_softirq_pending()) {
            preempt_enable_no_resched();
            //如果没有软中断在pending中就让出cpu
            schedule();
            //调度之后重新掌握cpu
            preempt_disable();
        }

        __set_current_state(TASK_RUNNING);

        while (local_softirq_pending()) {
            /* Preempt disable stops cpu going offline.
               If already offline, we'll be on wrong CPU:
               don't process */
            if (cpu_is_offline((long)__bind_cpu))
                goto wait_to_die;
            //有软中断则开始软中断调度
            do_softirq();
            //查看是否需要调度，避免一直占用cpu
            preempt_enable_no_resched();
            cond_resched();
            preempt_disable();
            rcu_sched_qs((long)__bind_cpu);
        }
        preempt_enable();
        set_current_state(TASK_INTERRUPTIBLE);
    }
    __set_current_state(TASK_RUNNING);
    return 0;

wait_to_die:
    preempt_enable();
    /* Wait for kthread_stop */
    set_current_state(TASK_INTERRUPTIBLE);
    while (!kthread_should_stop()) {
        schedule();
        set_current_state(TASK_INTERRUPTIBLE);
    }
    __set_current_state(TASK_RUNNING);
    return 0;
```

#### 使用软中断

软中断保留给系统中对时间要求最严格以及最重要的下半部使用。内核定时器和tasklet都是建立在软中断之上。

**1. 分配索引**

在编译期间，通过\<linux/interrupt.h\>中定义的一个枚举类型来静态地声明软中断。内核用这些从0开始的索引来表示一种相对优先级，索引小的先于索引大的执行。

![image-20201024000421258](https://raw.githubusercontent.com/xiaoqixian/Tiara/master/img/image-20201024000421258.png)

**2. 注册处理程序**

运行时通过`open_softirq()` 注册软中断处理程序，接收两个参数：软中断索引号和处理函数。

软中断处理程序执行时，允许响应中断，但不能休眠。在一个处理程序运行的时候，该处理器上的软中断被禁止，但其它处理器的软中断可以运行。这就导致任何共享数据都需要严格的锁保护。如果在软中断也使用锁保护就没有使用软中断的必要了，所以大部分软中断都通过采取仅属于某个处理器的数据来避免加锁，以获取更高的性能。

#### 触发软中断

通过在枚举类型中添加新项以及调用 `open_softirq()` 注册之后，中断处理程序就可以投入运行了。

`raise_softirq()` 可以将一个软中断设置为挂起状态，在下一次调用 `do_softirq()` 时就可以投入运行。

该函数在调用时会禁用处理器的中断，如果已经确定处理器的中断已经被禁止，则可以调用 `raise_softirq_irqoff()` 来带来一些性能优化。

### tasklet

tasklet 是一种软中断实现、行为与软中断类似、性能要求不如软中断的下半部机制。

大部分情况下使用 tasklet 都能获得不错的效果。

#### tasklet 特性

-   一种特定类型的 tasklet 只能运行在一个CPU上，只能串行执行；
-   多个不同类型的 tasklet 可以并行在多个 CPU 上；
-   tasklet 可以在运行时改变（比如添加模块）

#### tasklet的实现

**1. tasklet 结构体**

```c
struct tasklet_struct {
    struct tasklet_struct* next; //链表中下一个tasklet，多个tasklet链接而成的单向循环链表
    unsigned long state; //tasklet状态
    atomic_t count; //引用计数器
    void (*func)(unsigned long); //tasklet处理函数
    unsigned long data; //参数
}
```

state 成员只能在0、TASKLET_STATE_SCHED 和 TASKLET_STATE_RUN 之间取值。分别表示没有被调度、已被调度正要投入运行和正在运行。

count 成员是tasklet 的引用计数器，如果不为0，则tasklet不允许执行。

**2. 调度tasklet**

tasklet由 `tasklet_schedule()` 和 `tasklet_hi_schedule()` 两个函数进行调度，分别调度两个不同级别的 `tasklet` 。

`tasklet_schedule()` 的实现细节：

1.  检查 `tasklet` 的状态是否为 `TASKLET_STATE_SCHED`，如果是，说明已经被调度过了，函数返回；
2.  调用 `_tasklet_schedule()`
3.  保存中断状态，然后禁止本地中断；
4.  把需要调度的 `tasklet` 加到每个处理器一个 `tasklet_vec` 链表或 `tasklet_hi_vec` 链表上；
5.  唤起 `TASKLET_SOFTIRQ` 或 `HI_SOFTIRQ` 软中断，在下一次调用 `do_softirq()` 时就会执行该 `tasklet`；
6.  恢复中断到原状态并返回

#### tasklet 操作

```c
// 代码和注释来源于参考[1]
static inline void tasklet_disable(struct tasklet_struct *t)
//函数暂时禁止给定的tasklet被tasklet_schedule调度，直到这个tasklet被再次被enable；若这个tasklet当前在运行, 这个函数忙等待直到这个tasklet退出
static inline void tasklet_enable(struct tasklet_struct *t)
//使能一个之前被disable的tasklet；若这个tasklet已经被调度, 它会很快运行。tasklet_enable和tasklet_disable必须匹配调用, 因为内核跟踪每个tasklet的"禁止次数"
static inline void tasklet_schedule(struct tasklet_struct *t)
//调度 tasklet 执行，如果tasklet在运行中被调度, 它在完成后会再次运行; 这保证了在其他事件被处理当中发生的事件受到应有的注意. 这个做法也允许一个 tasklet 重新调度它自己
tasklet_hi_schedule(struct tasklet_struct *t)
//和tasklet_schedule类似，只是在更高优先级执行。当软中断处理运行时, 它处理高优先级 tasklet 在其他软中断之前，只有具有低响应周期要求的驱动才应使用这个函数, 可避免其他软件中断处理引入的附加周期.
tasklet_kill(struct tasklet_struct *t)
//确保了 tasklet 不会被再次调度来运行，通常当一个设备正被关闭或者模块卸载时被调用。如果 tasklet 正在运行, 这个函数等待直到它执行完毕。若 tasklet 重新调度它自己，则必须阻止在调用 tasklet_kill 前它重新调度它自己，如同使用 del_timer_sync 
```

### 工作队列

从上面的介绍看以看出，软中断运行在中断上下文中，因此不能阻塞和睡眠，而tasklet使用软中断实现，当然也不能阻塞和睡眠。但如果某延迟处理函数需要睡眠或者阻塞呢？没关系工作队列就可以如您所愿了。
把推后执行的任务叫做工作（work），描述它的数据结构为work_struct ，这些工作以队列结构组织成工作队列（workqueue），其数据结构为workqueue_struct ，而工作线程就是负责执行工作队列中的工作。系统默认的工作者线程为events。
工作队列(work queue)是另外一种将工作推后执行的形式。工作队列可以把工作推后，交由一个内核线程去执行—这个下半部分总是会在进程上下文执行，但由于是内核线程，其不能访问用户空间。最重要特点的就是**工作队列允许重新调度甚至是睡眠**。<font size = 2> 这段引自参考[1] </font>



---

### 参考

\[1\]  [Linux软中断、tasklet和工作队列](https://www.cnblogs.com/alantu2018/p/8527205.html)