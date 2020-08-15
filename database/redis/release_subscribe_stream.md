---
author: lunar
date: Mon 10 Aug 2020 11:37:07 AM CST
---

### 发布订阅系统

发布订阅系统是web系统比较常用的一个功能，redis虽然可以使用list列表结构结合`lpush`和`rpop`来实现消息队列的功能。

为此，redis有一个单独的模块`PubSub`来实现消息多播。

#### PubSub简介

PubSub引入了频道(Channel)的概念来消除`publisher`和`consumer`之间的点对点的强关联。当`publisher`往`channel`中发布消息时，关注了`channel`的`consumer`就能同时收到消息。

为了方便地让`consumer`同时收到多个消息，redis方便地提供了**模式订阅**的功能，可以一次性关注多个相同模式的频道。如果`publisher`新增了相同模式的频道，`consumer`也可以立刻收到消息。

#### 快速体验

PubSub的使用很简单，常用命令就下面几条：
```
# 订阅频道：
SUBSCRIBE channel [channel ....]   # 订阅给定的一个或多个频道的信息
PSUBSCRIBE pattern [pattern ....]  # 订阅一个或多个符合给定模式的频道
# 发布频道：
PUBLISH channel message  # 将消息发送到指定的频道
# 退订频道：
UNSUBSCRIBE [channel [channel ....]]   # 退订指定的频道
PUNSUBSCRIBE [pattern [pattern ....]]  #退订所有给定模式的频道
```

#### 实现原理

**订阅频道原理**

每个redis服务器进程维护着一个标识服务器状态的`redis.h/redisServer`结构体，其中就保存着订阅的频道以及订阅模式的信息：
```c
struct redisServer {
    //...
    dict* pubsub_channels;
    list* pubsub_patterns;
    //...
};
```

当客户端订阅某个频道之后，redis就往`pubsub_channels`字典中添加一条新的数据，实际上这个字典维护的是一个链表。

