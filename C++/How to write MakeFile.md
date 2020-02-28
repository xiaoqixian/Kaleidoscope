### **How to write MakeFile**

1. 程序的編譯.

   程序在編譯過程中，編譯器只檢測程序語法，函數和變量是否被聲明。而函數是否被實現的檢測是在鏈接的過程中檢測的。
   
2. 一個makefile的示例：

   ```makefile
   edit : main.o kbd.o command.o display.o insert.o search.o files.o utils.o             cc -o edit main.o kbd.o command.o display.o insert.o search.o files.o utils.o 
    
       main.o : main.c defs.h             
       	cc -c main.c     
       kbd.o : kbd.c defs.h command.h             
       	cc -c kbd.c     
       command.o : command.c defs.h command.h         
       	cc -c command.c    
       display.o : display.c defs.h buffer.h           
       	cc -c display.c     
       insert.o : insert.c defs.h buffer.h           
       	cc -c insert.c     
       search.o : search.c defs.h buffer.h          
       	cc -c search.c     
       files.o : files.c defs.h buffer.h command.h       
       	cc -c files.c   
       utils.o : utils.c defs.h            
       	cc -c utils.c     
       clean :             
       	rm edit main.o kbd.o command.o display.o insert.o search.o files.o utils.o 
   ```

   從這個makefile的示例中我們可以看出makefile的工作原理。可以將其想象成一個棧，首先是要生成edit目標文件，於是就將這個edit壓入棧，然後edit要依賴後面的這些中間目標文件，就將中間的這些文件壓入棧，再去尋找中間目標文件的依賴文件，也就是.c文件和.h文件，將那些文件進行編譯，再逐漸鏈接。如果編譯和鏈接成功就可以成功生成目標文件，否則就執行clean命令，將這些中間目標文件和可執行文件全部刪除。其次，在定義了依賴關係後，後面的那一行定義了如何生成目標文件的shell命令，如```cc -c main.c```就表示用gcc編譯器的-c選項編譯```main.c```文件，-c可以只生成.o文件而不是可執行文件。

   **這個shell命令一定要以Tab鍵作為開頭**

3. 變量的使用

   當文件中需要加入新的文件時，常常有多處需要修改，非常麻煩。所以可以定義一個變量來表示所有的中間目標文件。如我們可以定義：

   ```makefile
   objects = main.o kbd.o command.o display.o insert.o search.o files.o utils.o 
   ```

   於是所有運用到這一群中間目標文件的地方都可以用objects變量代替。於是makefile可以修改為：

   ```makefile
   edit : $(objects)
   	cc -o edit $(objects)
    
       main.o : main.c defs.h             
       	cc -c main.c     
       kbd.o : kbd.c defs.h command.h             
       	cc -c kbd.c     
       command.o : command.c defs.h command.h         
       	cc -c command.c    
       display.o : display.c defs.h buffer.h           
       	cc -c display.c     
       insert.o : insert.c defs.h buffer.h           
       	cc -c insert.c     
       search.o : search.c defs.h buffer.h          
       	cc -c search.c     
       files.o : files.c defs.h buffer.h command.h       
       	cc -c files.c   
       utils.o : utils.c defs.h            
       	cc -c utils.c     
       clean :             
       	rm edit $(objects)
   ```

4. make自動推導

   GNU的make很強大，make會自動識別，並推導出命令。只要 make 看到一个[.o]文件，它就会自动的把[.c]文件加在依赖关系中，如果 make 找到一 个 whatever.o，那么 whatever.c就会是 whatever.o 的依赖文件。并且 cc -c whatever.c 也会 被推导出来。

   於是makefile的.o文件依賴關係又可以修改為：

   ```makefile
    main.o : defs.h     
    kbd.o : defs.h command.h     
    command.o : defs.h command.h    
    display.o : defs.h buffer.h     
    insert.o : defs.h buffer.h     
    search.o : defs.h buffer.h     
    files.o : defs.h buffer.h command.h     
    utils.o : defs.h 
    
    .PHONY : clean    
    clean : 
    	rm edit $(objects)
   ```

   ".PHONY"表示clean是一個偽目標文件。

