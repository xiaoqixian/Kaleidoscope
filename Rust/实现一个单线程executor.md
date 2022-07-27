# 实现一个单线程executor

### Rust Standard Support

在Rust中，最重要的三个struct/trait 显然是：

- Future
- Context
- Waker

其中 Future 是一个trait，通常表示可以在未来某个时刻执行的computation，一个async block 可以是Future，一个被调用的 async fn 也可以是Future，当然一个自定义的实现了Future的struct也可以是Future。

```rust
pub trait Future {
    type Output;
    fn poll(self: Pin<&mut Self>, cx: &mut Context<'_>) -> Poll<Self::Output>;
}
```

`poll` 形式上是一个普通的函数，其是对于一段 computation 是否完成的询问的抽象。如果还在等待IO或其他，则返回 `Poll::Pending`；否则返回 `Poll::Ready`。

显然只有Future并不能体现Rust的异步编程特性，否则就只能不断轮询poll来判断是否已经完成computation。因此需要引入 Waker 来让对应的 Future 自动唤醒自己，所谓的自动唤醒就是由异步程序告诉 executor 自己已经 `Poll::Ready` 了，可以继续执行。这一步就是由 Waker 来完成。

可以从tokio文档中实现的 delay 函数来分析这个过程，本质是通过 delay 函数来模拟等待 IO 的过程，但是由不希望等待 IO 时阻塞当前线程，也不希望需要通过轮询是否完成。

```rust
impl Future for Delay {
  type Output = ();
  fn poll(mut self: Pin<&mut Self>, cx: &mut Context<'_>) -> Poll<()> {
    if let Some(waker) = &self.waker {
      let mut waker = waker.lock().unwrap();

      if !waker.will_wake(cx.waker()) {
        *waker = cx.waker().clone();
      }
    } else {
      let when = self.when;
      let waker = Arc::new(Mutex::new(cx.waker().clone()));
      self.waker = Some(waker.clone());

      thread::spawn(move || {
        let now = Instant::now();

        if now < when {
          thread::sleep(when - now);
        }

        let waker = waker.lock().unwrap();
        waker.wake_by_ref();
      });
    }

    if Instant::now() >= self.when {
      Poll::Ready(())
    } else {
      Poll::Pending
    }
  }
}

```

 else 块里面的语句为第一次被poll时的逻辑，Delay 将创建一个新线程并阻塞需要delay 的时间，这样做的好处是既不会阻塞当前的线程，还能满足在 delay 一段时间之后将当前的 Future 唤醒。唤醒调用的函数就是 `wake_by_ref`，`wake_by_ref` 和 `wake` 的区别很小，后面只解释 `wake` 函数。

`wake` 是 Waker 的一个成员函数，而Waker 其实是一个 RawWaker 的 wrap，所以直接看 RawWaker。RawWaker 的定义非常有C语言的风格，分别用一个指针指向数据和一个结构体包含所有需要的函数指针。

```rust
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

因此调用 Waker 的 wake 函数将相当于调用函数指针 `(wake)(data)`。

问题来了，查遍了标准库文档之后，你会发现Rust在标准库中并没有提供创建 Waker 实例的方法，在找到的几个说明Rust异步的示例中，均需要使用 futures-rs 这个第三方库才能得到 Waker。

原因就在于Rust标准库并没有提供一套异步编程的调度器，Rust 选择将 Task 唤醒的工作交给 executor 完成，因为每个 executor 在唤醒时需要完成的工作不同，比如单线程 executor 和多线程的就不同。

### FuturesUnordered

FutureUnordered 用于管理大量的Future，由其管理的Future只会在产生wake-up提醒时被poll。

```rust
pub struct FuturesUnordered<Fut> {
    ready_to_run_queue: Arc<ReadyToRunQueue<Fut>>,
    head_all: AtomicPtr<Task<Fut>>,
    is_terminated: AtomicBool,
}
```

在 FutureUnordered 内部通过一个Task链表管理所有传入的Future，并通过一个 ready_to_run_queue 来管理所有需要被poll的Future。

```rust
pub(super) struct Task<Fut> {
    pub(super) future: UnsafeCell<Option<Fut>>,
    pub(super) next_all: AtomicPtr<Task<Fut>>,
    pub(super) prev_all: UnsafeCell<*const Task<Fut>>,
    pub(super) len_all: UnsafeCell<usize>,
    pub(super) next_ready_to_run: AtomicPtr<Task<Fut>>,
    pub(super) ready_to_run_queue: Weak<ReadyToRunQueue<Fut>>,
    pub(super) queued: AtomicBool,
    pub(super) woken: AtomicBool,
}
```

由于FutureUnordered是多线程和单线程executor通用，所以许多变量类型都是采用的原子变量。

通过调用 FutureUnordered 的 poll_next 方法可以遍历 ready_to_run_queue 中的所有Task，每次遍历从 ready_to_run_queue 中取出一个Task，同时也将其从链表中取下，poll之后根据结果

- Poll::Pending: 将Task重新装回链表，如果已经poll了所有的Task，则通过 poll_next 传入的waker进行唤醒，表明当前所有的Task已经poll过一遍了，如果是多线程executor，通常需要unpark executor线程，但是这里是单线程，所以 poll_next 和 executor 其实是运行于同一个线程。
- Poll::Ready: 当前的 Task 完成返回，为了保存返回结果，需要立即返回。

根据 poll_next 的逻辑，最终的返回结果可以分为以下几种类型：

- Poll::Pending：ready_to_run_queue 为空，而 Task 链表不为空，说明当前无需要 poll 的Task；第二种情况就是 ready_to_run_queue 不为空，但是所有的 Task 被 poll 之后都返回 Pending
- Poll::Ready(Some(\_))：如前文所说，存在某个 Task 返回 Ready
- Poll::Ready(None)：所有的 Task 都已经执行完毕

