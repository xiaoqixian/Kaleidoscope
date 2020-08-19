---
author: lunar
date: Wed Aug 19 13:08:08 2020
---

### MATLAB决策

#### 判断语句

在每个if语句后面都要添加end关键字。其余部分与其它编程语言一致。

#### 循环语句

**while循环**

```matlab
while <expression>
    <statement>
end
```

**for循环**

```matlab
for index = values
    <statement>
end
```

values的格式为
- initval:endval: index变量从initval到endval每次递增1，并重复程序语句的行，直到index大于endval
- initval:step:endval: index变量从initval到endval每次递增step，并重复程序语句的行，直到index大于endval
- valArray: 在每次迭代中从数组valArray的后续列创建列向量索引，依次取出数组中的元素

在循环语句中同样可以使用continue和break语句。