5. 多個中間目標文件共享一個依賴文件

   在上面的makefile中，幾乎所有的.o文件都依賴的了def.h這個文件，每個.o文件都要寫一次對於def.h的依賴關係，因此看起來顯得非常的累贅。所以make可以使得多個.o文件共享一個.h文件，所以又可以寫成：

   ```makefile
   objects = main.o kbd.o command.o display.o insert.o search.o files.o utils.o
   
   edit: $(objects)
   	cc -o edit $(objects)
   	
   $(objects): def.h
   kbd.o command.o files.o: command.h
   display.o insert.o search.o files.o: buffer.h
   
   .PHONY: clean
   clean:
   	rm edit $(objects)
   ```

6. 引入其它makefile

   makefile中還可以通過include導入其它的Makefile，語法格式為：

   ```makefile
   include <filename>
   ```

   在 include 前面可以有一些空字符，但是绝不能是[Tab]键开始。同樣，include也可以通過$引用變量。也可以通過*符號+後綴名來通配特定後綴名的文件。

   make 命令开始时，会把找寻 include 所指出的其它 Makefile，并把其内容安置在当前的位置。 就好像 C/C++的#include 指令一样。如果文件都没有指定绝对路径或是相对路径的话，make 会在当前目录下首先寻找，如果当前目录下没有找到，那么，make 还会在下面的几个目录 下找：     

   ​	a. 如果 make 执行时，有“-I”或“--include-dir”参数，那么 make 就会在这个参数所 指定的目录下去寻找。     

   ​	b. 如果目录<prefix>/include（一般是：/usr/local/bin 或/usr/include）存在的话，make 也会去找。 

7. make通配

   在Makefile中定義變量，如果想要通配特定的後綴名的所有文件，並不是簡單的*+後綴名。Makefile中的變量相當於C/C++中的宏，想要通配符在變量中展開，需要寫為：

   ```makefile
   objects := $(wildcard *.o)
   ```

   wildcard是一個關鍵字，指出*通配符需要展開。

8. 文件搜尋

   make中需要指定特定的路徑make才知道去哪裡查找，否則make只會在當前目錄下查找。

   make下可以指定特殊變量"VPATH"來完成這個功能。

   ```makefile
   VPATH = src:../headers
   ```

   **不同的目錄之間通過冒號分割**。但當前目錄還是最優先搜索的地方。

   另一個設置搜索路徑的方法是通過make的"vpath"關鍵字，其使用方法有3種：

   * ```vpath <pattern> <directories>```

     為符合模式pattern的文件指定搜索目錄directories

   * ```vpath <pattern>```

     清除符合模式pattern的文件的搜索目錄

   * ```vpath```

     清除所有已經設置好了的文件搜索目錄。

   pattern中通過%來匹配字符，如```%.h```可以匹配所有.h文件。我们可以连续地使用 vpath 语句，以指定不同搜索策略。如果连续的 vpath 语句中出现了相 同的pattern，或是被重复了的pattern，那么，make 会按照 vpath 语句的先后顺序来执行搜索。

9. 偽目標

   在編譯過程中生成了很多編譯文件，應該提供一個清除它們的"目標"以備完整地重編譯使用。

   对于Makefile中建立的目标文件，可以通过make target命令来执行这个目标文件。偽目標同樣可以利用這一點，如果想要清楚中間文件。就可以設置一個clean的偽目標，clean可以不依賴任何文件，但可以設置shell要執行的命令，就像這樣：

   ```makefile
   .PHONY:clean
   clean:
   	rm *.o temp
   ```

   如果需要生產多個目標文件，但是又不想一個個命令的執行，可以設置一個all的偽目標。偽目標依賴於所有需要生成的目標文件。這樣就可以一次性生成所有目標文件了。

   ```makefile
   all:tar1 tar2 tar3
   .PHONY:all
   
   tar1:tar1.o
   	command
   ...
   ```

   通過make all便可以生成所有目標文件了。

   同樣，偽目標也可以作為第一個目標的依賴項，這樣就可以先一步生成，類似於一個子程序。
   
10. 多目標

11. 靜態模式

    ```makefile
    <targets>:<target-pattern>:<prerequsts-patterns ..>
    	<commands>
    ```

    targets定義了一系列的目標文件，可以有通配符。是目標的一個集合

    target-pattern 是指明了 targets 的模式，也就是的目标集模式。 

    prerequests-parrterns 是目标的依赖模式，它对 target-pattern 形成的模式再进行一次依赖目标 的定义。 

---

#### **書寫命令**

