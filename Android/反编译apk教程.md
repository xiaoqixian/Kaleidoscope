### 反编译apk教程

来源：[菜鸟教程][https://www.runoob.com/w3cnote/android-tutorial-decompile-apk-get-code-resources.html]

[反编译工具][http://static.runoob.com/download/%E5%8F%8D%E7%BC%96%E8%AF%91%E7%9B%B8%E5%85%B3%E7%9A%84%E4%B8%89%E4%B8%AA%E5%B7%A5%E5%85%B7.zip]

教程(以shadowsocks.apk为例):

1. 进入命令行，cd命令进入工具的存储路径
2. 键入``` apktool.bat d shadowsocks.apk ```
3. apk解压后会得到classes.dex文件，复制到des2jar.bat所在的目录下。键入``` d2j-dex2jar.bat classes.dex ```,这样就可以得到一个jar包。
4. 打开jd-gui.exe,在里面打开得到的jar包即可得到源码。