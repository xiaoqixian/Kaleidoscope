### **SQL运算符**

#### 算术运算符

加、减、乘、除、求余

#### 比较运算符

正则式匹配：REGEXP或RLIKE

安全等于：`<=>`，与=的区别为可以比较null和null，如果是等于号的话只要存在null就返回false，`<=>`则是两个都null时也可以返回True

#### 运算符优先级

![](https://www.runoob.com/wp-content/uploads/2018/11/1011652-20170416163043227-1936139924.png)

#### NULL值处理

我们已经知道MySQL使用SQL select命令及WHERE子句来读取数据表中的数据，但是当提供的查询字段为NULL时，该命令可能就无法正常工作。

为了处理情况，MySQL提供了三种运算符：

- IS NULL：当列的值是NULL时，此运算符返回true
- IS NOT NULL：非NULL时，返回True
- <=>：比较操作符（不同于=运算符），当比较的两个值相等或都为NULL时，返回True

