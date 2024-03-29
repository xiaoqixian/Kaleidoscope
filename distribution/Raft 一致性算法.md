## Raft 一致性算法与 Rust 实现（一）

所謂一致性算法，是指能夠允許一組機器可以協同工作並能容忍部分成員的宕機。在 Raft 算法出現之前，已經有 Paxos 算法朱玉在前，但是由於 Paxos 非常難以理解，因此斯坦福的兩位教授提出了 Raft 算法，Raft 算法被提出的首要目標是易理解性，正如其所言:

> It was important not just for the algorithm to work, but for it to be obvious why it works.

Raft 算法特點：

- 中央集权制：Raft 具有一個強有力的領袖节点
- 民主選举：使用隨機時間來選举領袖
- 成員变动：当需要变动集群中的服务器时，Raft 使用 *联合一致性* 算法来保证系统正常工作，从而是的系统在不宕机的前提下进行成员的更替。

### 复制状态机问题

分布式集群出现的前提是单个服务器的容错率已经不足以满足需求，因此需要部署服务器集群来提高容错率。将每个服务器看作一个状态机，一组状态机在初始状态相同，输入相同，转换函数和输出函数相同的前提下，输出必然是相同的。因此通过对比集群成员的输出，可以轻易地知道出错的服务器。

复制状态机由 *复制日志* 进行实现，每个日志项包含一系列有序的命令，每个状态机有序执行这些命令，在不出错误的情况下总能得到相同的结果。通常这些日志项由领袖服务器进行接收，并由其分发给其它的服务器。分发必须确保所有命令的数量和顺序完整性。分发完成后，由每个服务器执行并将结果返回给客户端。

### Raft 一致性算法

Raft 实现一致性首先通过选举出一个领袖节点，领袖节点负责从客户端接收命令并分发给其它所有服务器，并告知服务器可以安全执行这些命令的时间节点。

Raft 将一致性问题分为以下三个问题：

- 选举领袖：当现领袖节点无法响应时，必须选举新的领袖节点
- 复制日志：领袖节点必须接收客户端的日志项，并将其分发给所有集群里的所有成员
- 安全性：任何一个状态机执行了某一个日志项，则对于同一个日志索引，其它服务器不应该执行到任何不同的命令。即保证同一个日志索引对于任何服务器而言都是对应的同一个命令。

#### Raft 基础

通常对于一个具有 $2n+1$ 个服务器的 Raft 集群来说，其可允许的错误服务器数量为 $n$。

任意时刻单个服务器状态只可能处于 *领袖*、*追随者*、*候选领袖* 中的一种。在正常工作的情况下，则只有一个领袖节点和其它的追随者节点。

Raft 将系统时间划分为不同的 *任期*， 每个任期的长度不一且总以选举开始，如果任期内选举出领袖，则正常工作直至任期结束；如果任期内没有选举出领袖，则在新任期开始时重新选举。没有选举出领袖通常是指有多个候选领袖的票数相同。

不同服务器的任期变化并不是同时发生的，每个服务器携带有一个当前的任期号（线性增加），但是这个任期号可能并不是全局的当前任期号，所以当服务器与其他服务器通信时，如果发现对方的任期号大于己方，则修改任期号为对方任期号。如果有领袖节点或候选领袖节点发现自己的任期号小于其他服务器的任期号，则立刻转换为追随者状态。而其它服务器接收到小于自己任期号的服务器的请求时，则会直接拒绝。即领袖服务器的任期号必须大于等于其追随者的任期号才合法。

Raft 通过 RPC (Remote Procedure Call) 与其他服务器进行通信，Raft 只包含两种类型 RPC：

- RequestVote RPC: 请求选票
- AppendEntries RPC：添加日志项，领袖节点发送心跳信息也是这类RPC, 但是不携带日志项（用于向其他服务器表明领袖节点没有失联）

#### 选举领袖

正常情况下，领袖节点定期向其追随者发送心跳信息，如果存在追随者在一定时间内没有接收到心跳信息，则其认为领袖已经失联，随即发起一轮新的选举。

