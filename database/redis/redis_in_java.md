---
author: lunar
date: Thu 06 Aug 2020 02:24:27 PM CST
---

### **Java使用Redis**

#### 安装

首先需要安装Java的Redis驱动包，并在classpath中包含该驱动包

#### 连接到Redis服务

```java
import redis.clients.jedis.Jedis; 

public class RedisJava { 
   public static void main(String[] args) { 
      //Connecting to Redis server on localhost 
      Jedis jedis = new Jedis("localhost"); 
      System.out.println("Connection to server sucessfully"); 
      //check whether server is running or not 
      System.out.println("Server is running: "+jedis.ping()); 
   } 
} 
```