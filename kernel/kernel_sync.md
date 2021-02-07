---
author: lunar
date: Mon 26 Oct 2020 09:04:32 PM CST
location: Shanghai
---

## 内核同步介绍

用户空间之所以需要同步，是因为用户程序会被调度程序调度抢占和重新调度。由于用户进程可能在任何时刻被抢占，而调度程序完全可能选择另一个高优先级的进程到处理器上运行，所以就似的一个程序正处于临界区时，被非自愿地抢占了，如果新调度的程序随后也进入了同一个临界区，前后两个进程就产生了竞争。

在linux内核中，会导致并发bug的原因不止是多个线程共同工作，包括：
- 中断——中断可能随时打断当前正在执行的代码
- 软中断和tasklet——内核可以在任何时刻唤醒或调度软中断和tasklet，
- 内核抢占 —— 内核中执行的任务也可能被另一个任务抢占
- 睡眠与用户空间同步 —— 在内核执行的进程可能会睡眠，导致唤醒调度程序。
- 对称多处理(Symmetrical Multi-Processing, SMP) —— 多个处理器可能同时执行一段代码

并发程序设计最大的难点在于如何识别出真正需要共享的数据和相应的临界区。

### 原子操作

内核提供了两组原子操作 —— 一组针对整数进行操作，另一组针对单独的位进行操作。

#### 原子整数操作

针对整数的原子操作只能对`atomic_t`类型的数据进行处理。

```c
typedef struct {
    volatile int counter;
} atomic_t;
```

volatile 关键字可以使得编译器不对相应的值进行访问优化，也就是每次读值时都从内存中读取最新值。

尽管Linux支持的所有机器上的整数类型都是32位，但是使用`atomic_t`的代码只能当作24位来使用，这是为了兼容SPARC体系结构。SPARC体系结构对原子操作缺乏指令级别的操作，所以只能在`atomic_t`的低八位加锁来支持原子操作。

原子类型常用操作：

