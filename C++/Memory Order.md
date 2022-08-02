# Memory Order

### I. 内存一致性和内存持久性

现代操作系统的同一个进程的不同线程是有可能跑在不同CPU核心上的，而现代计算机虽然不同CPU核心共享内存，但是都各自的缓存（至少1、2级缓存）。核心在读写变量时，如果能够命中缓存，就不会再从内存取数据。这就导致可能 核心 A 在更新某个变量之后，核心 B 还是在使用 cache 中的旧值，带来内存一致性的问题。

一般来说，满足如下三个条件的内存系统是具有一致性的：

1. 对于同一地址 X, 若处理器 P 在写后读，并且在 P 的写后没有别的处理器写 X，那么 P 的读总是能返回 P 写入的值。
2. 处理器 P1 完成对 X 的写后，P2 读 X. 如果两者之间相隔时间足够长，并且没有其他处理器写 X, 那么 P2 可以获得 P1 写入的值。
3. 对于同一地址的写操作是串行的，在所有处理器看来，通过不同处理器对X的写操作都是以相同次序进行的。

### II. 内存一致性模型

#### 2.1 严格一致性模型 (Strict Consistency Model)

严格一致性模型是一致性最强的模型，其要求任何处理器对变量的写入都立即对其它处理器可见，即在该变量对所有处理器可见之前不允许插入其它操作。

#### 2.2 串行一致性模型 (Sequential Consistency Model)

串行一致性模型的一致性弱于严格一致性模型，其也是很多系统默认的一致性模型。对于串行一致性模型，当线程2获取线程1的 store 操作的结果时，线程1在该store 操作之前的所有操作也必须对线程2可见。

```
-Thread 1-       -Thread 2-
 y = 1            if (x.load() == 2)
 x.store (2);        assert (y == 1)
```

正常来说，线程1中两个写操作没有关系，因此可能存在两个写操作的乱序，在线程2中可能存在 assert 失败的情况。而如果是串行一致性模型，在 x load 时，就保证了 y =1 这个发生在 x.store(2) 之前的操作对于线程2已经完成，因此不会发生 assert 失败的情况。

#### 2.3 宽松一致性模型 (Relaxed Consistency Model)

宽松一致性模型移除了串行一致性模型中的*之前发生*的限制，唯一强制的顺序是一旦线程1中的某个变量被线程2看见，该变量之前的值对线程2都不可见。

```c++
-Thread 1-
x.store (1, memory_order_relaxed)
x.store (2, memory_order_relaxed)

-Thread 2-
y = x.load (memory_order_relaxed)
z = x.load (memory_order_relaxed)
assert (y <= z)
```

如上，assert 不可能失败，不可能存在 y 取到 x = 2 而 z 取到 x = 1 的情况。

宽松模式最常用当程序员仅仅希望一个变量是原子性的，而不是用于在不同线程之间同步内存数据。

#### 2.4 Acquire/Release

acquire/release 模式类似于串行一致性模式，但是其仅仅在相依赖的变量间要求 *先后发生* 的顺序关系。

```c++
 -Thread 1-
 y.store (20, memory_order_release);

 -Thread 2-
 x.store (10, memory_order_release);

 -Thread 3-
 assert (y.load (memory_order_acquire) == 20 && x.load (memory_order_acquire) == 0)

 -Thread 4-
 assert (y.load (memory_order_acquire) == 0 && x.load (memory_order_acquire) == 10)
```

线程3和4的 assert 是有可能成功的，因为线程1和2之间并没有顺序之分。

#### 2.3 因果一致性模型 (Causal Consistency Model)

因果一致性模型是对串行一致性模型的弱化，其将所有的事件分成因果相关的和非因果相关的，其定义只有写操作是因果相关的，需要对所有处理器保持相同的顺序。

满足下列条件的一致性模型可以被认为符合因果一致性：

- 潜在因果相关的写操作必须被所有处理器以相同的顺序看到
- 并发的写入在不同机器上可能有不同的顺序

因果一致性模型放宽了处理器并发写入和非因果写入的一致性顺序。

#### 2.4 处理器一致性模型 (Processor Consistency Model)

#### 2.3 松弛一致性模型 (Relaxed Consistency Model)

### III. C++ Memory Order



#### Relaxed ordering

