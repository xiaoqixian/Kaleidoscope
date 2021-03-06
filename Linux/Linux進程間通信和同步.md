### **Linux進程間通信和同步**

<font color = red>Armor</font>

Linux下多個進程間的通信機制稱為IPC。多個進程間通信的方法有：半雙工管道、FIFO(命名管道)、消息隊列、信號量、共享內存等。

#### **半雙工管道**

1. 基本概念

   管道是一種將一個進程的輸出與另一個進程的輸入連接起來的機制。在shell命令中通過"|"符號分割兩個管道。將數據從左邊管道傳到右邊管道。

   在創建管道時，內核創造兩個文件描述符來操作管道。其中一個進行寫操作，另一個進行讀操作。

   > 記得以前說過在Linux中"一切皆文件"嗎？在Linux中，管道也會被看成一種文件。而Linux在打開文件時就會分配一個文件描述符。

   但是這兩個進程之間在宏內核的Linux中並不是直接通過管道進行通信的，在它們每次向管道讀或者寫信息的時候，都會先交給內核處理。

2. 管道阻塞和管道操作的原子性

   當管道的寫端沒有關閉時，如果寫請求的字節數目大於閾值PIPE_BUF，則返回目前的字節數，否則返回管道現有的數據字節數。

   當寫入數據小於128K時，寫入是非原子的。反之，如果數據會阻塞在管道中直到前面的數據被讀完。

#### **命名管道**

1. 創建FIFO

   shell命令中可以通過```mkfifo pipe_name```來如同創建文件一樣創建一條管道。

2. FIFO操作

   命名管道默認總是處於阻塞狀態，命名管道打開時如果打開了讀設置，在沒有進程向管道中寫入數據時，該管道總是處於阻塞狀態。寫操作也是如此。