![image-20201027101348827](https://raw.githubusercontent.com/xiaoqixian/Tiara/master/img/image-20201027101348827.png)

原子操作通常是内联函数，往往是通过内联汇编指令来实现的。

在编写代码时，可以使用原子操作就尽量不要用复杂的加锁机制，系统开销更小。

#### 64位原子操作

为了能够兼容32位系统，`atmomic_t` 类型即使在64位系统下也是32位的。如果想要使用64位的原子操作，可以使用`atmoic64_t`

```c
typedef struct {
    volatile long counter;
} atomic64_t;
```

![image-20201027104205264](https://raw.githubusercontent.com/xiaoqixian/Tiara/master/img/image-20201027104205264.png)

#### 原子位操作

原子的位操作是直接对一个指针进行原子操作的，所以没有定义任何特殊的类型。

![image-20201027104427208](https://raw.githubusercontent.com/xiaoqixian/Tiara/master/img/image-20201027104427208.png)

在所有原子位操作函数的名字前加上\_\_ 就变成了非原子位操作。

### 自旋锁（Spin Lock）

我们在写代码时经常会遇到这种情况：从一种数据结构中取出数据，对其进行格式转换和解析，然后移入到另一个数据结构中。这种复杂的操作使用原子操作显然是无能为力的。只能通过加锁来实现。

自旋锁是linux内核中最常见的一种锁。自旋锁只能被一个可执行线程所拥有，如果有线程要抢占一个已经被占有的自旋锁，则其会一直进行循环来等待锁重新可用。当锁被释放后，请求锁的执行线程便能立刻得到它。

自旋锁只适用于那些在临界区停留很短时间的加锁操作。因为线程在等待锁期间会一直占据处理器，如果长时间等待锁会导致处理器效率降低。而如果线程占用锁只需要短暂的执行一下，那么使用自旋锁更优，因为不需要进行上下文的切换。

#### 自旋锁方法

自旋锁的实现与体系结构密切相关，代码往往通过汇编实现。基本使用形式如下：

```c
DEFINE_SPINLOCK(sp_lock);//定义一个自旋锁sp_lock
spin_lock(&sp_lock);
//临界区
spin_unlock(&sp_lock);
```

在单处理器机器上，编译的时候并不会加入自旋锁。

注意：在已经抢占到了自旋锁的代码中，**不能再调用自旋锁的抢占**，这样会造成系统死锁。

另外，在中断处理程序中使用自旋锁时，**一定要在获取锁之前禁止本地中断**。否则，中断处理程序有可能会打断持有锁的代码，万一这个中断处理程序再请求锁，就会造成中断处理程序不断自旋。而锁的持有者因为被抢占而不可能释放锁，从而造成死锁。

因此，在自旋锁中不允许睡眠。因为睡眠要依赖时钟调度，时钟依赖中断来唤醒程序，但是自旋锁又禁止了所有本地中断，所以睡眠后的进程无法被唤醒。反正，在linux内核中，禁止中断的时候都不允许睡眠，不然就睡死过去了。

所幸，内核提供禁止中断同时请求锁的借口：

```c
DEFINE_SPINLOCK(sp_lock);
unsigned long flags;

spin_lock_irqsave(&sp_lock, flags);
//临界区
spin_unlock_irqrestore(&sp_lock, flags);
```

`spin_lock_irqsave` 保存中断的当前状态，并禁止本地中断，然后获取锁。`spin_unlock_irqrestore` 释放锁并恢复到加锁前的中断状态。所以即使在加锁前本地中断就已经被禁止，这个接口也只会保持禁止的状态使用。使用后继续保持禁止。

#### 其他针对自旋锁的操作

`spin_try_lock()` ：试图获取一个自旋锁，如果获取不到，则马上返回一个非0值，不会自旋等待。获取到了就返回0

`spin_is_locked()`：检查自旋锁是否已被占用，没有上面那个实用。

### 读-写自旋锁

读-写自旋锁是内核提供的专门应对读-写这种场景的自旋锁，这种应用场景有一个特点：当有线程正在写入时，只能有一条写线程进入临界区；当有线程读取时，可以有任意多的读线程进入临界区，但是不允许任何写线程进入临界区。有时，为了保证数据的及时更新，即使临界区有多条读线程正在工作，但是只要写线程到达，就要立刻释放锁。

内核提供了以下接口来使用读-写锁：

![image-20201027144941895](https://raw.githubusercontent.com/xiaoqixian/Tiara/master/img/image-20201027144941895.png)

注意，读锁和写锁的使用要在完全不同的代码段中。不能像下面这样，读锁还没有释放就去请求写锁：

```c
DEFINE_RWLOCK(rw_lock);
read_lock(&rw_lock);
write_lock(&rw_lock);
```

`write_lock`的调用会导致整段代码都陷入自旋之中，从而导致读锁永远无法释放，陷入死锁。反过来也是一样。

如果是连续两次请求读锁的话，则是没有关系的。因为只要读锁被占用，则读锁的请求总是会成功，不会发生阻塞。

### 信号量

信号量是一种睡眠锁。当有任务试图获得一个已被占用的信号量时，信号量就会将其推进一个等待队列，然后使其睡眠。当信号量被释放后，处于等待队列的任务将会被唤醒继续执行。

显然，信号量适用于长时间占用锁的情形。

#### 计数信号量和二值信号量

信号量有一个有用的特性：它可以允许任意数量的锁持有者。同时允许持有的数量可以在创建信号量时指定。

#### 创建和初始化信号量

```c
struct semaphore name;
sema_init(&name, count);
```

#### 使用信号量

试图获取信号量的操作称为 down 操作。

在linux内核内，有三种函数用于获取一个信号量，分别对应三种应用场景：

-   down_interruptible(): 获取一个信号量，如果信号量为负数，则进程会进入TASK_INTERRUPTIBLE 状态
-   down(): 获取一个信号量，如果信号量为负数，则进程会进入TASK_UNINTERRUPTIBLE 状态。这个函数应用不是很普遍。
-   down_trylock(): 非阻塞地获取一个信号量，返回非0值说明没有获取到信号量

![image-20201028135424574](https://raw.githubusercontent.com/xiaoqixian/Tiara/master/img/image-20201028135424574.png)

### 读-写信号量

静态声明读-写信号量：

```c
static DECLARE_RWSEM(name);
```

动态初始化：

```c
struct rw_semaphore sem;
init_rwsem(struct rw_semaphore* sem);
```

四个操作函数

```c
down_read(&sem); //获取读信号量
up_read(&sem); //释放读信号量
down_write(&sem); //获取写信号量
up_write(&sem); //释放写信号量
```

读-写信号量相比读-写自旋锁多出来的一种操作是：`downgrade_write()`，可以动态地将获取的写锁转换为读锁。

### 互斥量 mutex

互斥量在内核中被用作一种**可以睡眠的强制互斥量**

![image-20201028141921753](https://raw.githubusercontent.com/xiaoqixian/Tiara/master/img/image-20201028141921753.png)

### 完成变量 Completion Variable

完成变量用于两个进程的同步，当一个任务要执行一些工作时，另一个任务会在完成变量上等待，当这个任务完成后，会使用完成变量去唤醒在等待的任务。

完成变量使用结构体`completion`来表示

![image-20201028144931587](https://raw.githubusercontent.com/xiaoqixian/Tiara/master/img/image-20201028144931587.png)

### 禁止抢占

从前面我们知道，在使用自旋锁时需要关闭内核抢占。但是在一些情况下，就算不用自旋锁，也要关闭内核抢占。

比如，对于只有一个处理器能够访问到数据，原理上是没有必要加自旋锁的，因为在任何时刻数据的访问者永远只有一位。但是，如果内核抢占没有关闭，则可能一个新调度的任务就可能访问同一个变量。

所以这时候害怕的不是多个任务访问同问同一个变量，而是一个任务的访问还没有完成就转到了另一个任务。

![image-20201028162436007](https://raw.githubusercontent.com/xiaoqixian/Tiara/master/img/image-20201028162436007.png)