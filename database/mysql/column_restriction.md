### **Mysql列约束**

1. 主键

   能够唯一表示记录的字段，一个表只能有一个主键。

   主键的值不能为null。

   主键虽然只能有一个，但是可以多个字段共同组成一个主键。

   例如：`create table tab (id int, stu varchar(10), age int, primary key(stu, age));`

2. UNIQUE

   唯一索引，使得某个字段即使不是主键也不允许被重复。

3. NULL约束

   一般通过not null来不允许字段为空。

4. DEFAULT默认值

5. AUTO_INCREMENT 自动增长约束

   自动增长必须为索引（主键或unique）

   只能存在一个字段为自动增长。

   默认从1开始字段增长，也可以通过auto_increment=x进行设置

6. COMMENT 注释

   例如：`create table tab (id int) comment '注释内容';

7. FOREIGN KEY 外键约束

   用于限制主表与从表的数据完整性

   语法格式：

   `alter table t1 add constraint t1_t2_fk foreign key (t1_id) references t2(id) on update/delete <action>;`

   这段命令的意思是将t1表的id字段关联到t2表的id字段。因此t1称为从表，t2称为主表。

   允许关联的操作一般是更新和删除，插入一般不允许，因为两个数据表一般字段会存在不一样的。

   MySQL支持五种处理时触发的动作：

   1. CASCADE: 更新或删除主表记录时，自动更新或删除从表的匹配的记录。
   2. SET NULL：更新或删除主表记录时，将从表中匹配的记录设置为NULL。
   3. RESTRICT：默认项。禁用来自主表的更新或删除操作。
   4. NO ACTION：与上一项完全等效
   5. SET DEFAULT：MySQL可以解析该工作，但是InnoDB和NDB引擎不支持。

   **使用外键前提**：MySQL引擎必须为InnoDB，MyISAM不支持。

