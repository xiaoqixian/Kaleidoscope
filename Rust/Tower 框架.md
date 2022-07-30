# Tower 框架

Tower 是一个专注于对网络编程进行抽象的框架，将网络编程中的各行为进行抽象从而提高代码复用率。

Tower 最核心的抽象为 Service trait，其接受一个 request 进行处理，成功则返回 response，否则返回 error。

```rust
async fn(Request) -> Result<Response, Error>
```

这个抽象可以同时运用于客户端和服务端。同时 Tower 也提供了 超时处理、访问频率限制和负载均衡之类的组件，这些功能可以被抽象为在 inner Service 调用之前和之后进行一些操作所共同组成的Service。这些 Service 称为中间件(middleware)。

Tower 库对 Service 的设计希望满足以下目标：

1. 能够满足异步编程的规范
2. 不同的 Service 能够灵活地层层嵌套
3. 我们在给一个 Service 递交 request 时，希望能够得到该 Service 的执行情况；如果该 Service 负载过重，则需要延缓提交 request 甚至直接丢弃 request，这一点类似于 Future 中的 poll 方法。

针对第一点，当 call 一个 Service 时，会直接返回一个 Future，由调用者决定怎么安排这个 Future，而不是要求实现了 Service trait 的结构体同时也实现 Future。

针对第二点，每个实现了 Service 的结构体自身可以继续携带一个 Service，只需要将 request 递交给里层的 Service，就实现了 Service 的嵌套，这样本结构体就成为了一个中间件。

针对第三点，在 Service 中定义了 `poll_ready` 方法用于获取一个 Service 的执行情况。

```rust
trait Service<Request> {
  type Response;
  type Error;
  type Future: Future<Output = Result<Self::Response, Self::Error>>;
  
  fn poll_ready(&mut self, cx: &mut Context<'_>) -> Poll<Result(), Self::Error>>;
  
  fn call(&mut self, req: Request) -> Self::Future;
}
```

#### 通过 Service trait 实现 Timeout 中间件

Timout 中间件用于对某个 request 的处理限定时间，如果超过时限还没有返回，则直接返回错误。Timout 应该有个用于进一步处理的里层serivce和一个时限。

```rust
struct Timeout<T> {
  service: T,
  duration: std::time::Duration
}
```

将 Timeout 也定义为一个 Service

```rust
impl<S, Request> Service<Request> for Timeout<S> 
where
	S: Service<R>,
	S::Error: Into<Box<dyn std::error::Error + Send + Sync>> 
```

`poll_ready` 非常好处理，直接将调用里层 Service 的 poll_ready 函数。

而 `call` 则要求返回一个 Future，如果要实现 Timeout 对应的行为逻辑，需要创建一个新的实现了 Future 的类型——ResponseFuture。我们希望它被poll时，首先会查看里层 Service 是否返回，如果已返回则返回结果，如果没有则检查是否已经timeout，如果没有则返回 Pending，如果已经超时则返回超时错误。

因此我们创建了一个融合了里层 future 和超时 future 的类型

```rust
#[pin_project]
struct ResponseFuture<F> {
  #[pin]
  response_future: F,
  #[pin]
  sleep: tokio::time::Sleep
}
```

pin_project 可以使得 Pin 类型的字段也是 Pin 类型，在调用 poll 函数时需要用到。

然后为 ResponseFuture 实现 Future trait

```rust
impl<F, Response, Error> Future for ResponseFuture<F> 
where
    F: Future<Output = Result<Response, Error>>,
    Error: Into<Box<dyn std::error::Error + Send + Sync>>
{
    type Output = Result<Response, Box<dyn std::error::Error + Sync + Send>>;
    fn poll(self: std::pin::Pin<&mut Self>, cx: &mut Context<'_>) -> Poll<Self::Output> {
        let this = self.project();

        match this.response_future.poll(cx) {
            Poll::Ready(res) => {
                let result = res.map_err(Into::into);
                return Poll::Ready(result);
            },
            Poll::Pending => {}
        }

        match this.sleep.poll(cx) {
            Poll::Ready(_) => {
                let error = Box::new(TimeoutError(()));
                Poll::Ready(Err(error))
            },
            Poll::Pending => Poll::Pending
        }
    }
}
```

