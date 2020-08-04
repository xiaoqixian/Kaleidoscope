### **Redis常用配置说明**

1. redis默认不是以守护进程的方式运行，修改

   `CONFIG SET daemonize yes`

   所谓守护进程，即在后台运行，不受命令行终端控制的一种进程。

2. 当客户端闲置多久后关闭连接

   `CONFIG SET timeout 300`

3. 指定日志的记录级别。redis支持四个级别：debug, verbose, notice, warning，默认为verbose

   `CONFIG SET loglevel verbose`

4. 日志输出方式，默认使用标准输出

   `CONFIG SET logfile stdout`

   如果是守护进程形式的话，默认输出到/dev/null，也就是不记录。

5. 指定在多长时间内，有多少个更新操作，就将数据同步到数据库文件。可以有多个条件配合使用

   `CONFIG SET save <seconds> <changes>`

6. 指定存储到本地时是否压缩数据，默认压缩。是否要进行压缩应当在CPU负载和磁盘空间中做出权衡。

   `CONFIG SET rdbcompression yes`

7. 指定本地数据库文件名，默认dump.rdb

   `CONFIG SET dbfilename name.rdb`

   以及本地数据库存放地址

   `CONFIG SET dir ./`

8. 如果设置本机为slave服务，则需要设置master服务的IP和端口，在本机redis启动时，需要自动从master进行数据同步

   `CONFIG SET slaveof <masterip> <masterport>`

   