### **SQL编程**

#### 局部变量

变量声明：`declare var_name type [default_value];`

该语句用于声明局部变量。

#### 全局变量

`set @var = value;`

也可以用select into语句进行赋值，这就要求select语句只能返回一行，但是可以是多个字段，用于给多个变量同时赋值，变量的数量需要与查询的列数一致。

```sql
select @var:=20;
select @v1:=id, @v2=name from t1 limit 1;
select * from tbl_name where @var:=30;
select into 可以将表中查询获得的数据赋给变量。
如:
select max(height) into @max_height from tb;
#注意，MySQL数据库不支持select into语句。
```

`@`定义的变量在定义后，在整个个会话周期内都有效。

#### 控制结构

if语句

```sql
if condition then
	statements
[elseif condition then
	statements]
[else
 	statements]
endif;
```

case语句

```sql
CASE value WHEN [compare-value] THEN result
[WHEN [compare-value] THEN result ...]
[ELSE result]
END
```

while循环

```SQL
[begin_label:] while search_condition do
    statement_list
end while [end_label];
```

如果需要在循环终止前退出循环，则需要使用标签；标签需要成对出现。

- 退出整个循环：leave
- 退出当前循环：iterate

通过退出的标签决定退出哪个循环

#### 内置函数

```sql
-- 数值函数
abs(x)          -- 绝对值 abs(-10.9) = 10
format(x, d)    -- 格式化千分位数值 format(1234567.456, 2) = 1,234,567.46
ceil(x)         -- 向上取整 ceil(10.1) = 11
floor(x)        -- 向下取整 floor (10.1) = 10
round(x)        -- 四舍五入去整
mod(m, n)       -- m%n m mod n 求余 10%3=1
pi()            -- 获得圆周率
pow(m, n)       -- m^n
sqrt(x)         -- 算术平方根
rand()          -- 随机数
truncate(x, d)  -- 截取d位小数
-- 时间日期函数
now(), current_timestamp();     -- 当前日期时间
current_date();                 -- 当前日期
current_time();                 -- 当前时间
date('yyyy-mm-dd hh:ii:ss');    -- 获取日期部分
time('yyyy-mm-dd hh:ii:ss');    -- 获取时间部分
date_format('yyyy-mm-dd hh:ii:ss', '%d %y %a %d %m %b %j'); -- 格式化时间
unix_timestamp();               -- 获得unix时间戳
from_unixtime();                -- 从时间戳获得时间
-- 字符串函数
length(string)          -- string长度，字节
char_length(string)     -- string的字符个数
substring(str, position [,length])      -- 从str的position开始,取length个字符
replace(str ,search_str ,replace_str)   -- 在str中用replace_str替换search_str
instr(string ,substring)    -- 返回substring首次在string中出现的位置
concat(string [,...])   -- 连接字串
charset(str)            -- 返回字串字符集
lcase(string)           -- 转换成小写
left(string, length)    -- 从string2中的左边起取length个字符
load_file(file_name)    -- 从文件读取内容
locate(substring, string [,start_position]) -- 同instr,但可指定开始位置
lpad(string, length, pad)   -- 重复用pad加在string开头,直到字串长度为length
ltrim(string)           -- 去除前端空格
repeat(string, count)   -- 重复count次
rpad(string, length, pad)   --在str后用pad补充,直到长度为length
rtrim(string)           -- 去除后端空格
strcmp(string1 ,string2)    -- 逐字符比较两字串大小
-- 聚合函数
count()
sum();
max();
min();
avg();
group_concat()
-- 其他常用函数
md5();
default();
```

#### 自定义函数

语法格式：

```sql
CREATE FUNCTION function_name(args) RETURNS result_type
	function body
```

注意事项：

- 一个函数应该属于某个数据库，可以使用`db_name.function_name`的形式来调用其它数据库的函数，否则默认为当前数据库
- 参数部分有参数名和参数类型构成，多个参数之间通过逗号分隔
- 函数体如果有多条语句需要用 begin...end 语句块包括
- 一定要有return 返回值语句

删除函数

`DROP FUNCTION [IF EXISTS] function_name;`

查看所有函数

`SHOW FUNCTION STATUS LIKE 'pattern';`

查看某个函数的具体信息

`SHOW CREATE FUNCTION function_name;`

#### 存储过程

存储过程，通常是一段代码，存储在数据库中的SQL组成。

一个存储过程通常用于完成一段业务逻辑，例如报名，交班费，订单入库等。

存储过程通过`call`调用执行，没有返回值，只能单独调用执行，不能夹杂在其它语句中。

**创建存储过程**

```sql
CREATE PROCEDURE procedure_name (args)
BEGIN
	body
END
```

参数

```
-- 参数
IN|OUT|INOUT 参数名 数据类型
IN      输入：在调用过程中，将数据输入到过程体内部的参数
OUT     输出：在调用过程中，将过程体处理完的结果返回到客户端
INOUT   输入输出：既可输入，也可输出
```