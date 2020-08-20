---
author: lunar
date: Thu 20 Aug 2020 02:01:24 PM CST
---

### MATLAB数据导入

MATLAB通过`importdata`函数进行数据导入

该函数有多种使用方式
1. `A = importdata(filename)`
从文件`filename`中读取数据到数组A中
2. `A = importdata('-pastespecial')`
从剪切板读取数据
3. `A = importdata(filename, delimiterIn)`
解析`delimiterIn`作为在文件中的列分隔符
4. `A = importdata(filename, delimiterIn, headerlinesIn)`
从行头标题`headerlinesIn + 1`开始加载数字数据

#### 文件I/O

函数`importdata`其实是对于底层一些文件I/O的封装。MATLAB同样提供类似C语言的文件操作函数，如`fread, fwrite`等。

### MATLAB数据导出

MATLAB提供了几个数据导出的选项

- 来自数组的矩形，有分隔符的ASCII数据文件
- 日志文件的按键和结果文本输出
- 使用`fprintf`等低级函数的专用ASCII文件

#### 将数字数组导出为有分隔符的ASCII数据文件

- 使用`save`函数并指定`-ascii`限定符
`save my_data.out num_array -ascii`
- 使用`dlmwrite`函数
`dlmwrite('my_data.out', num_array, 'dlm_char')`