当该追随者发起一轮新的选举时，其将自己的任期号加一，用于表示进入新的任期，自身状态进入候选领袖状态。随后向集群的所有服务器平行发送 RequestVote RPC，该候选者将持续该状态直到下列情况中的一种发生：

1. 赢下选举：条件是赢下大多数服务器的选票，而追随者投票的规则是只会投给不小于自己的任期号的候选者，且根据先到先得的规则只能投一票；当某个服务器赢得选举之后，其会给其它所有服务器发送心跳消息来建立自己的权威以及组织新的选举进行。
2. 已有另一个服务器赢下选举：在当前服务器等待选票的过程中，可能会接收到 AppendEntries RPC（来自于领袖节点），如果该RPC 的任期号至少大于等于当前服务器的任期号，则说明已有合法领袖，当前服务器退回追随者状态；如果任期号小于当前服务器，则说明是过时的领袖，则拒绝请求并保持候选状态。
3. 一段时间之后依旧没有胜者：当多个候选者同时竞选时，可能存在没有任何一个候选者获得大多数选票，则无法产生一个合法的领袖，需要进行新一轮的选举，在没有外界干预的情况下，可能一直无法产生领袖。

Raft 使用 *随机化选举时长* 来尽可能减少第三种情况的出现，随机时长通常出现在150-300ms 之间，因此更容易出现一个服务器可以先出现超时从而成为领袖节点（在多个候选节点的情况下）。

#### 复制日志

领袖节点负责从客户端接收命令并组成日志项并并行分发给其它服务器，如果其它节点由于运行速度、网络问题或者已经崩溃，领袖节点依旧会持续给这些服务器发送 AppendEntries RPC 直到所有节点都已经存储所有日志项。

每个日志项不仅所要执行的命令，同时携带其被组成时的领袖节点任期号以及一个索引号用于表征该日志项在所有日志中的位置。

当一个日志项已经被安全复制到大多数服务器上时，其可被认为是 *已提交 (committed)* 状态。同时也代表领袖节点之前的所有日志项也已经是已提交状态（包括之前的领袖节点所创建的日志项），即日志项的提交是有序的。

而领袖节点负责记录当前已被提交的日志项的最大索引，并将该索引携带于 AppendEntries RPC 中，对于追随者节点，小于等于该索引的日志项可安全按顺序执行。

Raft 维持以下属性来确保安全性：

- 如果两个位于不同服务器日志中的日志项具有相同的索引和任期号，则其必然包含相同的命令；
- 同上条件的两个日志项，则其两个日志在这两个日志项之前的所有日志项也必然相同。

在正常情况下，领袖节点可以与其追随者节点保持一致；但是当领袖节点突然宕机时，该领袖节点可能并没有将其日志安全复制到所有节点，因此可能导致新上任的领袖无法与其他节点保持一致，包括以下情况：

- 服务器缺失日志项，即没有完全复制所有日志项；
- 存在比当前领袖服务器的最大任期号更大的任期号的日志项，即当前领袖节点没有被前领袖完全复制日志项；
- 存在比当前领袖服务器的最大任期号更小但不存在于当前的领袖服务器的日志中的日志项。这种情况发生的原因是该服务器曾为领袖服务器，但是生成这些日志项后未来得及提交就已经宕机，导致这些日志项只存在于该服务器内。

