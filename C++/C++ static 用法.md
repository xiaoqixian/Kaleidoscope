### **C++ static 用法**
1. 靜態存儲區：靜態變量存儲的空間分為DATA段和BBS段。DATA段用於存放已經初始化的靜態變量，BBS段存放未初始化的。BBS段在程序開始執行前會被系統自動置為0。於是完成了靜態變量的初始化。
2. c++的static的內部實現機制要求static變量在程序開始執行前就已經完成了初始化，不能在任何函數內分配空間和初始化。
3. static修飾全局變量時，這個全局變量只能在本文件訪問，即便是extern修飾也不能在外部訪問。修飾函數時也是這樣。
4. 即便是函數內部定義的靜態局部變量也是放入全局數據區，直到函數運行結束才釋放內存。
5. 函數內產生的自動變量放在棧區，如定義了一個int變量。產生的動態數據放在堆區，如通過malloc或new產生的對象。
```
//來自菜鳥教程的源代碼
//example:
#include <stdio.h>  
#include <stdlib.h>  
int k1 = 1;
int k2;
static int k3 = 2;
static int k4;
int main()
{
    static int m1 = 2, m2;
    int i = 1;
    char*p;
    char str[10] = "hello";
    char*q = "hello";
    p = (char *)malloc(100);
    free(p);
    printf("栈区-变量地址    i：%p\n", &i);
    printf("栈区-变量地址   p：%p\n", &p);
    printf("栈区-变量地址 str：%p\n", str);
    printf("栈区-变量地址   q：%p\n", &q);
    printf("堆区地址-动态申请：%p\n", p);
    printf("全局外部有初值 k1：%p\n", &k1);
    printf("   外部无初值 k2：%p\n", &k2);
    printf("静态外部有初值 k3：%p\n", &k3);
    printf("   外静无初值 k4：%p\n", &k4);
    printf("  内静态有初值 m1：%p\n", &m1);
    printf("  内静态无初值 m2：%p\n", &m2);
    printf("    文字常量地址：%p, %s\n", q, q);
    printf("      程序区地址：%p\n", &main);
    return 0;
}
```
6. 靜態函數內部不能調用非靜態函數也不能引用非靜態變量，因為在靜態函數調用時可能類並沒有初始化。而非靜態則可以調用靜態變量和函數。