# Mini-Tokio

Tokio 是 Rust 中一个非常著名的关于异步编程的库。在其文档里，通过一个非常mini的tokio实现讲述了rust中异步编程的实现方式。

### Task

```rust
struct Task {
  future: Mutex<Pin<Box<dyn Future<Output = ()> + Send>>>,
  executor: channel::Sender<Arc<Task>>
}
```

每个 Task 结构体表示一个需要完成的task，每个task在分配之后并不会立刻执行，而是由一个统一的调度器进行分配，将任务传送给调度器的过程是由一个channel来完成的，这里的channel 来自于 crossbeam crate。

#### spawn

Task 通过 spawn 函数来创建一个新的 task。

```rust
    fn spawn<F>(future: F, sender: &channel::Sender<Arc<Task>>)
    where
        F: Future<Output = ()> + Send + 'static,
    {
        let task = Arc::new(Task {
            future: Mutex::new(Box::pin(future)),
            executor: sender.clone(),
        });

        let _ = sender.send(task);
    }
```

创建的task通过管道发送到 executor 进行统一的调度。

#### poll

executor 实际要执行一个task时是通过调用task的poll函数进行的。

```rust
    fn poll(self: Arc<Self>) {
        // Get a waker referencing the task.
        let waker = task::waker(self.clone());
        // Initialize the task context with the waker.
        let mut cx = Context::from_waker(&waker);

        // This will never block as only a single thread ever locks the future.
        let mut future = self.future.try_lock().unwrap();

        // Poll the future
        let _ = future.as_mut().poll(&mut cx);
    }
```

由于Task相当于一个Future类型的wrap，调用task的poll函数就相当于调用对应Future的poll函数。

