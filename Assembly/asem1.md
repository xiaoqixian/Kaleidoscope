### **彙編語言**

```assembly
assume cs:codesg

codesg segment

start: mov ax,addr
	mov bx,addr
	add ax,bx
	
codesg ends
end
```



1. 彙編語言中分為彙編指令和偽指令

   彙編指令是對內存和CPU進行指示的指令，可以被翻譯成機器碼。如ADD,MOV

   偽指令只是決定程序的走向和邏輯結構，在編譯時就被執行，如START，ENDS

2. START ENDS

這兩個指令是成對出現的一對指令，標誌著一個**段**的開始和結束。

3. END

   END指令是彙編程序結束的標誌，遇到了END指令後程序執行完成。

4. ASSUME

   假設寄存器和程序中的一個段相關聯。如實例程序中使用assume來使得codesg與段寄存器相關聯。

#### **源程序**

1. 標號

   一個標號指代了一個地址。如實例程序中，codesg置於segment前面作為一個段的名字，這個名字最終會被編譯為一個段的段地址。

2. 程序返回

   一個程序在結束後，將CPU的控制權轉交給調用它的程序，稱為程序返回。

3. 可執行文件的程序裝入內存運行的原理

   