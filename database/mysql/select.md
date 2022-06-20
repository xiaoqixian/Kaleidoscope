### **SELECT查询**

> 虽然是说select查询，但是WHERE子语句的很多部分都可以用到update和delete语句中。

语法格式：

`select [all|distinct]{*|字段列名} from <表名> [where <表达式> [group by {<字段>|<表达式>|<位置>] [order by <字段1> [desc/asc],<字段2> [desc/asc]] [limit [<offset>] <行数>] with rollup having [条件]]`

- `[all|distinct]`：是否查询不重复的记录。all表示查询所有记录，distinct表示查询不重复的记录。此关键字必须放在开头。

- group by：告诉MySQL如何显示查询出来的数据，并按照指定的字段进行分组。

  三个可选参数分别是字段、表达式和位置。表达式通常与聚合函数一起使用。常见的聚合函数有：

  - count: 返回不同的非NULL值数目，count(*)、count(字段)
  - sum：求和
  - max：求最大值
  - min：最小值
  - avg：平均值
  - group_concat：返回带有来自一个组的连接的非NULL值的字符串结果，组内字符串连接。

  位置用于指定分组的选择列在select语句结果集中的位置，如group by 2表示对于第2列进行逻辑分组。

- order by <字段>：告诉MySQL按照什么样的顺序显示查询的数据。desc表示降序排列，asc表示升序排列。

- limit[\<offset\>] <行数>：限制显示的查询条数，起始偏移量默认是0，只有在输入两个数字时才会认为输入了起始偏移量。

- `with rollup`：表示是否对分类后的结果再进行汇总

- `having [条件]`：条件子句

  与`WHERE`功能相同，用法相同，执行时机不同

  WHERE在开始时执行检测数据，对原数据进行过滤。

  HAVING 对筛选出来的结果再进行一次过滤

  HAVING 后的字段必须是查询出来的，WHERE 后的字段必须是表中存在的。

  WHERE 不可以使用字段的别名，having可以

  WHERE 不可以使用合计函数，一般需要用合计函数时才会用having

  SQL标准要求having必须引用group by子句中的列或用于合计函数中的列

#### UNION

将多个select查询的结果组合成一个结果集合

`select ... union [all|distinct] select ...`

默认使用distinct

建议对每个select查询都是用小括号包裹

需要各select查询的字段数量一致，每个select查询的字段列表（数量、类型）应一致。

#### 子查询

语法格式：

`select * from (select * from tb where id > 0) as subform where id > 1;`

子查询的数据来源是第一次查询的结果，**要求子查询结果必须取别名**。

#### 连接

将多个表的字段进行查询，可以指定查询条件

语法格式：

`select t1.field..., t2.field from t1 inner join t2 on t1.field=t2.field;`

上面的语句就等价于：

`select t1.field, t2.field from t1, t2 where t1.field = t2.field;`

但是这个等价仅适用于内连接的情况。

SQL的连接可以分为三类：

1. inner join（内连接）：获取两个表中字段匹配关系的记录
2. left join（左连接）：获取左表所有记录，即使右表中没有匹配的记录
3. right join（右连接）：与左连接正好相反。

左连接和右连接又统称为外连接。

#### LIKE子句

SQL语句中允许通过like子句进行字符串的匹配，通过百分号`%`来表示任意字符，类似与正则表达式中的`*`。如果没有使用百分号，则效果与等号是一样的。

语法格式为：

`select field1, field2... from tab where field1 like condition1 [and [or]] field2 = "somevalue";`

单是使用`%`匹配任意字符，可以匹配的东西还是太少了。

所以SQL提供了四种匹配方式：

- `%`：匹配任意类型和长度的字符
- `_`：匹配任意单个字符
- `[]`：表示括号内所列字符串中的一个，要求所匹配对象为括号内字符串中的任意一个字符。
- `[^]`：与`[]`相反，要求匹配括号内以外的任意一个字符。
- 如果要匹配特殊字符，可以通过将特殊字符用`[]`括起来实现。

**ESCAPE子句**

SQL默认的转义字符是反斜杠`\`，但是如果想要自己想要指定转义字符，可以通过`escape`实现。