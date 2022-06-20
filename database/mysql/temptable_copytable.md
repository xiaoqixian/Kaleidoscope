### **临时表和复制表**

#### 临时表

临时表在保存一些临时数据时非常有用。临时表只在当前连接有效，当关闭当前连接时，临时表就会被销毁并释放空间。

1. 创建临时表

   只需要在创建表时在TABLE前面加一个TEMPORARY关键字，其它步骤与创建普通表相同

2. 删除临时表

   DROP删除表

3. 查询创建临时表的方式

   ```sql
   CREATE TEMPORARY TABLE table_name AS
   (
   	SELECT * FROM other_table LIMIT 0,10000;
   );
   ```

   只是一个举例

#### 复制表

复制表是一个动作。将一个表的结构和数据完全复制到另一个表中。

```sql
CREATE TABLE target_table LIKE source_table;
INSERT INTO target_table SELECT * FROM source_table;
```

如果只想拷贝其中的一些字段：

```sql
CREATE TABLE target_table AS
(
	SELECT field1, field2 FROM source_table
);
```

可以将新建的字段改名：

```sql
CREATE TABLE target_table AS
(
	SELECT field1 as new_field1, field2 as new_field2 FROM source_table
);
```