### Balance 中间件

从名字就可以看出来，Balance 模块用于提供负载均衡的服务，负载均衡会根据所有服务的负载程度来决定处理 request 的服务。

在官方文档提供了两种 Balance 服务

- p2c：根据p2c算法 (Power of Two Random Choices) 实现，提供一种简单而大概的 service 选择方法，一般在无法精确每个 service 的负载时使用。
- pool：实现了一个动态大小的服务池 (service pool)，通过追踪每个 service 的 `poll_ready` 成功的次数来估计每个 service 的负载状况。（虽然这个模块还存在于官方文档之上，但是已经从最近的源码上移除了，显然官方打算移除这个模块，参见[#658](https://github.com/tower-rs/tower/pull/658)。

这里选择p2c算法进行分析。p2c 并非是一种挑选最优的算法，而是一种避免选到最坏的算法。其随机从所有 service 中选取两个，比较两个 service 的负载，选择较小的那个 service，从而保证避免选到负载最重的 service。这个算法在 nginx 中就有所运用。

Balance 内部通过 ready_cache 模块维护一个 Pending 队列和一个 Ready map，当 Service 陷入 Pending 状态时，则加入 Pending 队列中，新加入的 Service 一开始也是加入到 Pending 队列中。可以通过调用 `promote_pending_to_ready` 函数遍历所有的 Pending Service 将已经 Ready 的 Service 加入到 Ready map 中。

同样，Balance 也实现了 Service trait：

- `poll_ready`：只有有存在一个被选中的 Service 是ready的，那么就可以返回 ready，并记录该 Service 的 index
- `call`：直接调用上面的 index 对应的 Service 处理 request，这也就是为什么 Tower 建议在调用某个 Service 之前一定要调用 `poll_ready` 询问服务是否空闲。对应的 Service 在被调用之后会被插入到 Pending 队列中。

综上所述，Balance 模块提供了一种 Service 集托管服务，通过将 Service 集托管到 Balance 模块，由 Balance 决定 request 交给哪个 Service 处理。

### Buffer 中间件

Buffer 中间件希望提供一个类似于 mpsc 一样多生产者单消费者一样的缓存队列，可以允许多个用户同时像某个 Service 提交 request，更重要的是，Service 要能够将 request 的执行结果返回给用户。

Buffer 中间件的做法是将 Service 看作一个生产者，另外定义一个 Worker 作为消费者，Worker 负责接收 request 并处理。

```rust
struct Worker<T, Request>
where T: Service<Request> 
{
  current_message: Option<Message<Request, T::Future>>,
  rx: mpsc::Receiver<Message<Request, T::Future>>,
  service: T,
  finish: bool,
  failed: Option<ServiceError>,
  handle: Handle
}
```

Worker 维护了一个 mpsc channel 的接收端rx，而每个 Buffer Service 维护了一个 mpsc channel 的发送端tx，且 Buffer 实现了 Clone trait，当 Buffer 被 clone 时，对应的 tx 也被clone。

由于用户的 request 是由 Buffer 转交给 Worker 的，因此 request 的处理结果无法直接从 Buffer 获取。这里就体现了 Service trait 的灵活性，由于 Service 的call函数返回的是一个 Future，因此可以自定义一个 ResponseFuture，然后在 Worker 要处理的 Message 中包含一个 channel 的发送端，在call函数返回的 Future 中包含该 channel 的接收端，就可以使得 Worker 和用户之间可以直接通信。这个设计应该说是非常巧妙的。

```rust
impl<Req, Rsp, F, E> Service<Req> for Buffer<Req, F>
where
	F: Future<Output = Result<Rsp, E>> + Send + 'static,
	E: Into<Box<dyn std::error::Error + Send + Sync>>,
	Req: Send + 'static
{
  type Response = Rsp;
  type Error = Box<dyn std::error::Error + Send + Sync>;
  type Future = ResponseFuture<F>;
  
  fn call(&mut self, request: Rsp) -> Self::Future {
    let span = tracing::Span::current();//这个不用管
    let (tx, rx) = oneshot::channel();//构建一次性管道用于传输返回结果。
    match self.tx.send_item(Message {request, span, tx}) {
      Ok(_) => ResponseFuture::new(rx),
      Err(_) => {}
    }
  }
}
```

### Discover 中间件

在前面的 Balance 中间件中提到了 Service 集的概念，有集合，就意味着有集合内元素的变动。各个中间件对于 Service 集合的实现可能并不相同，但是都对外提供了统一的增删接口，这个接口就是 Discover trait。

Discover 为了方便对 Service 集进行管理，要求用户对每个 Service 定义一个唯一的标识符并且实现了 Eq。

对 Service 集的修改主要就是增加和删除，用枚举 Change 表示：

```rust
enum Change<K, V> {
  Insert(K, V),
  Remove(K)
}
```

对于一个维护 Service 集的struct，其对 Service 集的修改选择交给用户，由用户提供一个实现 Discover trait 的 struct，而维护 Service 集的 struct 只需要调用 poll_discover 函数就可以获取外界对 Service 集的修改。

```rust
trait Discover: Sealed<Change<(), ()>> {
  type Key: Eq,
  type Service;
  type Error;
  fn poll_discover(
    self: Pin<&mut self>, 
    cx: &mut Context<'_>
  ) -> Poll<Option<Result<Change<Self::Key, Self::Service>, Self::Error>>>;
}
```

> Tips: 在Rust异步编程中，很多的poll及类似的函数的返回结果都是 Poll<Option<Result<V, E>>> 类型的。这种返回类型可以从结果上反映很多东西，通常用于需要被多次poll的函数。
>
> - Poll::Pending: 暂时没有value返回，和普通的poll函数类似
> - Poll::Ready(None): 当前Future结束，不会再yield任何值
> - Poll::Ready(Some(Ok(_))): 当前 Future yield 一个值，可能还需要被poll
> - Poll::Ready(Some(Err(_))): 当前 Future 产生错误，需要进行处理
>
> 这一套规则在很多 Rust 异步编程代码中都有体现，可以看作 Rust 异步编程中的潜规则。

值得注意的是，这里的 Sealed 是一个空 trait，并且在crate之外无法访问，但是在 discover 模块中为所有实现了 TryStream 的类型实现了 Sealed

```rust
impl<K, S, E, D: ?Sized> Sealed<Change<(), ()>> for D
where
    D: TryStream<Ok = Change<K, S>, Error = E>,
    K: Eq,
{}
```

也就是说，要实现 Discover 首先要实现 TryStream，而在 discover 中也为所有实现了 TryStream 的类型自动实现了 Discover trait:

```rust
impl<K, S, E, D: ?Sized> Discover for D
where
    D: TryStream<Ok = Change<K, S>, Error = E>,
    K: Eq,
{
    type Key = K;
    type Service = S;
    type Error = E;

    fn poll_discover(
        self: Pin<&mut Self>,
        cx: &mut Context<'_>,
    ) -> Poll<Option<Result<D::Ok, D::Error>>> {
        TryStream::try_poll_next(self, cx)
    }
}
```

也就是将 Discover 抽象为流式操作，这样就可以用到很多现成的实现了 Stream 的工具来存储对于 Service 集的修改。

### Filter 中间件

Filter 顾名思义，对于 request 进行一次筛选，只有符合筛选条件的 request 才会提交给 Service 处理。

```rust
struct Filter<T, U> {
  inner: T,
  predicate: U
}
```

可以看出，Filter 的初始定义非常自由，Filter 对 predicate 并没有任何限制，但是 Filter 必须要根据 predicate 的返回结果分别处理，所以 Filter 和 predicate 总是相关的。

Filter 只对于当 predicate 实现了 Predicate trait 时实现了 Service trait。

```rust
trait Predicate<Req> {
  type Request;
  fn check(&mut self, request: Request) -> Result<Self::Request, Box<dyn std::error::Error + Send + Sync>>;
}
```

实现过程也很有意思，由于call函数要求返回一个 Future，因此当筛选不通过时，需要返回一个立刻返回 Ready(Err(\_)) 的 Future

```rust
impl<T, U, Request> Service<Request> for Filter<T, U>
where
    U: Predicate<Request>,
    T: Service<U::Request>,
    T::Error: Into<BoxError>,
{
    type Response = T::Response;
    type Error = BoxError;
    type Future = ResponseFuture<T::Response, T::Future>;//即future_util::future::Either;

    fn poll_ready(&mut self, cx: &mut Context<'_>) -> Poll<Result<(), Self::Error>> {
        self.inner.poll_ready(cx).map_err(Into::into)
    }

    fn call(&mut self, request: Request) -> Self::Future {
        ResponseFuture::new(match self.predicate.check(request) {
            Ok(request) => Either::Right(self.inner.call(request).err_into()),
            Err(e) => Either::Left(futures_util::future::ready(Err(e))),
        })
    }
}
```

#### async predicate

上面讲的predicate函数并不是异步的，这只适用于一些快速筛选的 Filter，如果 predicate 过程也需要等待IO等适合做成异步的场景，那么应该将 predicate 过程也做成异步形式。因此 Filter 模块还存在一个适用于异步场景的 AsyncFilter。

这就导致在一个 Service 同时存在两种 Future，用户也不知道两种 Future 的先后关系，因此需要将两种 Future 放到一个 AsyncResponseFuture，由 AsyncResponseFuture 协调两个 Future。

```rust
enum State<F, G> {
  Check {check: F},
  WaitResponse {response: G}
}
struct AsyncResponseFuture<P, S, Request>
where
	P: AsyncPredicate<Request>,
	S: Service<P::Request>
{
  state: State<P::Future, S::Future>,
  service: S
}
```

AsyncResponseFuture 的 poll 结果由当前 state 决定。

```rust
impl<P, S, Request> Future for AsyncResponseFuture<P, S, Request>
where
    P: AsyncPredicate<Request>,
    S: Service<P::Request>,
    S::Error: Into<crate::BoxError>,
{
    type Output = Result<S::Response, crate::BoxError>;

    fn poll(self: Pin<&mut Self>, cx: &mut Context<'_>) -> Poll<Self::Output> {
        let mut this = self.project();

        loop {
            match this.state.as_mut().project() {
                StateProj::Check { mut check } => {
                    let request = ready!(check.as_mut().poll(cx))?;
                    let response = this.service.call(request);
                    this.state.set(State::WaitResponse { response });
                }
                StateProj::WaitResponse { response } => {
                    return response.poll(cx).map_err(Into::into);
                }
            }
        }
    }
}
```

### Limit 中间件

服务器的处理能力是有限的，如果短时间内到达的 request 过多，可能会导致系统宕机。Limit 中间件用于对 request 进行限制，主要分为两种方式：

- concurrency: 限制并发处理的 request 数量
- rate：限制 request 处理的速率

concurrency 很好实现，只需要在 Service 维护一个信号量 semaphore，每要处理一个 request 就获取一个信号量，使得并发处理的数量不会超过信号量的值。

rate 可以表示为每一段时间允许的 request 数量：

```rust
struct Rate {
  num: u64,
  per: Duration
}
```

借助 tokio::time::sleep_util future，限制 now 到 now+per 这段时间内的 request 处理数量。

```rust
impl<S, Request> Service<Request> for RateLimit<S>
where
	S: Service<Request>
{
  type Response = S::Response;
  type Error = S::Error;
  type Future = S::Future;
 	fn call(&mut self, request: Request) -> Self::Future {
    match self.state {
      State::Ready{mut until, mut rem} => {
        let now = Instant::now();
        if now >= until {
          until = now + self.rate.per();
          rem = self.rate.num();
        }
        
        if rem > 1 {
        	rem -= 1;
          self.state = State::Ready{until, rem};
        } else {
          self.sleep.as_mut().reset(until);
          self.state = State::Limited;
        }
        
        self.inner.call(request);
      }
      State::Limited => panic!("service not ready")
    }
  }
}
```

### Load 中间件

Load 是用于定量化表示一个 Service 的负载的中间件。调用 Balance layer 的 Service 集就要求 Service 必须实现 Load trait。

```rust
trait Load {
  type Metric: PartialOrd,
  fn load(&self) -> Self::Metric;
}
```

Load 提供下列三个计算 Service 负载的模块：

- Constant：将 Service 的 Load 指标设为常数；

- PendingRequests: 根据 Service 的 Pending request 的数量作为 Service 的负载指标；

- PeakEwma: 峰值移动指数平均算法，将 request 的 rtt 时间作为 Service 的负载指标，rtt 即 request 从被接收到返回 response 中间经历的时间。

  同时 Load 维护一个平均 rtt 时间，如果最新 request 的 rtt 大于平均 rtt，则取最新 rtt 作为平均 rtt（这就是峰值移动指数平均法的意思）；如果 rtt 小于平均rtt，则根据最新 rtt 和移动指数平均算法计算平均rtt。

 第二、第三个模块显然需要追踪每个 request 的运行情况，为了解决这个问题，两个模块在实现 Service trait 的 call 函数时会返回一个 TrackCompletionFuture

```rust
struct TrackCompletionFuture<F, C, H> {
  #[pin]
  future: F,
  handle: Option<H>,
  completion: C
}
```

其中，handle 为通知 Service request 已经完成的柄，TrackCompletionFuture 只需要负责在 request 执行完成之后 drop handle，由具体的模块去实现 handle 被 drop 时需要实现的动作。

比如 PeakEwma 模块的 handle 需要追踪从接收 request 到执行完成的时间：

```rust
struct Handle {
  sent_at: Instant,
  decay_ns: f64,
  rtt_estimate: Arc<Mutex<RttEstimate>>
}
impl Drop for Handle {
  fn drop(&mut self) {
    let recv_at = Instant::now();
    if let Ok(mut rtt) = self.rtt_estimate.lock() {
      rtt.update(self.sent_at, recv_at, self.decay_ns);//涉及到PeakEwma算法的实现。
    }
  }
}
```

至于 PendingRequests 就更简单了，其 handle 直接就是一个 Arc\<()\> 类型的 wrap，直接调用 Arc 类型的 strong_count 函数就知道当前 Pending 的 request 数量。

### LoadShed 中间件

LoadShed 类似于 Rust 中的一些 try_xxx 函数，其 poll_ready 函数返回 `Poll<Result<(), E>>` 类型，当 poll_ready 被调用时，总是返回 Ready，但是根据里层的类型判断里层 Service 是否真的 Ready，这个中间件适用于一些特殊的场景。

如果在 Service not ready 的情况下调用call函数，则会返回 overloaded 错误。

### Make 中间件

Make 中间件是一种产生 Service 的 Service，适用于一些需要产生新的 Service 来进行处理的场景。Tower 给出的例子是 TCP listener，当收到一个新的 TCP 连接时，listener 需要创建一个新的 Service 来处理 TCP stream。

```rust
trait MakeService<Target, Request>: Sealed<(Target, Request)> {
  type Response;
  type Error;
  type Service: Service<Reuquest, Response = Self::Response, Error = Self::Error>;
  type MakeError;
  type Future: Future<Output = Result<Self::Service, Self::MakeError>>;
  
  fn poll_ready(&mut self, cx: &mut Context<'_>) -> Poll<Result<(), Self::MakeError>>;
  fn make_service(&mut self, target: Target) -> Self::Future;
}
```

MakeService 已经为所有 Response type 为 Service 类型的 Service 自动实现。

```rust
impl<M, S, Target, Request> MakeService<Target, Request> for M
where
    M: Service<Target, Response = S>,
    S: Service<Request>,
{
    type Response = S::Response;
    type Error = S::Error;
    type Service = S;
    type MakeError = M::Error;
    type Future = M::Future;

    fn poll_ready(&mut self, cx: &mut Context<'_>) -> Poll<Result<(), Self::MakeError>> {
        Service::poll_ready(self, cx)
    }
    fn make_service(&mut self, target: Target) -> Self::Future {
        Service::call(self, target)
    }
}
```

#### service_fn 组件

Tower 提供了一个可以快速将一个签名为

```rust
async fn(req: Request) -> Result<Response, Box<dyn std::error::Error + Send + Sync>>;
```

的异步函数包装为一个 Service 的函数 service_fn，其就是一个 Make Service。这种包装很简单，因为每个异步函数在调用时编译器会自动生成一个 Future。

```rust
struct ServiceFn<T> {
  f: T
}
impl<T, F, Request, R, E> Service<Request> for ServiceFn<T>
where
    T: FnMut(Request) -> F,
    F: Future<Output = Result<R, E>>,
{
    type Response = R;
    type Error = E;
    type Future = F;

    fn poll_ready(&mut self, _: &mut Context<'_>) -> Poll<Result<(), E>> {
        Ok(()).into()
    }
    fn call(&mut self, req: Request) -> Self::Future {
        (self.f)(req)
    }
}
```

### Reconnect 中间件

Reconnect 是一个可以在发生错误时自动重连的中间件，一个 Reconnect Service 有三种状态：

- Idle: 暂时没有任何服务连接，当在这个状态 poll_ready 时，需要根据内部的一个 MakeService 中间件创建一个 Service Future 并跳到 Connecting(MakeService::Future) 状态
- Connecting: 通过前一步的 Service Future 进行 poll，如果返回 Ready 则跳到 Connected(Service) 状态，如果有错误则跳到 Idle 状态
- Connected: 调用内层 Service 的 poll_ready，如果返回错误，则需要重新创建连接，跳到 Idle 状态

在 poll_ready 函数中，遇到 Poll::Ready(Ok(\_)) 或 Poll::Pending 则直接返回，如果遇到 Poll::Ready(Err(\_)) 则不断循环，直到 Service 正常，因此为 Reconnect。从这一点来看，poll_ready 其实永远不会返回 Poll::Ready(Err(\_))，但是为了后续的扩展性，在函数签名上还是有。

Reconnect 如果在非 Connected 状态下调用 call 函数则会 panic。

### Retry 中间件

Retry 中间件试图将多次里层 Service 的 poll 表现为一次，最简单的场景，对于一个比较繁忙的 Service，单次 poll 可能会返回 Error，于是我可能希望将 Service Future 的一次 poll 表现为里层 Service 每隔一段时间进行一次 poll 进行多次，直到成功返回 Ready 或达到次数限制。Retry 中间件就适用于这些场景。

显然上面只是一种最简单的场景，Tower 为了给予用户最大的 Retry 定制化空间，只需要用户决定是否继续 retry 的类型实现 Policy trait

```rust
trait Policy<Req, Res, E>: Sized {
  type Future: Future<Output = Self>;
  fn retry(&self, req: &Req, result: Result<&Res, &E>) -> Option<Self::Future>;
  fn clone_request(&self, req: &Req) -> Option<Req>;
}
```

其中 retry 函数用于决定是否应该继续 retry，如果返回 None 则停止，否则返回 Some(Future)。Future 可以在被 poll 时每次生成一个新的实现了 Policy 的 Retry Service，这意味着每次 retry 之后都可以产生新的 Service，而不是只能一直使用同一种 Policy，进一步增大了自由度。

最后再看 Tower 给的 Retry Service 对于 call 函数的 ResponseFuture 的实现。ResponseFuture 包含三种状态：

- Called(service_future): 可以poll一次里层 Service，如果是 Pending 则直接返回 Pending。否则调用 retry 函数生成一个新的 Retry Service Future，跳到 Checking(retry_future) 状态
- Checking(retry_future): 等待 retry_future 生成新的 Retry Service 的中间态，如果生成 Retry Service 则跳到 Retrying 状态
- Retrying: 等待里层 Service poll_ready 的中间态，如果里层 Service 已经 Ready，则调用里层 Service 的call函数生成 service_future 并跳到 Called(service_future) 状态

### SpawnReady 中间件

SpawnReady 在官方文档上的介绍是 "Drive a service to readiness on a background task"。如果我们需要尽快察觉到某个 Service 已经 ready，那我们可能会经常去 poll_ready 一下，而 SpawnReady 就是将这件事包装为一个 Service，并且在内部包装一个 task 用于检查内层 Service 是否 ready。假设 executor 里面只有两个 task，那么一个是真正在做事的 task，另一个则是检查前一个 task 是否 ready 的 task。

```rust
impl<S, Req> Service<Req> for SpawnReady<S>
where
    Req: 'static,
    S: Service<Req> + Send + 'static,
    S::Error: Into<BoxError>,
{
    type Response = S::Response;
    type Error = BoxError;
    type Future = ResponseFuture<S::Future, S::Error>;

    fn poll_ready(&mut self, cx: &mut Context<'_>) -> Poll<Result<(), BoxError>> {
        loop {
            self.inner = match self.inner {
                Inner::Service(ref mut svc) => {
                    if let Poll::Ready(r) = svc.as_mut().expect("illegal state").poll_ready(cx) {
                        return Poll::Ready(r.map_err(Into::into));
                    }
                    let svc = svc.take().expect("illegal state");
                    let rx =   tokio::spawn(svc.ready_oneshot().map_err(Into::into).in_current_span());
                    Inner::Future(rx)
                }
                Inner::Future(ref mut fut) => {
                    let svc = ready!(Pin::new(fut).poll(cx))??;
                    Inner::Service(Some(svc))
                }
            }
        }
    }
}
```

通过 ready_oneshot 函数将 Service 包装为一个 ReadyOneshot task，然后通过 tokio::spawn 传入 executor

### Steer 中间件

Steer 中间件用于管理 Service 数组，根据自定义的规则将 request 导向特定的 Service。

```rust
trait Picker<S, Req> {
  fn pick(&mut self, r: &Req, services: &[S]) -> usize;
}
```

由于 Steer 内部维护多个 Service，所以只有多个 Service 同时 ready， Steer 才会返回 Ready。

```rust
struct Steer<S, F, Req> {
  router: F,
  services: Vec<S>,
  not_ready: VecDeque<usize>,
  _phantom: PhantomData<Req>
}
impl<S, Req, F> Service<Req> for Steer<S, F, Req>
where
    S: Service<Req>,
    F: Picker<S, Req>,
{
    type Response = S::Response;
    type Error = S::Error;
    type Future = S::Future;

    fn poll_ready(&mut self, cx: &mut Context<'_>) -> Poll<Result<(), Self::Error>> {
        loop {
            // must wait for *all* services to be ready.
            // this will cause head-of-line blocking unless the underlying services are always ready.
            if self.not_ready.is_empty() {
                return Poll::Ready(Ok(()));
            } else {
                if self.services[self.not_ready[0]]
                    .poll_ready(cx)?
                    .is_pending()
                {
                    return Poll::Pending;
                }

                self.not_ready.pop_front();
            }
        }
    }

    fn call(&mut self, req: Req) -> Self::Future {
        assert!(
            self.not_ready.is_empty(),
            "Steer must wait for all services to be ready. Did you forget to call poll_ready()?"
        );

        let idx = self.router.pick(&req, &self.services[..]);
        let cl = &mut self.services[idx];
        self.not_ready.push_back(idx);
        cl.call(req)
    }
}
```

这样的处理实际会拖累整体的效率，如果某个 request 所需要的 Service 实际是 ready 的，但是可能为了等待其他的 Service 而延缓调用。但是为了兼容 Tower 的核心 API 不得不这么处理，毕竟 poll_ready 会与 request 相关的 Service 只有这一个。

### 结论

Tower 将网络编程中常见的行为抽象为统一的 Service，对外的接口非常统一，并且可以相互叠加，而且是异步式，是一个扩展性非常强大的框架，值得学习一下。