1. 顯示命令

   make會把其要執行的命令在命令執行前輸出到屏幕上，如果想要命令的名字不被顯示，可以在其前面加上@符號，如：

   ```@echo 正在編譯XXX模塊```,就不會輸出```echo 正在編譯XXX模塊```，而是```正在編譯XXX模塊```

   如果make加上-n參數或者```--just-print```，就會只輸出這些命令而不執行。

   而-s參數則是全面禁止命令的顯示。

2. 命令執行

   如果想要想要上一條命令作用在下一條命令上，如cd命令作用在pwd命令上，就不能將兩條命令寫在兩行，而是寫在一行用分號隔開。

3. 命令出錯

   有時候命令出錯會導致make終止執行該規則，但並不是所有的錯誤都會影響項目的執行。因此可以選擇性地在一些命令前加上```-```符號表示不管命令是否出錯都認為是成功的。

4. 嵌套執行make

   不將所有的Makefile寫在一個文件中更便於維護，可以通過一個總控Makefile來控制其它的Makefile，總控Makefile可寫為：

   ```makefile
   subsystem:
   	cd subdir && $(MAKE)
   ```

   ，总控 Makefile 的变量可以传递到下级的 Makefile 中（如果你显示的声明），但是不会覆盖下层的 Makefile 中所定义的变量，除非指定了“-e” 参数。 

   聲明傳遞變量的方式為：

   ```makefile
   export variable = value
   ```

   如果不想傳入變量，則運用unexport命令。

---

#### **使用變量**

1. 變量基礎

   在 Makefile 中的定义的变量，就像是 C/C++语言中的宏一样，他代表了一个文本字串，在 Makefile 中执行的时候其会自动原模原样地展开在所使用的地方。其与 C/C++所不同的是， 你可以在 Makefile 中改变其值。

   在使用變量時，可以通過$()的方式來使用。

2. 變量定義

   * '='定義變量：可以直接定義變量和引用後面定義的變量

   * ':='定義變量：這種也可以直接定義變量，但是只能引用前面已經定義了的變量。 

   * 定義空格：

     ```makefile
     nullstring := 
     space := $(nullstring)#end of the line
     ```

     所以#可以表示一個變量定義的終止，但是這樣就使得所有的注釋都必須緊貼在變量定義的後面才會使變量定義時不包含空格。

   * '?='定義變量：如果左邊的變量名沒有被定義過，則什麼也不做，否則就執行定義。這樣可以防止覆蓋之前的定義。

3. 變量高級用法

   * 變量值的替換：格式為```$(var:a=b)```。

     這個可以將變量中的以"a"字串“结尾”的“a”替换成“b”字串。这里的“结尾”意思 是“空格”或是“结束符”。 

     示例：

     ```makefile
     foo := a.o b.o c.o
     bar := $(foo:.o=.c)
     ```

     這樣就可以方便的將所有.o文件替換為.c文件

   * 把變量的值當成變量，這樣在引用時就嵌套多個$()。如：

     ```makefile
     x = y
     y = z
     a := $($(x)) #則a的值為z
     ```

     複雜一點的可以引用函數

     ```makefile
     x = var1
     var2 := hello
     y = $(subst 1,2,$(x))#subst函數可以將x的值中的1替換為2 
     z = y
     a := $($(z)) #a的值為hello
     ```

     還可以通過多個變量來組成一個變量

     ```makefile
     hello_world = hello
     a = hello
     b = world
     all = $($a_$b) #all的值為hello。
     ```

4. 追加變量值

   我們可以用"+="操作符給變量追加值，如：
   
   ```makefile
   objects = main.o file.o
   objects += another.o
   ```
   
   如果變量之前沒有定義過，那麼“+=”就會變成“=”。
   
5. override指示符

   如果在命令行定義了一個和make裡面相同的變量，那麼原來Makefile中定義的變量的值會被覆蓋。如果不想被覆蓋，那麼就可以通過override指示符來指定。語法格式為：

   ```override <variable> = <value>```

   ```override <variable> := <value>```

6. 多行變量

   使用```define```關鍵字可以定義多行變量，使用define定義變量的值可以有換行。define 指示符后面跟的是变量的名字，而重起一行定义变量的值，定义是以 endef 关键字结束。**因為所有命令都需要以[Tab]鍵作為開頭，所以在define中定義的命令要想被認成命令也要以[Tab]鍵開頭。**

   此外，在變量定義完後，要以endef結尾。
   
