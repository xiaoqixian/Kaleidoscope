# C++ Async

#### future

​	`std::future<T>` 类型提供了一种异步操作结果的访问机制，可以通过以下方法来获取异步操作状态：

- `get`: 阻塞等待函数完成，返回结果
- `wait`: 阻塞等待函数完成，但无返回结果
- `wait_for`: 等待函数一定时间，当函数完成或时限到达时返回一个 `future_status`:
  - `future_status::defered`: `future` 中包含一个 lazy evaluation 函数，只有在调用 `get` 时才会开始运行
  - `future_status::ready`: 函数已完成
  - `future_status::timeout`: 时限到达，函数未完成
- `wait_until`: 与 `wait_for` 相似，只是参数为某个具体的时间点

#### shared_future

​	`std::shared_future<T>` 允许多线程同时共享一个 `future`，可以看作一个 `shared_ptr`。`shared_future` 由 `future` 调用 `share` 方法转化而来。

#### promise

​	`std::promise<T>` 类型提供了一种类似管道的线程间通信机制，线程1可以创建一个 `promise` 后共享给线程2，线程2可以向 `promise` 传入必要的数据，而线程1可以通过已经提前通过 `get_future` 方法创造的 `future` 等待获取该数据。当然数据流动的方向也可以反过来，与管道不同的是 `promise` 被设计为仅使用一次。

- `get_future`：获取对应的 `future`，`future` 相当于一个获取数据的入口
- `set_value`: 传入数据
- `set_exception`: 传入异常

#### packaged_task

```c++
template <typename> class packaged_task;
template <typename F, typename... Args>
class packaged_task<R(Args...)>;
```

​	`packaged_task` 打包了一个函数对象及其参数，这使得其可以在任何时间运行。

#### launch

​	`std::launch` 定义了两种异步执行的方式，一种用于在另一个线程中执行，一种用于缓执行，即在需要数据的时候执行。

```cpp
enum class launch {
    async = 1, //真正的异步
    defered = 2, //缓执行
    any = async | defered
};
```

---

### Coroutines (C++20)

​	corountine 是 C++20 引入的无栈协程，这意味着协程的执行数据存储在栈之外。任何含有以下三个关键字之一的表达式的函数可看作一个协程。

- `co_await`: 中断当前执行，进入另一个异步函数
- `co_yield`: 中断当前执行，返回一个值
- `co_return`: 完成执行，返回一个值

每个协程都关联了以下数据：

- `promise`： 用于协程提交数据或异常给调用者
- `coroutine handle`: 用于从外部恢复或撤销协程
- `coroutine state`: 内部数据，动态分配，主要包括
  - `promise` 对象
  - 参数（值复制）
  - 中断点：以方便恢复运行或析构域内变量
  - 局部变量

当开始一个协程时，其会执行以下过程：

- 分配一个新的协程对象
- 复制所有参数：值参数则复制或移动，引用参数则引用
- 创建一个 `promise` 对象
- 调用 `promise.get_return_object()` 并将结果保存到某个局部变量中，这次调用的结果会在协程第一次暂停时返回给协程发起者，包括任何异常也会返回给发起者。
- 调用 `promise.initial_suspend()`，然后 `co_await` 结果。典型的 `Promise` 对象会要么返回 `std::suspend_always` 给缓执行协程 (lazily-started coroutines)，或返回 `std::suspend_never` 给急执行协程 (eagerly-started coroutines)。
- 从 `promise.initial_suspend` 中恢复执行，协程正式开始执行函数。

#### co_await

​	