![](https://camo.githubusercontent.com/ad0f6c4e94fd35075c4fe41d9e537859fe15bb4d/68747470733a2f2f75706c6f61642d696d616765732e6a69616e7368752e696f2f75706c6f61645f696d616765732f373839363839302d323138666331356637633336386565652e706e673f696d6167654d6f6772322f6175746f2d6f7269656e742f7374726970253743696d61676556696577322f322f772f31323430)

**订阅模式原理**

前面讲到，订阅模式维护的是一个`list`，对于`list`的每个元素，都是一个`redis.h/pubsubPattern`结构体：

```c
typedef struct pubsubPattern {
    redisClient* client;
    robj* pattern;
} pubsubPattern;
```

![](https://camo.githubusercontent.com/30c4b7d3fb30be685db4e33e96c2d18e1d328b9f/68747470733a2f2f75706c6f61642d696d616765732e6a69616e7368752e696f2f75706c6f61645f696d616765732f373839363839302d656462663131393935353930646535302e706e673f696d6167654d6f6772322f6175746f2d6f7269656e742f7374726970253743696d61676556696577322f322f772f31323430)

每当调用`psubscribe`命令订阅一个模式时，程序就创建一个包含客户端信息和被订阅模式的`pubsubPattern`结构体，并将该结构体添加到`redisServer.pubsub_patterns`链表中。

#### PubSub的缺点

尽管 Redis 实现了 PubSub 模式来达到了 多播消息队列 的目的，但在实际的消息队列的领域，几乎 找不到特别合适的场景，因为它的缺点十分明显：

- 没有 Ack 机制，也不保证数据的连续： PubSub 的生产者传递过来一个消息，Redis 会直接找到相应的消费者传递过去。如果没有一个消费者，那么消息会被直接丢弃。如果开始有三个消费者，其中一个突然挂掉了，过了一会儿等它再重连时，那么重连期间的消息对于这个消费者来说就彻底丢失了。

- 不持久化消息： 如果 Redis 停机重启，PubSub 的消息是不会持久化的，毕竟 Redis 宕机就相当于一个消费者都没有，所有的消息都会被直接丢弃。

基于上述缺点，Redis 的作者甚至单独开启了一个 Disque 的项目来专门用来做多播消息队列，不过该项目目前好像都没有成熟。不过后来在 2018 年 6 月，Redis 5.0 新增了 Stream 数据结构，这个功能给 Redis 带来了 持久化消息队列，从此 PubSub 作为消息队列的功能可以说是就消失了..

### 更为强大的Stream持久化的发布/订阅系统

Redis Stream从概念上来说，就像是一个仅追加内容的消息链表，把所有加入的消息都一个一个串起来，每个消息都有一个唯一的ID和内容。

![](https://camo.githubusercontent.com/6f3715dbb159808ad824726583c193daf96e9c25/68747470733a2f2f75706c6f61642d696d616765732e6a69616e7368752e696f2f75706c6f61645f696d616765732f373839363839302d623964386166646530363861313635662e706e673f696d6167654d6f6772322f6175746f2d6f7269656e742f7374726970253743696d61676556696577322f322f772f31323430)

上图是一个Stream结构。每个Stream都有唯一的名称，它就是redis的`key`，在我们首次使用`xadd`指令追加消息时自动创建。

- Consumer Group: 消费者组。同一个消费者组内的消费者共享所有的Stream信息，同一条消息只会有一个消费者消费到。

- last_deliverd_id: 用来表示消费者组消费在Stream上消费位置的游标信息。

- pending-ids: 每个消费者内部都有的一个状态变量，用来表示已经被客户端获取，但是还没有`ack`的消息。记录的目的是为了保证客户端至少消费了消息一次，而不会在网络传输的中途丢失而没有消费到。

#### 增删改查示例

1. `xadd`: 追加消息
2. `xdel`: 删除消息，这里的删除仅仅是设置了标志位，不影响消息总长度。
3. `xrange`: 获取消息列表，会自动过滤已经删除的消息
4. `xlen`: 消息长度
5. `del`: 删除Stream

```redis
# *号表示服务器自动生成ID，后面顺序跟着一堆key/value
127.0.0.1:6379> xadd codehole * name laoqian age 30  #  名字叫laoqian，年龄30岁
1527849609889-0  # 生成的消息ID
127.0.0.1:6379> xadd codehole * name xiaoyu age 29
1527849629172-0
127.0.0.1:6379> xadd codehole * name xiaoqian age 1
1527849637634-0
127.0.0.1:6379> xlen codehole
(integer) 3
127.0.0.1:6379> xrange codehole - +  # -表示最小值, +表示最大值
1) 1) 1527849609889-0
   2) 1) "name"
      2) "laoqian"
      3) "age"
      4) "30"
2) 1) 1527849629172-0
   2) 1) "name"
      2) "xiaoyu"
      3) "age"
      4) "29"
3) 1) 1527849637634-0
   2) 1) "name"
      2) "xiaoqian"
      3) "age"
      4) "1"
127.0.0.1:6379> xrange codehole 1527849629172-0 +  # 指定最小消息ID的列表
1) 1) 1527849629172-0
   2) 1) "name"
      2) "xiaoyu"
      3) "age"
      4) "29"
2) 1) 1527849637634-0
   2) 1) "name"
      2) "xiaoqian"
      3) "age"
      4) "1"
127.0.0.1:6379> xrange codehole - 1527849629172-0  # 指定最大消息ID的列表
1) 1) 1527849609889-0
   2) 1) "name"
      2) "laoqian"
      3) "age"
      4) "30"
2) 1) 1527849629172-0
   2) 1) "name"
      2) "xiaoyu"
      3) "age"
      4) "29"
127.0.0.1:6379> xdel codehole 1527849609889-0
(integer) 1
127.0.0.1:6379> xlen codehole  # 长度不受影响
(integer) 3
127.0.0.1:6379> xrange codehole - +  # 被删除的消息没了
1) 1) 1527849629172-0
   2) 1) "name"
      2) "xiaoyu"
      3) "age"
      4) "29"
2) 1) 1527849637634-0
   2) 1) "name"
      2) "xiaoqian"
      3) "age"
      4) "1"
127.0.0.1:6379> del codehole  # 删除整个Stream
(integer) 1
```


