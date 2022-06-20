### ALTER命令

当需要修改数据表名或表中字段时，需要用到alter命令。

#### 删除，增加或修改表字段

1. 删除字段

   `ALTER TABLE table_name DROP field_name;`

   当表中只剩下最后一个字段时无法使用DROP来删除。

2. 增加字段

   `ALTER TABLE table_name ADD field_name TYPE AFTER field_name;`

   AFTER用于指定字段的位置。

   如果是想要放在第一位，可以使用FIRST指定位置。

3. 修改字段

   在ALTER命令中使用MODIFY或CHANGE子句

   例如，将字段c的类型从CHAR（1）改为CHAR（10），可以执行：

   `ALTER TABLE table_name MODIFY c char(10);`

   而使用CHANGE可以用：

   `ALTER TABLE table_name CHANGE c c char(10);`

   这样看来，MODIFY是在原字段上面进行修改，而CHANGE是直接将新的字段代替原来的字段。

4. 修改字段默认值

   `ALTER TABLE table_name ALTER field_name SET DEFAULT default_name;`

   同样还可以删除字段的默认值

   `ALTER TABLE table_name ALTER field_name DROP DEFAULT;`

5. 修改表名

   `ALTER TABLE table_name RENAME TO new_name;`

#### 使用ALTER命令来添加和删除索引

