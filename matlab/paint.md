---
author: lunar
date: Thu 20 Aug 2020 02:33:48 PM CST
---

### MATLAB绘图

#### `plot`函数绘制函数图

MATLAB使用`plot`函数来绘制函数曲线

`plot`函数需要指定横轴点和纵轴点。一般纵轴的点是横轴的点某个映射，所以大小相同。

**在图上添加标题，标签，网格线和缩放**

#### `bar`函数绘制条形图

直接给示例代码：

```matlab
x = [1:10];
y = [75, 58, 90, 87, 50, 85, 92, 75, 60, 95];
bar(x,y), xlabel('Student'),ylabel('Score'),
title('First Sem:')
print -deps graph.eps
%原文出自【易百教程】，商业转载请联系作者获得授权，非商业请保留原文链接：https://www.yiibai.com/matlab/matlab_graphics.html#article-start
```

#### `contour`函数绘制等高线

绘制等高线首先需要明确一个网格，通过`meshgrid`函数给出

`[x,y] = meshgrid(-5:0.1:5, -3:0.1:3);`

其次需要明确一个双自变量的函数，

`g = x.^2 + y.^2;`

将三个参数输入到`contour`函数中

```matlab
contour(x,y,g)
pring -deps graph.eps
```

#### `surf`函数画三维图

与画等高线过程相似，只不过将`contour`函数改为`surf`函数


