title: Python 核心编程读书笔记 Day3
date: 2014-07-13
category: readings
tags: corepython, reading-notes, python
slug: corepython-reading-notes-how-day3
author: tonychow
summary: 

今天阅读的章节是 8 和 9 章，前面的章节已经介绍了 Python 的基本的数据类型，这两章分别介绍了 Python 的条件
循环语句和文件类型。

### 第八章：条件和循环

这章主要就是介绍 Python 中的条件和循环语句，Python 中的条件语句有 if-else，而循环则有 while 和 for。要点：

1.if 语句有 if-else 和 if-elif-elif-else 模式；

2.Python 中也存在条件表达式，和其他语言的不同，是利用 if 实现的：X if C else Y；

3.Python 中的 while 和其他语言的类似，而 for 循环则不一样，for 循环可以遍历可迭代对象；

4.在遍历迭代器的时候，for 循环会调用迭代器的 next 方法，并且在遇到 StopIteration 异常结束遍历；

5.range(start, stop, step=1) 函数可以生成一个列表；

6.sorted 和 zip 函数返回一个列表，而 reversed 和 enumerate 函数则返回一个迭代器；

7.else 同样可以用在 while 和 for 循环语句中，在循环结束后执行，break 则会跳出这个 else；

8.迭代器对象需要实现 next 和 `__iter__` 方法；

9.列表解释：[expr for iter_var in iterable]，返回列表；

10.生成器表达式：(expr for iter_var in iterable)；

<!--more-->

### 第九章：文件和输入输出

本章主要关注 Python 中的文件对象及输入和输出方面，下面是要点：

1.文件只是连续的字节序列；

2.可以用 open 或者 file 函数打开或者创建文件，这两个函数类似；

3.文件对象的 readlines 方法将会将该文件所有行都加载到内存中，打开大文件不太友好；

4.xreadlines 是以迭代的方式每次读取文件的一行，不过现在可以直接对文件对象进行迭代达到一样的效果；

5.readline 函数不会去除读取到的行的换行符，writelines 也不会自动添加换行符；
