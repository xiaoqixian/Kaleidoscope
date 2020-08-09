---
author: lunar
date: Sun 09 Aug 2020 08:49:59 PM CST
---

### GeoHash查找附近的人

GeoHash算法将二维的经纬度数据映射到一维的整数，这样所有的元素都将挂载到一条线上，距离相近的二维坐标映射到一维后也会很接近。当我们要计算「附近的人时」时，首先将目标位置映射到这条线上，然后在这个一维的线上获取附近的点就行了。

GeoHash的核心思想是将整个地球看成一个二维的平面，然后这个平面不断地等分成一个一个小的方格，每一个方格元素都位于其中的唯一一个方格中，等分之后的方格越小，坐标就越准确。

将所有的方格经过特殊的编码之后，均可以表示称一串二进制编码。然后经过`Base32`的编码操作，可以将其编程一个字符串。

### 在Redis中使用Geo

在Redis中，Geo的内部数据结构是zset。通过zset的score排序就可以得到坐标附近的其他元素，通过将score还原成坐标值就可以得到元素的原始坐标了。

#### 增加元素

`geoadd`指令携带集合名称以及多个经纬度名称三元组

```redis
127.0.0.1:6379> geoadd company 116.48105 39.996794 juejin
(integer) 1
127.0.0.1:6379> geoadd company 116.514203 39.905409 ireader
(integer) 1
127.0.0.1:6379> geoadd company 116.489033 40.007669 meituan
(integer) 1
127.0.0.1:6379> geoadd company 116.562108 39.787602 jd 116.334255 40.027400 xiaomi
(integer) 2
```
redis没有提供删除指令，但是可以使用zset的`zrem`指令进行删除。

#### 计算距离

使用`geodist`指令来计算集合内两个元素的距离，携带集合名称、2个元素名称和一个距离单位。

```redis
127.0.0.1:6379> geodist company juejin ireader km
"10.5501"
127.0.0.1:6379> geodist company juejin meituan km
"1.3878"
127.0.0.1:6379> geodist company juejin jd km
"24.2739"
127.0.0.1:6379> geodist company juejin xiaomi km
"12.9606"
127.0.0.1:6379> geodist company juejin juejin km
"0.0000"
```

#### 获取元素位置

`geopos`指令获取元素位置，可以一次获取多个

```redis
127.0.0.1:6379> geopos company juejin
1) 1) "116.48104995489120483"
 2) "39.99679348858259686"
127.0.0.1:6379> geopos company ireader
1) 1) "116.5142020583152771"
 2) "39.90540918662494363"
127.0.0.1:6379> geopos company juejin ireader
1) 1) "116.48104995489120483"
 2) "39.99679348858259686"
2) 1) "116.5142020583152771"
 2) "39.90540918662494363"
```

#### 附近的公司

`georadiusbymember`用来查询指定元素附近的元素，它的参数非常复杂

```redis
# 范围 20 公里以内最多 3 个元素按距离正排，它不会排除自身
127.0.0.1:6379> georadiusbymember company ireader 20 km count 3 asc
1) "ireader"
2) "juejin"
3) "meituan"
# 范围 20 公里以内最多 3 个元素按距离倒排
127.0.0.1:6379> georadiusbymember company ireader 20 km count 3 desc
1) "jd"
2) "meituan"
3) "juejin"
# 三个可选参数 withcoord withdist withhash 用来携带附加参数
# withcoord 显示坐标值
# withdist 很有用，它可以用来显示距离
# withhash 显示hash值
127.0.0.1:6379> georadiusbymember company ireader 20 km withcoord withdist withhash count 3 asc
1) 1) "ireader"
 2) "0.0000"
 3) (integer) 4069886008361398
 4) 1) "116.5142020583152771"
 2) "39.90540918662494363"
2) 1) "juejin"
 2) "10.5501"
 3) (integer) 4069887154388167
 4) 1) "116.48104995489120483"
 2) "39.99679348858259686"
3) 1) "meituan"
 2) "11.5748"
 3) (integer) 4069887179083478
 4) 1) "116.48903220891952515"
 2) "40.00766997707732031"
```

#### 注意事项

在一个地图应用中，车的数据、餐馆的数据、人的数据可能会有百万千万条，如果使用 Redis 的 Geo 数据结构，它们将 全部放在一个 zset 集合中。在 Redis 的集群环境中，集合可能会从一个节点迁移到另一个节点，如果单个 key 的数据过大，会对集群的迁移工作造成较大的影响，在集群环境中单个 key 对应的数据量不宜超过 1M，否则会导致集群迁移出现卡顿现象，影响线上服务的正常运行。

所以，这里建议 Geo 的数据使用**单独的**Redis 实例部署，不使用集群环境。

如果数据量过亿甚至更大，就需要对 Geo 数据进行拆分，按国家拆分、按省拆分，按市拆分，在人口特大城市甚至可以按区拆分。这样就可以显著降低单个 zset 集合的大小。