7. 環境變量

   make 运行时的系统环境变量可以在 make 开始运行时被载入到 Makefile 文件中，但是如果 Makefile 中已定义了这个变量，或是这个变量由 make 命令行带入，那么系统的环境变量的 值将被覆盖。（如果 make 指定了“-e”参数，那么，系统环境变量将覆盖 Makefile 中定义的 变量） 。

   環境變量會使得所有的Makefile都受到影響，一般不建議使用。

8. 目標變量

   之前講的所有變量都是全局變量，在任何地方都可以訪問到。我們同樣可以为某个目标设置局部变量，这种变量被称为“Target-specific Variable”， 它可以和“全局变量”同名，因为它的作用范围只在这条规则以及连带规则中，所以其值也 只在作用范围内有效。而不会影响规则链以外的全局变量的值。 

   語法格式為：```<target>:<variable-assignment>```或```<pattern>:override <variable-assigment>```

   示例：

   ```makefile
   prog:CFLAGS = -g
   prog:prog.o foo.o brog.o
   	$(CC) $(CFLAGS) prog.o foo.o bar.o
   prog.o : prog.c             
    	$(CC) $(CFLAGS) prog.c     
   foo.o : foo.c             
   	$(CC) $(CFLAGS) foo.c     
   bar.o : bar.c             
   	$(CC) $(CFLAGS) bar.c 
   ```

   在这个示例中，不管全局的CFLAGS的值是什么，在 prog 目标，以及其所引发的所有规 则中（prog.o foo.o bar.o 的规则），$(CFLAGS)的值都是“-g” 

9. 模式變量

   在 GNU 的 make 中，还支持模式变量（Pattern-specific Variable）。模式变量的好处就是，我们可以给定一种“模式”， 可以把变量定义在符合这种模式的所有目标上。

   語法格式：```<pattern>:<variable-assigment>```或```<pattern>:override <variable-assigment>```

   示例：

   ```%.o:CFLAGS = -o```

---

#### **條件判斷**

1. 語法

   ```makefile
    <conditional-directive>     
    <text-if-true>     
    else     
    <text-if-false>     
    endif 
   ```

   ```<conditional-directive>```表示條件關鍵字，總共有4個。

   * ifeq

     ifeq(<arg1>,<arg2>):比較兩個參數arg1和arg2是否相同。

     也可以使用make的函數

   * ifneq

     ifneq(<arg1>,<arg2>):比較兩個參數arg1和arg2是否不相同。

   * ifdef:判斷一個變量是否非空

   * ifndef

   **特别注意的是，make 是在读取 Makefile 时就计算条件表达式的值，并根据条件表达式的值 来选择语句，所以，你好不要把自动化变量（如“$@”等）放入条件表达式中，因为自 动化变量是在运行时才有的。**

---

#### **函數**

1. 調用的語法

   ```$(<function> <arguments>)```或```${<function> <arguments>} ```

   arguments是函数的参数，参数间 以逗号“,”分隔，而函数名和参数之间以“空格”分隔。函數的參數也可以通過$來引用變量。

2. 常見字符串處理函數

   * ```$(subst <from>,<to>,<text>)```

     功能：將text中的from字符串替換為to字符串。

   * ```$(patsubst <pattern>,<replacement>,<text>)```

     功能：查找<text>中的单词（单词以“空格”、“Tab”或“回车”“换行”分隔）是否符 合模式<pattern>，如果匹配的话，则以<replacement>替换。这里，<pattern>可以包括通配符 “%”，表示任意长度的字串。如果<replacement>中也包含“%”，那么，<replacement>中的 这个“%”将是<pattern>中的那个“%”所代表的字串。（可以用“\”来转义，以“\%”来 表示真实含义的“%”字符） 

     示例：

     ```$(patsubst %.c,%.o,x.c.c bar.c)```,於是返回結果為"x.c.o bar.o"

     這個函數和之前變量定義中有相似的部分，```$(x.c.c bar.c:%.c = %.o)```與這個有異曲同工之妙。

   * ```$(strip <string>)```:去掉string中開頭和結尾的空格

   * ```$(findstring <find>,<in>)```:查找字符串函數，在in字符串中找到find。如果找到則返回find，否則返回空字符串。

   * ```$(filter <pattern>,<text>)```:過濾到不符合pattern的單詞，只保留符合的

   * ```$(filter-out <pattern>,<text>)```:反過濾函數，過濾到符合pattern的，只保留不符合的。

   * ```$(sort <list>)```

   * ```$(word <n>,<text>)```:取text的第n個單詞

   * ```$(wordlist <s>,<e>,<text>)```:返回從text中從<s>到<e>的字符串，<s>和<e>都是數字。**如果<s>比<text>中的单词数要大， 那么返回空字符串。如果<e>大于<text>的单词数，那么返回从<s>开始，到<text>结束的单 词串。 **

   * ```$(words <text>)```:同濟text中的單詞個數

