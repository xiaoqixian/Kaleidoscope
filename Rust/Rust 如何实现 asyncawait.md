# Rust 如何实现 async/await

异步编程在 Rust 中的地位非常高，很多 crate 尤其是多IO操作的都使用了 async/await.

首先弄清楚异步编程的几个基本概念：

### Future

Future 代表一个可在未来某个时候获取返回值的 task，为了获取这个 task 的执行状况，Future 提供了一个函数用于判断该 task 是否执行返回。

```rust
trait Future {
  type Output;
  fn poll(self: Pin<&mut self>, cx: &mut Context<'_>) -> Poll<Self::Output>;
}
```

poll 函数就是一个 Future 用于检查自己的 task 是否已经完成，例如我可以创建一个与某个 IP 建立 TCP 连接的 struct，在构建时完成建立连接的工作，然后实现 Future trait 时检查连接是否已经建立完成。根据建立情况返回 enum Poll 中的两个元素之一：

- Poll::Pending: task 还在等待
- Poll::Ready(result): task 携带 result 返回

实际上，基于 async 定义的函数和代码块也会被编译器编译为 Future。但是 async 函数或代码块无法显式地返回 Pending，因此一般只能完成一些简单的调用其他 Future 的工作。复杂的异步过程通常还是交由实现了 Future trait 的类型完成。

### Wake & Context

你可能会好奇上面 poll 函数签名里的 cx 参数的作用，在 Rust 官方文档的定义中，Context 暂时只用于获取 Waker，而 Waker 的作用是用于提醒 executor 该 task 已经准备好运行了。

#### 为什么需要 executor ？  

同样以上面的建立 TCP 连接的例子来说，在网络卡顿时，进行一次 poll 可能都没有建立连接，如果没有设置 timeout 之类的东西的话，就需要进行多次 poll。这样的 Future 多了以后，我们可能会想，不妨将所有的 Future 都存储在一起，然后另起一个线程用于循环遍历所有的 Future 是否已经 ready，如果 ready 则返回结果。这就是一个非常简单的单线程 executor 的雏形。

也就是说，executor 是一个托管运行 task 的工具，类似于多线程，多线程要成功运行需要一个调度器进行调度。但是多线程至少需要语言层面甚至操作系统层面的支持，而 executor，如果你翻看 Rust 的官方文档的话，会发现没有任何关于 executor 的实现。实际上，Rust 选择将 executor 的实现交给第三方，自己只保留相关的交互接口（我在隔壁C++看了看，似乎也是一样的做法，并没有一个官方的 executor 实现，我唯一所知的在语言层面提供支持的只有Golang 的 goroutine）。

#### 什么是 waker ？

上面讲述的轮询所有的 Future 是否已经完成实际是最低效的一种做法，当 Future 多了以后会带来相当多的 CPU 损耗。考虑到这点，Rust 还提供了一种机制可以用于通知 executor 某个 Future 是否应该被轮询，当然这只是其中的一种解决方式，实际上 Waker 的 wake 函数可以被实现为任何逻辑，取决于 executor。

在我看来，Waker 的内部定义相当不简洁，相当不 Rust。Waker 内部定义有一个 RawWaker，RawWaker 包含一个 RawWakerVTable，RawWakerVTable 定义了四个函数指针，executor 要实现 Waker 就需要定义这四种类型的函数然后赋值给 RawWakerVTable。

```rust
struct Waker {
  waker: RawWaker
}
struct RawWaker {
  data: *const (),
  vtable: &'static RawWakerVTable
}
struct RawWakerVTable {
  clone: unsafe fn(*const ()) -> RawWaker,
  wake: unsafe fn(*const ()),
  wake_by_ref: unsafe fn(*const ()),
  drop: unsafe fn(*const ())
}
```

之所以没有设计为 trait 形式，主要是 clone 函数，受限于 Rust 的 trait object safety，trait 中的任何函数的参数或返回值如果包含 Self 且有 type bound Sized，则不符合 trait object safe 规范，这样的 trait 可以被定义，可以被实现，但是无法与 dyn 一起进行动态绑定。

而 clones 函数又是必须的，因为 future 可能还会接着调用 future 的 poll 方法，就需要再 clone 一个 context 传入。

或许可以用 `Box<dyn Waker>` 或者 `Arc<dyn Waker>` 之类的，但是这些都不比 raw pointer 灵活，所以最终 Rust 还是选择定义一个包含函数指针的 struct。

### async/await

这两个关键字可以说是异步编程领域的标志。，但在 Rust 中这两个关键字只是起到语法糖的作用，并不是异步的核心。

async 用于快速创建 Future，不管是函数还是代码块或者lambda表达式，都可以在前面加上 async 关键字快速变成 Future。对于

```rust
async fn bar() {
  foo().await;
}
```

编译器会自动生成类似下面的代码

```rust
fn bar() -> impl Future {
    std::future::from_generator(move |mut _task_context| {
        let _t = {
            match std::future::IntoFuture::into_future(foo()) {
                mut __awaitee => loop {
                    match unsafe {
                        std::future::Future::poll(
                            std::pin::Pin::new_unchecked(&mut __awaitee),
                            std::future::get_context(_task_context),
                        )
                    } {
                        std::task::Poll::Ready { 0: result } => break result,
                        std::task::Poll::Pending {} => {}
                    }
                    _task_context = (yield ());
                },
            };
        };
        _t
    })
}
```

Tips：上面的代码可以在 Rust Playground 里面点生成 HIR 看到。

### Executor

