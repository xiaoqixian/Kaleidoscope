#### **C/C++ extern**

extern可以置於變量或者函數前，以標示變量或者函數的定義在別的文件中，提示編譯器遇到此變量和函數時在其他模塊中尋找其定義。

extern的兩個作用：

1. extern "C" void fun()：告訴C++編譯器在編譯fun時按照C的編譯方式去編譯，因為C語言編譯後函數不會變化，**而C++因為要支持重載，所以會將函數和參數聯合起來生成一個中間函數的名稱**。所以比較適用於一些根據字符串去調用函數的情況。

   extern "C"的標準寫法:

   ```c++
   #ifdef __cplusplus
   #if __cplusplus //#if和#ifdef相同
   extern "C"{
   　#endif
   　#endif /* __cplusplus */
   　…
   　…
   　//.h文件结束的地方
   　#ifdef __cplusplus
   　#if __cplusplus
   }
   #endif
   #endif /* __cplusplus */ 
   ```

   

extern用在变量声明中常常有这样一个作用，你在.c文件中声明了一个全局的变量，这个全局的变量如果要被引用，就放在.h中并用extern来声明。如果直接在.h文件中聲明並定義這個extern變量會產生相當於沒有這個extern修飾的效果(迷惑)。容易產生鏈接錯誤。總的說就是因為extern修飾的變量是整個工程共享的變量，應該整個工程只有一份，如果直接include會多次定義extern變量導致報錯。事實上gcc編譯器已經不允許在.h文件中實例化extern變量了。

最後引一位博主的評論：

>假如a.h中有 int a=10; t1.cpp和t2.cpp同时include "a.h"则编译不成功，因为a重复定义；
>如果 a.h中是 static int a=10;则可以，因为t1和t2中的a只是名字相同，地址空间不同；
>如果a.h中是 extern int a; 并且在a.cpp中 int a=10; 则t1和t2中的a指向同一个地址空间。