3. 文件名操作函數

   * ```$(dir <names..>)```:取目錄函數，目錄是是指后一个反斜杠（“/”）之 前的部分。如果没有反斜杠，那么返回“./”。 
   * ```$(notdir <names..>)```:取非目錄部分函數。
   * ```$(suffix <names..>)```:取後綴函數
   * ```$(basename <names..>)```:取前綴函數
   * ```$(addsuffix <suffix>,<names..>)```:顧名思義
   * ```$(addpreffix <suffix>,<names..>)```
   * ```$(join <list1>,<list2>)```:把<list2>中的单词对应地加到<list1>的单词后面。如果<list1>的单词个数要比 <list2>的多，那么，<list1>中的多出来的单词将保持原样。如果<list2>的单词个数要比<list1> 多，那么，<list2>多出来的单词将被复制到<list2>中。 

4. foreach函數

   foreach函數用於循環，語法格式為：```$(foreach <var>,<list>,<text>)```

   这个函数的意思是，把参数<list>中的单词逐一取出放到参数<var>所指定的变量中，然后再 执行<text>所包含的表达式。每一次<text>会返回一个字符串，循环过程中，<text>的所返回 的每个字符串会以空格分隔，后当整个循环结束时，<text>所返回的每个字符串所组成的 整个字符串（以空格分隔）将会是 foreach 函数的返回值。 

   示例：

   ```makefile
   names = a b c
   names_o = $(foreach n,names,$(n).o)
   #names_o的值便為a.o b.o c.o
   ```

5. if函數

   if函數與if條件句類似，語法為：

   ```$(if <condition>,<then-part>)```或```$(if <condition>,<then-part>,<else-part>)```

6. call函數

   call 函数是唯一一个可以用来创建新的参数化的函数。語法格式為：

   ```$(call <expression>,<parm1>,<parm2>,<parm3>...) ```

   当make执行这个函数时，<expression>参数中的变量，如$(1)，$(2)，$(3)等，会被参数<parm1>， <parm2>，<parm3>依次取代。而<expression>的返回值就是 call 函数的返回值。

   示例：

   ```makefile
   reverse = $(1) $(2)
   foo = $(call reverse,a,b)
   #foo的值便為a b
   ```

   參數的次序也可以變化。

7. origin函數

   origin函數負責告訴你變量是哪裡來的，語法為```$(origin <variable>)```

   這個函數返回的信息如下：

   * “undefined”       如果<variable>从来没有定义过，origin 函数返回这个值“undefined”。 

   * “default”       如果<variable>是一个默认的定义，比如“CC”这个变量，这种变量我们将在后面讲 述。 

   * “environment”       如果<variable>是一个环境变量，并且当 Makefile 被执行时，“-e”参数没有被打开。

   * “file”       如果<variable>这个变量被定义在 Makefile 中。 

   * “command line”       如果<variable>这个变量是被命令行定义的。 

   * “override”       如果<variable>是被 override 指示符重新定义的。 

   * “automatic”       如果<variable>是一个命令运行中的自动化变量。关于自动化变量将在后面讲述。 

8. shell函數

   shell函數的參數是操作系統的shell命令，和反引號"`"有相同的功能。也就是說shell函數可以執行操作系統命令後將輸出作為函數返回值。

9. error函數

   產生一段錯誤信息，並退出make。語法格式為：```$(error <text>)```

---

#### **make的運行**

1. make的退出碼

   make 命令执行后有三个退出码： 

   * 0 —— 表示成功执行。     

   * 1 —— 如果 make 运行时出现任何错误，其返回 1。     

   * 2 —— 如果你使用了 make 的“-q”选项，并且 make 使得一些目标不需要更新，那么 返回 2。

2. 指定Makefile

   如果不想你的Makefile只能被命名為"GNUmakefile"、"makefile"或"Makefile"中的一個(如果不指定Makefile，只輸入make就是在這三個中尋找)，可以通過-f參數指定一個文件作為讀取的Makefile。