![image-20220208000408138](https://gitee.com/xiaoqixian/picbed2/raw/master/2022/02/image-20220208000408138.png)

为了保持领袖节点与追随者节点的同步，领袖节点必须找到与追随者节点最近的前部分相同的节点，然后将追随者节点之后的所有日志项删除并复制领袖节点的之后的日志项。所有这些动作由追随者节点在对 AppendEntries RPC 的回复中完成。

领袖节点对每个追随者节点都要维护一个 *nextIndex* 值，用于表示领袖要发送给追随者的下一个日志项的索引。当一个领袖新上任时，其将所有的服务器的 nextIndex 值初始化为其自己的 nextIndex 值，这样在发送 AppendEntries RPC 时，如果该 nextIndex 值无法与追随者的 nextIndex 值对应，则追随者拒绝该 RPC, 而领袖节点在知道该 RPC 失败之后主动减小对于该追随者的 nextIndex 值，最终总能达到追随者和领袖的日志相匹配。

#### 安全性

##### 选举限制

Raft 要求所有参加选举的候选者都必须携带之前所有已经提交的日志项，从而无需从其他节点上将缺失的已提交的日志项转移到新领袖上。因此，**在 Raft 中，日志的复制永远只会单向流动（身份意义上的单向流动），即领袖节点从来不会覆写其已有的日志项。 **

Raft 通过 RequestVote RPC 来实现这个限制。由于成为领袖需要得到大多数成员的选票，而一个日志项被提交也要复制到大多数成员上。因此结合两点可以得出：如果候选者的日志至少与大多数成员中的一个的日志保持 “最新”，则说明该候选者保有所有已提交的日志项。

因此只需在 RequestVote RPC 中携带候选者的日志信息，如果票民发现其日志信息落后于自己，则拒绝为其投票，从而保证日志项不够的候选者不会当选。

Raft 对于日志信息的新旧比较方法为：首先比较两组日志的任期号，任期号更新的日志就是更新的一组日志；如果任期号相同，则比较日志长度，更长的日志是更新的一组日志。

##### 提交前任任期内组成的日志项

领袖服务器可以很容易地知道在当前任期下组成的日志项是否已经安全复制到大多数成员上，只需要比较已复制的成员数量与总成员数量即可。而新领袖上任时，其还需要负责将前任宕机前为复制完的日志项复制到未复制的成员上去，但是有一个问题是其无法立刻判断一个前任任期内组成的日志项是否已经复制到大多数成员上，因为无法知道前任已经复制给了多少成员。可能已经复制给了大多数成员，但是还未来得及提交就宕机了，导致已经复制的日志项被新领袖覆写。

<img src="https://gitee.com/xiaoqixian/picbed2/raw/master/2022/02/image-20220208171607509.png" alt="image-20220208171607509" style="zoom:70%;" />

如图，S1 在任期 2 成为领袖时，(b) 图为 S1 未来得及将index2 的日志项复制到大多数的成员之前就宕机了，导致 S5 在任期3成为领袖之后将index2 的日志项覆写掉；如果S1 及时提交index2 的日志项，S5 就会因为日志项缺少而无法当选。该图展现的问题即即使一个日志项已经被复制到了大多数成员上了，但是仍然可能被新领袖的日志项覆写掉。

为了解决上图中的问题，Raft 并不会通过回复计数的方式提交前任领袖遗留的未提交的日志项。当任领袖只会提交当任时组成的日志项，而根据 **Log Matching Property**，前任领袖的遗留日志项则间接被提交。

所谓 Log Matching Property:

> - 如果两个日志项具有相同的索引和任期号，则两个日志项存储的命令必然相同；
>
> - 如果两个处于不同日志中的日志项有相同的索引和任期号，则两组日志在到该日志项为止的所有日志项都必然相同，包括顺序。

##### 安全性证明

首先介绍 Raft 的 Leader Completeness Property: 

> 如果某个日志项在某个任期内被提交，则该日志项必然被包含在所有往后任期内的领袖节点的日志中。

通过反证法可以证明，某日志项在任期 T 内组成，任期 U 为 T 后一个任期，假设任期 U 领袖未携带该日志项，则有以下推导（下面用领袖 U 指代任期 U 内的领袖节点，领袖 T 指代任期 T 内的领袖节点）：

1. 由于领袖节点不会删除自己的日志项，则该日志项必然在选举之前就没有；
2. 由于该日志项已被提交，因此必然大多数服务器都携带该日志项，而领袖 U 在当选时必然也获得大多数成员的选票，两部分成员必然有重叠部分，则至少有一个服务器既给领袖 U 投了票也携带有该日志项，选择其中一名成员进行论证；
3. 既然该成员投票给了领袖U, 则领袖U的日志记录至少和该成员一样新，这将带来两个矛盾；
4. 首先，如果领袖U和该成员的最新日志项的任期号相同，则说明领袖U的日志项至少和该成员一样长，即领袖U至少包含该成员的所有日志项而与假设矛盾；
5. 如果两者的任期号不同，领袖U的最新日志项的任期号更大，而可以确定的是该成员的最后一项日志项的任期号至少为T, 因为其携带了由任期T提交的日志项，则创建领袖U的最新日志项的领袖也必然包含该日志项，因此根据 Log Matching Property, 领袖U也必然包含该日志项。

#### 追随者和候选人宕机

追随者和候选人宕机的处理容易多了，两种身份的处理方式也相同。如果追随者或候选人宕机，则所有发送给其的两种RPC都会响应失败，而 Raft 在没有收到成功回复之前，会一直发送两种RPC直到服务器重启并成功响应。

#### 时间与可用性的关系

Raft 并不是一个对时间敏感的系统，但是不同类型时间之间的数量级的差别和可用性的关联很大。比如服务器的崩溃间隔，如果服务器的崩溃间隔与领袖选举的时长是一个级别，则很可能领袖还没选出来或者刚选出来系统就宕机了，系统只能一直选举。比如网络传播延时与选举时长的关系，如果网络传播延时和选举时长差不多，可能部分候选者还没有得到消息就结束了。

一般来说：
$$
broadcastTime\ll eletionTimeout\ll MTBF
$$
MTBF即服务器的平均崩溃时间间隔。

### 集群成员变动

为了保证安全，集群成员的变动必须分两阶段完成。首先，集群需要转换到中间态模式，称为 *联合一致性*。

联合一致性同时融合了旧集群和新集群：

- 日志项被复制到了所有旧集群和新集群的服务器上；
- 领袖既可以是旧集群成员也可以是新集群成员；
- 选举领袖和提交日志项需要同时得到旧集群和新集群的大多数成员的同意

集群的配置信息存储在特殊的日志项中，并通过该日志项将配置信息发送给所有成员。当领袖服务器接收到更改集群配置的请求时，其将该请求组成一个联合一致性配置信息日志项 $C_{\mathrm{old,new}}$ 并分发给所有成员，成员一旦将该日志项加入到其日志中，则其在未来的所有决定都是基于该配置信息作出，不管 $C_{\mathrm{old,new}}$ 是否已经被提交。

一旦 $C_{\mathrm{old,new}}$ 被提交，则 Leader Completeness Property 确保只有携带有 $C_{\mathrm{old,new}}$ 日志项的候选者可以当选。此时领袖可以安全地组成一个描述新集群的配置信息日志项 $C_{\mathrm{new}}$ 分发给所有成员，成员一旦接受新配置则立即使用。

上面的方法还有几个问题。

第一个是如果是加入全新的服务器，这些服务器可能并不包含任何日志项，如果日志项很多的话需要花费一定的时间才能让这些服务器的日志项与旧服务器保持一致。在这段时间内也就无法提交新的日志项，更无法执行，相当于整个系统暂停了。为了解决这个问题，Raft 决定在更换配置信息之前加入一个阶段，在这个阶段之内新服务器不具有投票权，但是仍然接受领袖的日志项 AppendEntries RPC，只有在复制了足够的日志项之后才进入下一阶段。

第二个问题是领袖服务器可能并不是新集群的一员，在这种情况下，在领袖提交了 $C_{\mathrm{new}}$ 日志项之后主动卸任，随后由新集群的服务器进行选举。因此存在一个领袖在提交 $C_{\mathrm{new}}$ 前其并不属于集群的一个空档期，在这个空档期间其不算在大多数成员的一员，因此在采票时不包括自己。在 $C_{\mathrm{new}}$ 提交之后，系统也正是退出了联合一致性的状态。

第三个问题是被移除出系统的旧服务器可能会依旧工作（依旧运行 $C_{\mathrm{old,new}}$ 配置信息） ，但是其并不会收到新集群的领袖的心跳信息，因此会自发开始一轮选举，RequestVote RPC 可能会发到新集群的领袖，导致新集群领袖可能会退回到追随者状态，虽然最终新集群还是会选出一个领袖，但是干扰依旧存在。为了解决这个问题，服务器在确定领袖存在时（可以接收到心跳信息），在最小开始选举超时之前会拒绝 RequestVote RPC，如果一直没有接收到领袖的心跳信息才会开始投票。

### 日志压缩

随着系统的运行，系统的日志越来越多，占据的空间越来越多。*快照(snapshot)* 是解决这个问题一个很好的办法。

快照只包含了拍摄快照时的对应日志项的机器状态、日志项索引和任期号（用于 AppendEntries 的一致性检查），为了支持集群成员调整，快照还会包含到该日志项为止时使用的最新的配置日志项，拍摄快照之后，之前的日志项可能全部被丢弃。

尽管各个服务器都是独立拍摄自己的快照，但是领袖服务器还要负责不时将自己的快照发送给各个成员，虽然在正常情况下和领袖保持联系的成员都已经有了快照之前的各日志项，但是运行慢的服务器已经后来加入的成员可能没有该日志项。因此催生出一种新的 RPC 来解决这种情况。

领袖服务器发送 InstallSnapshot RPC 来提醒服务器发送快照，成员接收到该RPC之后需要比较自己的日志信息和RPC的日志信息，如果最新的日志项还不如快照的日志信息，则其丢弃其所有的日志项，只保留该快照。如果成员有部分日志项领先于该快照，则领袖部分保留，其余日志项删除并用快照替代。

### 与客户端交流

客户端只能将请求发送给领袖服务器，客户端与系统第一次进行通信时会随机选择集群的一个服务器，如果不是领袖服务器，则该服务器将拒绝请求并将已知的最新领袖服务器信息返回（ip地址包含在其最新接收的 AppendEntries RPC) 中。

