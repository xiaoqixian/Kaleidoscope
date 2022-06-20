#### **如何在数据库中正确存储时间数据**

时间在web开发中是一种经常需要存储的数据类型。所以有必要好好认识一下如何正确地存储时间。

#### 1. 不要用字符串存储日期

原因：

1. 字符串占用的空间更大；
2. 字符串存储的日期比较效率更低（逐个字符比对），无法用日期相关的API进行计算和比较

#### 2. Datetime 和 Timestamp之间抉择

首选timestacmp

1. Datetime 类型没有时区信息

   当服务器的时区更换后，会导致从数据库读出的时间错误

2. Datetime 类型耗费空间更大

   一个占用4个字节，一个占用8个字节

扩展：一些关于MySQL时区设置的常用SQL命令

```
# 查看当前会话时区
SELECT @@session.time_zone;
# 设置当前会话时区
SET time_zone = 'Europe/Helsinki';
SET time_zone = "+00:00";
# 数据库全局时区设置
SELECT @@global.time_zone;
# 设置全局时区
SET GLOBAL time_zone = '+8:00';
SET GLOBAL time_zone = 'Europe/Helsinki';
```

#### 数值型时间戳

有时也会经常使用数值型时间戳来表示时间。时间戳是从一个绝对的时间起点开始计算，以秒为单位计时。这种时间表示形式不用考虑时区的影响，跨系统也非常方便。就是可读性太差了。