前面讲到 wake 的时候，其实现与具体的 executor 相关，但是我觉得如果不从 executor 的实现角度看一下比较难以理解，只能浅显地知道 wake 是告诉 executor 准备再 poll 一遍。

Rust 中我知道的 async runtime lib 就是 futures-rs 和 tokio，前者在 GitHub 上是 rust-lang 官方组织推出的 repo，而后者虽然不清楚是否有官方参与，但是功能明显比前者丰富，据我所知使用异步的项目大部分都是使用 tokio。

我这里选择更简单的 futures-rs 讲一下其 executor 的实现，虽然其更加轻量但起码也是官方推出的，有质量保证。

#### Waker struct 到 ArcWake trait

futures-rs 还是将标准库里面的 Waker 封装成了 ArcWake trait，并且是 pub 的。和 raw pointer 打交道毕竟是 unsafe 的，与其满篇的 unsafe 乱飞，不如将 unsafe 限制在一定的范围内。

Waker 本质上是一个变量的指针(data)带着四个函数指针的结构体(RawWakerVTable)，因此在定义函数指针时只需要将指针强转成实现某个 trait 的泛型，再调用该 trait 的对应方法不就可以了。以 wake 函数为例：

```rust
trait Wake {
  fn wake(self) {
    Wake::wake_by_ref(&self);
  }
  fn wake_by_ref(&self);
}
unsafe fn wake<T: WakeTrait>(data: *const ()) {//对应RawWakerVTable里的函数指针
  let v = data.cast::<T>();
  v.wake();
}
```

这样就实现了 Waker struct 到 Waker trait 的转换。尽管如此，我们还需要一个结构体用来表示 Waker，满足下列条件：

- 实现 Deref trait，在引用时返回 &std::task::Waker
- 为了满足 Rust 的 safety rules，需要手动管理data的内存，显然某个实现了 Wake 的类型不会为了创建 waker 就交出自己的拥有权，因此只能通过传入的引用转成指针来创建 ManuallyDrop 实例，并考虑到 Deref trait 和后续的 Context 创建，需要通过 PhantomData 来管理 lifetime annotation

从而创建 WakeRef 结构体：

```rust
use std::mem::ManuallyDrop;
use std::task::Waker;
use std::marker::PhantomData;
struct WakeRef<'a> {
  waker: ManuallyDrop<Waker>,
  _marker: PhantomData<&'a ()>
}
```

如何根据引用创建 WakeRef 实例：

```rust
use std::task::{Waker, RawWaker};
fn get_waker<W: Wake>(wake: &W) -> WakeRef<'_> {
  let ptr = wake as *const _ as *const ();
  WakeRef {
    waker: ManuallyDrop::new(unsafe {Waker::from_raw(RawWaker::new(ptr, ...))}),//...省略的是创建RawWakerVTable的过程
    _marker: PhantomData
  }
}
```

实现 Deref

```rust
use std::task::Waker;
impl std::ops::Deref for WakeRef<'_> {
  type Target = Waker;
  fn deref(&self) -> &Waker {
    &self.waker
  }
}
```

因此对于某个实现 Wake 的类型来说，只需要传入引用就可以用 Context::from_waker(&waker) 来创建 context 了。

在 futures-rs 中，由于涉及到多线程，所以上述的其实并不安全，需要将普通引用改成 Arc 用于在多线程之间传递，Wake trait 也变成了 ArcWake，

```rust
trait ArcWake: Send + Sync {
  fn wake(self: Arc<Self>) {
    Self::wake_by_ref(&self)
  }
  
  fn wake_by_ref(arc_self: &Arc<Self>);
}
```

但是道理差不多。RawWakerVTable 的四个函数也与这个有关，以 wake 函数为例：

```rust
unsafe fn wake_arc_raw<T: ArcWake>(data: *const ()) {
  let arc: Arc<T> = Arc::from_raw(data.cast::<T>());
  ArcWake::wake(arc);
}
```

#### 单线程 executor

单线程 executor 允许在单线程上复用任意数量的 task，官方建议尽量在多I/O场景，只需要在 I/O 操作之间完成很少的工作的场景下使用。

在单线程 executor 中通过 FutureUnordered struct 来管理所有的 Future，其有一条链表维护所有的 Future，再通过一个队列维护所有需要运行的 Future（当然这里都不是 collections 里面那种普通的链表和队列，由于 FutureUnordered 其实要与线程池 executor 公用，所以这两个数据结构其实还涉及很多原子化操作，在保证原子化且无锁的前提下要自己设计一个链表还挺麻烦的）。

```rust
struct FutureUnordered<Fut> {
  ready_to_run_queue: Arc<ReadyToRunQueue<Fut>>,//需要运行的Future队列
  head_all: AtomicPtr<Task<Fut>>,//所有Future组成的链表
  is_terminated: AtomicBool
}
```

这里重点看 FutureUnordered 如何实现 Waker，FutureUnordered 将 Future 包装为 Task 使用。

```rust
struct Task<Fut> {
  future: UnsafeCell<Option<Fut>>,
  next_all: AtomicPtr<Task<Fut>>,//下一个Task节点
  len_all: UnsafeCell<usize>,//链表长度
  next_ready_to_run: AtomicPtr<Task<Fut>>,//下一个要运行的Task
  ready_to_run_queue: Weak<ReadyToRunQueue<Fut>>,
  queued: AtomicBool,//是否在Task链表内(Task运行时需要从链表上摘下)
  woken: AtomicBool//是否已经调用wake函数
}
```

