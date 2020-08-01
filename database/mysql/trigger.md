### **触发器**

触发程序是与表有关的命名数据库对象，当该表出现人特定事件时，将激活该对象。

#### 创建触发器

`CREATE TRIGGER trigger_name trigger_time trigger_event ON table_name FOR EACH ROW trigger_statement;`

- trigger_time：before | after，指明触发程序是在激活它的语句之前还是之后触发。
- trigger_event：指明了激活触发器的语句类型
  - INSERT：新行插入表时触发
  - UPDATE：更改某一行时触发
  - DELETE：从表中删除一行时触发
- table_name：必须是永久性的表，不能是暂时表或者视图
- trigger_statement：激活触发器后执行的语句，可以执行多个语句，可以使用BEGIN...END符合语句结构

#### 删除触发器

`DROP TRIGGER trigger_name;`

注意：一个表不能有两个相同触发时间和触发事件的触发程序

```sql
-- 特殊的执行
1. 只要添加记录，就会触发程序。
2. Insert into on duplicate key update 语法会触发：
    如果没有重复记录，会触发 before insert, after insert;
    如果有重复记录并更新，会触发 before insert, before update, after update;
    如果有重复记录但是没有发生更新，则触发 before insert, before update
3. Replace 语法 如果有记录，则执行 before insert, before delete, after delete, after insert
```

