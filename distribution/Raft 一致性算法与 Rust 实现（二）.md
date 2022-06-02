## Raft 一致性算法与 Rust 实现（二）

### 数据结构

首先实现各种数据结构，

#### 日志

日志项：

```rust
/// A replicated log entry
#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
pub struct Entry {
    /// The term in which the entry was added
    pub term: u64,
    /// The state machine command. None is used to commit noops during leader election.
    pub command: Option<Vec<u8>>,
}
```

日志项的index作为存储的key进行管理，所以在日志项内不保存index

日志：

```rust
/// The replicated Raft log
#[derive(Debug)]
pub struct Log {
    /// The underlying key-value store
    kv: Box<kv::Store>,
    /// The index of the last stored entry.
    last_index: u64,
    /// The term of the last stored entry.
    last_term: u64,
    /// The last entry known to be committed. Not persisted,
    /// since leaders will determine this when they're elected.
    commit_index: u64,
    /// The term of the last committed entry.
    commit_term: u64,
    /// The last entry applied to the state machine. This is
    /// persisted, since the state machine is also persisted.
    apply_index: u64,
    /// The term of the last applied entry.
    apply_term: u64,
}
```

其中 `Store` 是一个trait，用于描述一种map型的行为，只是必须以&str类型作为key进行存取，而value则是一个字节buffer。

```rust
/// A key-value store
pub trait Store: 'static + Sync + Send + std::fmt::Debug {
    /// Deletes a value in the store, regardless of whether it existed before.
    fn delete(&mut self, key: &str) -> Result<(), Error>;

    /// Gets a value from the store
    fn get(&self, key: &str) -> Result<Option<Vec<u8>>, Error>;

    /// Sets a value in the store
    fn set(&mut self, key: &str, value: Vec<u8>) -> Result<(), Error>;
}
```

这样做的目的是降低日志项的存储和操作的耦合性，只需要实现相应的函数，日志项的存储可以灵活设计。

#### 抽象状态机：

```rust
/// A Raft-managed state machine.
pub trait State: 'static + Sync + Send + std::fmt::Debug {
    /// Reads from the state machine.
    fn read(&self, command: Vec<u8>) -> Result<Vec<u8>, Error>;

    /// Mutates the state machine.
    fn mutate(&mut self, command: Vec<u8>) -> Result<Vec<u8>, Error>;
}
```

状态机可以抽象为两个函数，一个只读状态机，另一个要对状态机进行修改。

#### 通信

通信模块用于在 Raft 节点之间传输信息，首先抽象出通信方式：

```rust
/// A transport for communication between a Raft node and its peers.
pub trait Transport: 'static + Sync + Send {
    /// Returns a channel for receiving inbound messages.
    fn receiver(&self) -> Receiver<Message>;

    /// Sends a message to a peer.
    fn send(&self, msg: Message) -> Result<(), Error>;
}
```

然后创建一个 Message 结构体用于表示一段消息。消息首先要包括发送者和接收者的id, 然后还要包括发送者的任期号term, 还有一个事件类型表示 Message 的类型。

```rust
/// A message passed between Raft nodes.
#[derive(Debug, PartialEq)]
pub struct Message {
    /// The current term of the sender.
    pub term: u64,
    /// The ID of the sending node, or None if local sender.
    pub from: Option<String>,
    /// The ID of the receiving node, or None if local receiver.
    pub to: Option<String>,
    /// The message event.
    pub event: Event,
}
```

由于一个节点可能自己给自己发送消息（比如给自己投票），因此发送者和接收者可以为None。

显然，按照 Rust 的传统，Event 势必是enum类型：

