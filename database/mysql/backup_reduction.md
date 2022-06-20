### **备份与还原**

备份：将数据库的结构与表内的数据保存到文件中，可以上传到其他地方。

#### 导出

导出一张表

```sql
mysqldump -u username -p password database_name table_name > file_name
```

导出多张表

```
mysqldump -u username -p password database_name table_name1 table_name2 table_name3 > file_name
```

导出所有表

```
mysqldump -u username -p password database_name > file_name
```

导出一个数据库

```
mysqldump -u username -p password --lock-all-tables --database database_name > filename;
```

可以通过-w携带WHERE条件

#### 导入

在登录MySQL的情况下：

`source 备份文件;`

在不登录的情况下：

`mysql -u username -p password database_name < mysql_file`