Raft 致力于实现线性化语义（所有操作只能顺序执行且只能执行一次，指客户端的每个请求只执行一次，而无关具体的命令内容）。但是现在为止的 Raft 协议是有可能一个命令执行多次的，比如领袖服务器在提交一个日志项之后还没来记得返回给客户端就宕机了，客户端等待超时后重新发送该命令，导致系统执行同一个命令两次。

因此客户端可以选择给每个命令加一个序列号，如果系统发现已经有该序列号的命令执行过，则可以直接返回执行结果而不用执行多次。系统也不用存储所有执行命令的序列号，只需要保存该客户端执行的最新命令的序列号即可，因为一般每个客户端在前一个命令没有受到成功回复之前不会发送下一个命令的请求。

在 Raft 中读取数据命令不会作为日志项写入日志中，因此存在这样一种情况：新一轮选举已经产生了一个新的领袖，但是原领袖对此并不知情，而客户端刚好找到了原来的领袖读取数据，但是该数据对于整个系统而言可能已经被新领袖修改过了，而客户端收到了旧领袖返回的过时的数据。而如果是需要写入日志项的请求，旧领袖需要将日志项复制到大多数成员才可以执行返回，在这个过程中旧领袖会发现存在比自己任期号更大的领袖，因此退回追随者状态，因此不会发生这种错误。

Raft 对此问题的解决办法是读操作仍然不记入日志，但是需要添加两个限制：第一个，一个领袖必须有已提交领袖的最新消息，Leader Completeness Property 确保了每个领袖都具有所有已提交的日志项，但是在其任期开始时，其 commitIndex 可能并不是整个集群的 commitIndex，因此在其任期开始时，需要提交一个空操作的日志项来确保领袖的 commitIndex 就是整个集群的 commitIndex，则读操作只需等待领袖应用完到达时的 commitIndex 就可以执行了；第二个，每次接收到只读的请求时，收到请求的领袖（不一定是整个系统的领袖）需要与大多数服务器交换心跳信息来确保自己依旧是领袖，确保之后才能回复读请求。

