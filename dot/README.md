---
author: lunar
date: Sat 08 Aug 2020 06:42:02 PM CST
---

### Linux dot command

Graphviz （Graph Visualization Software的缩写）是一个由AT&T实验室启动的开源工具包，用于绘制DOT语言脚本描述的图形。它也提供了供其它软件使用的库。Graphviz是一个自由软件，其授权为Common Public License。其Mac版本曾经获得2004年的苹果设计奖。

Graphviz包括很多命令行工具，dot命令是一个用来将生成的图形转换成多种输出格式的命令行工具，其输出格式包括PostScript，PDF，SVG，PNG，含注解的文本等等。neato命令用于spring model的生成（在Mac OS版本中称为energy minimized）。twopi命令用于放射状图形的生成。circo命令用于圆形图形的生成。fdp命令另一个用于生成无向图的工具。dotty命令一个用于可视化与修改图形的图形用户界面程序。lefty命令是一个可编程的(使用一种被EZ影响的语言[4])控件，它可以显示DOT图形，并允许用户用鼠标在图上执行操作。Lefty可以作为MVC模型的使用图形的GUI程序中的视图部分。 

DOT语言是一种文本图形描述语言。它提供了一种简单的描述图形的方法，并且可以为人类和计算机程序所理解。DOT语言文件通常是具有.gv或是.dot的文件扩展名。本文将主要介绍从源代码安装Graphviz工具以及dot命令的使用方式。


