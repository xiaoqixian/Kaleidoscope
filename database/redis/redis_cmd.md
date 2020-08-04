#### 与键相关的命令

| cmd                      | description                        |
| ------------------------ | ---------------------------------- |
| del key                  | 删除键                             |
| dump key                 | 序列化给定键，并返回被序列化的值   |
| exists key               | 键是否存在                         |
| expire key seconds       | 设置键过期的时间                   |
| expireat key timestamp   | 接受Unix时间戳作为过期时间         |
| pexpire key milliseconds | 设置键的过期时间以毫秒计           |
| keys pattern             | 查找符合pattern的键                |
| move key db              | 将当前数据库的键移动到给定数据库中 |
| persist key              | 删除键的过期时间，一直保留在内存中 |
| pttl key                 | 以毫秒为单位返回键的剩余的过期时间 |
| ttl key                  | 以秒为单位...                      |
| randomkey                | 随机返回一个键                     |
| rename key newkey        | 重命名键                           |
| renamenx key newkey      | 当新键不存在时才执行重命名         |
| type key                 | 返回键的类型                       |

#### 与字符串相关的命令

| CMD                             | DESCRIPTION                                |
| ------------------------------- | ------------------------------------------ |
| set key value                   |                                            |
| get key                         |                                            |
| getrange key start end          |                                            |
| getset key value                | 为键设置新的值并返回旧的值                 |
| getbit key offset               | 返回键的值的字符串一定偏移处的位值         |
| mget key1 [key2...]             | 返回多个键的值                             |
| setbit key offset value         | 设置键的值的字符串一定偏移处的位值         |
| setex key secodes value         | 设置键到期时的值                           |
| setrange key offset value       | 设置键的字符串从一定偏移处开始的字符串部分 |
| strlen key                      | 返回字符串的长度                           |
| mset key value [key value...]   | 设置多个键值对                             |
| msetnx key value [key value...] | 当多个键都不存在时，设置多个键的值         |
| psetex key milliseconds value   | 设置键的值和过期时间（单位为毫秒）         |
| incr key                        | 将键的整数值递增1                          |
| incrby key increment            | 设置键递增的量，整数                       |
| incrbyfloat key increment       | 按给定量增加键的浮点值                     |
| decr key                        | 键的整数值递减1                            |
| decrby key decrement            |                                            |
| append key value                | 将值附加到键                               |
|                                 |                                            |

#### 与哈希有关的命令

| CMD                                     | Description                      |
| --------------------------------------- | -------------------------------- |
| hdel key field2 [field2]                | 删除一个或多个哈希字段           |
| hexists key field                       | 确定是否存在哈希字段             |
| hget key field                          | 获取指定键中的哈希字段的值       |
| hgetall key                             | 获取指定键中的所有哈希字段的值   |
| hkeys key                               | 获取哈希中的所有字段             |
| hlen key                                | 获取字段数                       |
| hmget key1 [field2]                     | 获取所有给定哈希字段的值         |
| hmset key field1 value1 [field2 value2] | 设置键的多个字段的多个值         |
| hset key field                          | 设置哈希字段的字符串值           |
| hsetnx key field                        | 仅当字段不存在时设置哈希字段的值 |
| hvals key                               | 获取哈希值中的所有值             |

#### 与列表有关的命令

这些命令中与单词无关的L和R分别代表列表的左和右，由此可以推知一个命令的其它形式

| CMD                                   | Description                                                  |
| ------------------------------------- | ------------------------------------------------------------ |
| BLPOP key1 [key2] timeout             | 删除和获取列表中的第一个元素，或阻塞知道一个元素可用。timeout应该是用于设置最长阻塞时间 |
| BRPOPLPUSH source destination timeout | 从source中删除最后一个元素并push到destination中              |
| LINDEX key index                      | 根据索引获得值                                               |
| LINSERT key before\|after pivot value | 插入值                                                       |
| LLEN key                              | 列表长度                                                     |
| LPOP key                              | 删除头部                                                     |
| LPUSH key value1 [value2]             | 头部插入元素                                                 |
| LPUSHX key value1 [value2]            | 列表存在时才插入                                             |
| LRANGE key start stop                 | 展示列表范围内的元素                                         |
| LREM key count value                  | 从列表删除元素                                               |
| LSET key index value                  | 设置索引处的值                                               |
| LTRIM key start stop                  | 将列表修剪到指定范围                                         |
| RPUSH key value1 [value2]             | 尾部插入                                                     |

#### 与集合有关的命令

| CMD                                            | Description                                   |
| ---------------------------------------------- | --------------------------------------------- |
| SADD key member1 [member2]                     | 增加集合成员                                  |
| SCARD key                                      | 获取集合中成员数量                            |
| SDIFF key1 [key2]                              | 返回所有集合的差集                            |
| SDIFFstore destination key1 [key2]             | 返回所有集合的差集并将结果存储在destination中 |
| SINTER key1 [key2]                             | 返回所有集合的交集                            |
| SINTERSTORE destination key1 [key2]            | 返回所有集合的交集并将结果存储在destination中 |
| SISMEMBER key member                           | 判断member是否是key对应集合的成员             |
| SMOVE source destination member                | 将member从source移动到destination             |
| SPOP key                                       | 移除并返回集合中的一个随机元素                |
| SRANDMEMBER key [count]                        | 返回集合中的一个或多个随机数                  |
| SREM key member1 [member2]                     | 移除集合中的一个或多个成员                    |
| SUNION key1 [key2]                             | 返回给定集合的并集                            |
| SUNIONSTORE destination key1 [key2]            | 返回给定集合的并集并存储到destination中       |
| SSCAN key cursor [match pattern] [count count] | 迭代集合中的元素                              |

#### 与有序集合有关的命令

有序集合的命令大部分与集合相同（命令前缀要从S改成Z），所以这里只列举不同的部分。

| CMD                            | Description                                            |
| ------------------------------ | ------------------------------------------------------ |
| ZCOUNT key min max             | 返回集合指定分数区间内的成员数                         |
| ZLEXCOUNT key min max          | 计算指定字典区间内的成员数量                           |
| ZRANGE key start stop          | 通过索引区间返回指定区间内的成员                       |
| ZRANGEBYLEX key min max        | 通过字典区间返回指定区间内的成员                       |
| ZRANGEBYSCORE key min max      | 通过分数区间返回指定区间内的成员                       |
| ZRANK key member               | 返回有序集合中的指定成员的索引                         |
| ZREMRANGEBYLEX key min max     | 通过字典区间删除集合中的成员                           |
| ZREMRANGEBYRANK key start stop | 通过索引区间删除集合中的成员                           |
| ZREMRANGEBYSCORE key min max   | 通过分数区间删除集合中的成员                           |
| ZREVRANGE key start stop       | 返回有序集合中指定区间内的成员，通过索引，分数从高到低 |
| ZREVRANGEBYSCORE key max min   | 返回有序集合中指定区间内的成员，通过分数从高到低       |
| ZREVRANK key member            | 返回有序集合中指定成员的排名                           |
| ZSCORE key member              | 返回指定成员的分数                                     |
|                                |                                                        |