3. 指定目標

   一般make的最終目標就是Makefile中的第一個目標。但是也可以通過```make 目標名字```的方式來指定目標。

   有一個make的環境變量叫"MAKECMDGOALS"，這個變量會存放你指定的終極目標的列表。示例用法：

   ```makefile
    sources = foo.c bar.c     
    ifneq ( $(MAKECMDGOALS),clean)     
    include $(sources:.c=.d)     
    endif 
   ```

   在Makefile中我們可以通過設立各種偽目標來完成不同的功能，一般在Makefile中都包含了編譯、安裝、打包等功能。

   * “all”         这个伪目标是所有目标的目标，其功能一般是编译所有的目标。      
   * “clean”         这个伪目标功能是删除所有被 make 创建的文件。      
   * “install”         这个伪目标功能是安装已编译好的程序，其实就是把目标执行文件拷贝到指定的目 标中去。      
   * “print”         这个伪目标的功能是例出改变过的源文件。      
   * “tar”         这个伪目标功能是把源程序打包备份。也就是一个 tar 文件。      
   * “dist”         这个伪目标功能是创建一个压缩文件，一般是把 tar 文件压成 Z 文件。或是 gz 文 件。      
   * “TAGS”         这个伪目标功能是更新所有的目标，以备完整地重编译使用。      
   * “check”和“test”         这两个伪目标一般用来测试 makefile 的流程。 

4. 檢查規則

   有時候只想檢查一下命令，而不像Makefile執行起來。可以用下列參數：

   * ["-n","--just-print","--dry-run","--recon"]：不执行参数，这些参数只是打印命令，不管目标是否更新，把规则和连带规则下的命令 打印出来，但不执行，这些参数对于我们调试 makefile 很有用处。 
   * ["-t","-touch"]：將目標文件的時間更新，但不更改目標文件。
   * ["-q","-question"]： 这个参数的行为是找目标的意思，也就是说，如果目标存在，那么其什么也不会输出， 当然也不会执行编译，如果目标不存在，其会打印出一条出错信息。 

5. make的參數

   自己參詢吧

---

#### **隱含規則**

Makefile有一些規則並不需要寫出來make就可以自動推導出來，稱為隱藏規則。比如自動利用gcc編譯器將.c文件編譯為.o文件。

**事先聲明所有隱藏規則都可以通過"-r"參數禁止使用**。

1. 常用隱藏規則：

   * c程序編譯的隱藏規則

     “<n>.o”的目标的依赖目标会自动推导为“<n>.c”，并且其生成命令是“\$(CC) –c ​\$(CPPFLAGS) $(CFLAGS)” 。

   * c++程序編譯的隱藏規則

     “<n>.o”的目标的依赖目标会自动推导为“<n>.cc”或是“<n>.C”，并且其生成命令是“\$(CXX) –c \$(CPPFLAGS) $(CFLAGS)”。（建议使用“.cc”作为 C++源文件的后缀，而不是“.C”） 

   * Pascal、Fortran和彙編之類的語言的隱藏規則暫時不寫

   * 鏈接object文件的隱藏規則

     “\<n>”目标依赖于“\<n>.o”，通过运行 C 的编译器来运行链接程序生成（一般是“ld”）， 其生成命令是：“\$(CC) \$(LDFLAGS) \<n>.o \$(LOADLIBES) $(LDLIBS)”。这个规则对于只有 一个源文件的工程有效，同时也对多个 Object 文件（由不同的源文件生成）的也有效。

2. 隱藏規則所使用的變量

   隱藏規則中一般使用了預先設置的變量，自己可以在Makefile中修改這些變量的值。但是要想不被修改，可以添加"-R"參數。

   命令的變量：

   * CC:C語言編譯程序。默認命令是"cc"
   * CXX:C++語言編譯程序。默認命令是"g++"
   * AS:彙編語言編譯程序。默認命令是"as"
   * AR:函數庫打包程序。默認命令是"ar"

   還有一些命令參數的變量：

   * ARFLAGS:函數庫打包程序AR命令的參數。默認值為"rv"
   * ASFLAGS:彙編語言編譯器參數。
   * CFLAGS:c編譯器參數
   * CXXFLAGS:cpp編譯器參數
   * CPPFLAGS:c預處理器參數