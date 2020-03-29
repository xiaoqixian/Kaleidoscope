### **TCP網絡編程**

---

#### **套接字編程**

1. 最常用的套接字數據結構

   在以太網中，一般使用```struct sockaddr_in```作為套接字數據結構。

   ```c
   struct sockaddr_in {
       u8 sin_len; //結構struct sockaddr_in的長度，16
       u8 sin_family; //通常為AF_INET
       u16 sin_port; //16位的端口號，使用網絡字節序
       struct in_addr sin_addr;//IP地址
       char sin_zeros[8];//未用，需要全部置零
   };
   ```

   ```in_addr```的結構為

   ```c
   struct in_addr {
       u32 s_addr; //IP地址，網絡字節序
   };
   ```

2. 用戶層與內核層的交互過程

   * 向內核傳入數據

     向內核傳入數據的函數有send()、bind()函數等，接收數據的有accept()、recv()等。以bind()函數舉例，bind()函數需要向內核傳入地址結構的指針和結構的長度，內核通過指針和長度去響應的內存用內存複製的方式複製到內核。

   * 內核傳出數據

     在內核傳出時同樣需要傳出長度和地址，但是長度在傳入過程中是傳值，傳出是傳址。

---

#### **TCP網絡編程流程**

<font size = 4>**TCP網絡編程架構**</font>

1. 服務器端的程序設計模式
   * 套接字的初始化(socket()):根據用戶定義的網路類型、協議類型和具體的協議標號來定義。生成一個套接字文件描述符。
   * 套接字和端口的綁定bind()
   * 設置服務器的監聽listen()
   * 接收客戶端連接accept():一個服務器可能會面臨多個客戶端的連接請求，所以服務器會設置一個排隊，監聽函數會限制請求連接的排隊長度。
   * 接收和發送數據read()、write()
   * 套接字的關閉close()
   
2. 客戶端的程序設計模式
   * 套接字初始化(socket())
   * 連接服務器connect()
   * 讀寫網絡數據read()、write()
   * 套接字的關閉close()
   
   客戶端與服務端的一大區別就是在socket初始化後不需要綁定端口就可以直接與服務器相連

<font size = 4>**socket()函數**</font>

1. socket函數介紹

   ```c
   #include <sys/types.h>
   #include <sys/socket.h>
   int socket(int domain, int type, int protocol);
   ```

2. socket()與內核函數的關係

   用戶調用socket()函數時，這個函數會首先調用sys_socket()(在net/socket.c中)。這個函數一方面生成內核socket結構，另一方面與文件描述符綁定，傳回給應用層。

<font size = 4>**bind()函數**</font>

1. 介紹

   ```c
   int bind(int sockfd, const struct sockaddr *my_addr, socklen_t addrlen);
   ```

   sockaddr中包含了地址、端口和IP地址的信息。

2. 與內核的關係

<font size = 4>**listen()函數**</font>

1. 介紹

   ```c
   int listen(int sockfd, int backlog);
   ```

   backlog參數表示在accept()函數處理之前等待隊列的長度，超過這個長度則返回ECONNREFUSED錯誤。

<font size = 4>accept()函數</font>

1. 介紹

   ```int accept(int sockfd, struct sockaddr *addr, socklen_t *addrlen);```

   通過accept()函數可以得到連接客戶端的IP地址、端口和協議族信息。這個函數會通過sockfd接收來自客戶端的連接請求，並將客戶端的地址信息存儲在```addr```指針中，並返回一個客戶端的文件描述符。

<font size = 4>**connect()函數**</font>

1. 介紹

   ```int connect(int sockfd, struct sockaddr* serv_addr, int addrlen);```