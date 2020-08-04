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

   当master主机设置了密码保护时，需要设置master密码
   
   `CONFIG SET masterauth <master-password>`
   
9. 设置最大客户机连接数

10. 指定redis的最大内存限制，当达到最大内存时，redis会尝试清除到期或即将到期的key。如果仍然达到最大内存限制，redis将禁止写操作。但是仍然可以读。在Redis新的vm机制中，Redis会将key放入内存，而value放入交换内存区。

    `CONFIG SET maxmemory <bytes>`

11. 指定是否开启在每次更新操作后进行日志记录，因为Redis是异步地将数据写入磁盘，如果没有日志记录，可能在断电的一段时间内数据无法找回。默认不开启

    `CONFIG SET appendonly no`

    还可以指定更新日志名

12. 指定是否使用虚拟内存机制，默认为no。

    vm机制将数据分页存放，访问量少的页面被交换到磁盘中，访问量大的页面被交换到内存中（如果不在内存中的话）。

    `CONFIG SET vm-enabled no`

    虚拟内存文件路径

    `CONFIG SET vm-swap-file /tmp/redis.swap`

13. vm-max-memory

    将所有大于vm-max-memory的数据存入内存，无论这个值设置多小。所有的key都是存储在内存中的，当设置为0时，所有的value都将存储到磁盘中。

14. vm-page-size

    分页大小，如果存储很多小对象，则分页设置小一点。

15. vm-pages

    设置swap文件中的page数量，由于页表是存储在内存中的，在磁盘上的每8个pages都将消耗1byte的内存。

16. vm-max-threads

    设置访问swap文件中的线程数，最好不要超过机器的核数。默认4

17. glueoutputbuf

    设置在向客户端应答时，是否将较小的包合并为一个包发送，默认开启

18. include

    指定包含其它的配置文件