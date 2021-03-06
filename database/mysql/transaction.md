### **事务**

MySQL事务主要用于处理操作量大，复杂度高的数据。比如在人员管理系统中删除一个人员时，需要删除基本资料，职务信息等，这些往往不是存储在一个数据表中的，所有这些数据库语句就构成了一个事务。

MySQL中只有使用了InnoDB引擎的数据库或表才支持事务。

事务可以保证语句执行的完整性，一个事务的所有语句要么均被正确地执行，要么都没有执行。

一般事务需要满足四个性质：

- 原子性：一个事务所有的语句执行看做一个整体，要么都完成，要么都没有完成。如果中间发生差错，数据表就会回滚到事务前的状态。

- 一致性：事务开始之前和结束之后，数据库的完整性没有被破坏。这表示写入的资料必须完全符合所有的预设规则，这包含资料的精确度、串联性以及后续数据库可以自发性地完成预定的工作。

- 隔离性：数据库允许多个并发事务同时对其数据进行读写和修改的能力，隔离性可以防止多个事务并发执行时而导致数据的不一致。

  隔离事务分为不同级别：读未提交（Read uncommitted），读提交（Read committed），可重复读（repeatable read），串行化（Serializable）

- 持久性：事务处理结束后，对数据的修改是永久的。

#### 事务控制语句

- BEGIN或者START TRANSACTION：显式地开启一个事务；
- COMMIT：提交事务，并对数据库造成永久性的修改；
- ROLLBACK：回滚会结束用户的事务，并撤销所有正在进行的**未提交**的修改
- SAVEPOINT identifier：在事务创建一个保存点，一个事务中允许创建多个保存点；
- RELEASE SAVEPOINT identifier：删除一个事务的保存点，没有指定保存点的话会报错；
- ROLLBACK TO identifier：将事务回滚到某个保存点；
- SET TRANSACTION：用来设置事务的隔离级别；

#### 自动提交特性

MySQL另一种开启事务的方式是设置自动提交的开启与关闭。

`SET autocommit = 0|1; `

0表示关闭自动提交，1表示开启自动提交。

如果关闭了自动提交，则所有SQL语句执行后同样需要commit以后才能生效。

与上一种方式的区别是`SET autocommit`可以永久改变服务器的设置，直到下次修改该设置。

而`BEGIN`则是记录开启前的状态，一旦事务提交或回滚后就需要再次开启事务。

#### 事务的原理

事务的原理正是利用了上面提到的数据库的自动提交特性。开启一个事务后会暂时关闭“自动提交”机制，需要commit提交持久化数据操作。

#### 并发事务带来的问题

在典型的应用程序中，多个事务并发运行，经常会操作相同的数据来完成各自的任务。可能会导致下列问题：

- **脏读**：当一个事务正在访问数据并进行了修改，但是还没有提交到数据库。这时另一个事务读取了这个尚未修改的数据，也就是”脏数据“。
- **丢失修改**：指在一个事务读取一个数据时，另外一个事务也访问了该数据，那么在第一个事务中修改了这个数据后，第二个事务也修改了这个数据。这样第一个事务内的修改结果就被丢失，因此称为丢失修改。 例如：事务1读取某表中的数据A=20，事务2也读取A=20，事务1修改A=A-1，事务2也修改A=A-1，最终结果A=19，事务1的修改被丢失。
- **不可重复读**：在一个事务内多次读取数据时，这个事务还没有结束时，另一个事务访问该数据并进行修改。这样前一个事务前面读取的数据与后面读取的数据不一致，可能导致错误。
- **幻读（Phantom Read）**：幻读与不可重复读类似。它发生在一个事务（T1）读取了几行数据，接着另一个并发事务（T2）插入了一些数据时。在随后的查询中，第一个事务（T1）就会发现多了一些原本不存在的记录，就好像发生了幻觉一样，所以称为幻读。
- 不可重复读与幻读的区别：不可重复读的重点是修改，幻读的终点在于新增或删除

#### 事务隔离级别

SQL定义了四个隔离级别：

- RAED-UNCOMMITTED（读取未提交）：最低的隔离级别，允许读取尚未提交的数据变更，可能会导致脏读、幻读或不可重复读
- READ-COMMITTED（读取已提交）：允许读取已经提交的数据，依然无法阻止幻读和不可重复读
- REPEATABLE-READ（可重复读）：对同一字段的多次读取结果是相同的，除非数据被本事务修改。依旧无法阻止幻读。为InnoDB引擎默认的隔离级别。
- SERIALIZABLE（可串行化）：最高的隔离级别，完全服从ACID的隔离级别。所有事务依次执行，完全没有并行的概念。

因为隔离级别越低，事务请求的锁越少，所以大部分数据库系统的隔离级别都是**READ-COMMITTED(读取提交内容):**，但是你要知道的是InnoDB 存储引擎默认使用 **REPEATABLE-READ（可重读）**并不会有任何性能损失。

InnoDB 存储引擎在 **分布式事务** 的情况下一般会用到**SERIALIZABLE(可串行化)**隔离级别。