```rust
/// An event contained within messages.
#[derive(Clone, Debug, PartialEq)]
pub enum Event {
    /// Leaders send periodic heartbeats to its followers.
    Heartbeat {
        /// The index of the leader's last committed log entry.
        commit_index: u64,
        /// The term of the leader's last committed log entry.
        commit_term: u64,
    },
    /// Followers confirm loyalty to leader after heartbeats.
    ConfirmLeader {
        /// The commit_index of the original leader heartbeat, to confirm
        /// read requests.
        commit_index: u64,
        /// If false, the follower does not have the entry at commit_index
        /// and would like the leader to replicate it.
        has_committed: bool,
    },
    /// Candidates solicit votes from all peers.
    SolicitVote {
        // The index of the candidate's last stored log entry
        last_index: u64,
        // The term of the candidate's last stored log entry
        last_term: u64,
    },
    /// Followers may grant votes to candidates.
    GrantVote,
    /// Leaders replicate a set of log entries to followers.
    ReplicateEntries {
        /// The index of the log entry immediately preceding the submitted commands.
        base_index: u64,
        /// The term of the log entry immediately preceding the submitted commands.
        base_term: u64,
        /// Commands to replicate.
        entries: Vec<Entry>,
    },
    /// Followers may accept a set of log entries from a leader.
    AcceptEntries {
        /// The index of the last log entry.
        last_index: u64,
    },
    /// Followers may also reject a set of log entries from a leader.
    RejectEntries,
    /// Reads from the state machine.
    ReadState {
        /// The call ID.
        call_id: Vec<u8>,
        /// The state machine command.
        command: Vec<u8>,
    },
    /// Mutates the state machine.
    MutateState {
        /// The call ID.
        call_id: Vec<u8>,
        /// The state machine command.
        command: Vec<u8>,
    },
    /// The response of a state machine command.
    RespondState {
        /// The call ID.
        call_id: Vec<u8>,
        /// The command output.
        response: Vec<u8>,
    },
    /// An error response
    RespondError {
        /// The call ID.
        call_id: Vec<u8>,
        /// The error.
        error: String,
    },
}
```

Event 既包括 Raft 协议中的两种 RPC：ReplicateEntries、SolicitVote，此外还包括了其他类型的事件比如心跳信息、follower 对于 leader 的回复等。

#### 节点

节点的实现需要通过区分不同角色：Leader, Candidate, Follower, 但是这三种角色也有相同点，所以可以创建一个共同结构体来描述共同点，并用泛型来保存角色特定的内容。

```rust
// A Raft node with role R
#[derive(Debug)]
pub struct RoleNode<R> {
    id: String,
    peers: Vec<String>,
    term: u64,
    log: Log,
    state: Box<State>,
    sender: Sender<Message>,
    role: R,
}
```

##### Leader

```rust
// A leader serves requests and replicates the log to followers.
#[derive(Debug)]
pub struct Leader {
    /// Number of ticks since last heartbeat.
    heartbeat_ticks: u64,
    /// The next index to replicate to a peer.
    peer_next_index: HashMap<String, u64>,
    /// The last index known to be replicated on a peer.
    peer_last_index: HashMap<String, u64>,
    /// Any client calls being processed.
    calls: Calls,
}
```

Leader 主要完成的工作包括下列函数：

- append： 添加一个日志项到自己的日志中并分发给自己的追随者
- apply: 通过一个循环将日志中的日志项应用到状态机
- commit：提交一个日志项需要确保大多数成员的最新提交的日志项的索引都不小于领袖的最新提交的日志项的索引，否则直接返回当前提交的日志项的最大索引；即便上一个条件满足，领袖也只能安全提交来自自己的任期内的日志项，在 Raft 论文的图8有详细说明。
- replicate: 复制一段日志项给追随者，包括该追随者应该接收的下一个日志项的索引到领袖的最后一个日志项索引
- step：处理其它节点（可能是自己）发送的消息，如果发现消息的任期比自己的任期大，则需退回到追随者状态。
  - ConfimLeader：记录发送者并增加自己的票数
  - AcceptEntries: 说明追随者接受了自己的日志项，则更新该追随者已经复制的日志项的索引并尝试提交自己的日志项和应用到状态机；
  - RejectEntries: 说明追随者拒绝了自己的日志项，因为其索引太大，则应该将该追随者的nextIndex减一并重新复制日志项；
  - ReadState: 
  - MutateState: 



