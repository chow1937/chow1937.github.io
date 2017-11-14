title: Python 核心编程读书笔记 Day4
date: 2014-07-15
category: readings
tags: corepython, reading-notes, python
slug: corepython-reading-notes-how-day4
author: tonychow
summary:

今天的主要阅读了 10-12 章的内容，这三章内容主要涉及异常，函数及模块，这几个模块
也是 Python 中比较重要的基本内容，也有相对于其他语言的独特之处，下面继续总结今
天的阅读笔记。

### 第十章：错误和异常

本章关注的内容是异常。异常在其他语言中也有实现，一般来说，异常处理给程序员提供
了一种在错误发生的时候对错误进行处理的方式。与其出现错误的时候，直接终止程序的
执行，不如对错误进行处理之后让程序继续执行。下面是本章要点：

1.错误引发异常的时候会打断正常的程序处理流程；

2.Python 异常的检测可以通过 try 语句进行，通常有 try-excetpt，try-finally模式；

3.try 语句可以带多个 except ，可以处理多种异常，也可以直接多个异常放在一个元组
中；

4.except Exception[, reason]；

5.try-except 同样也支持 else 子句，不发生异常则执行 else 子句的语句；

6.实现了 `__enter_` 和 `__exit__` 方法的类可以利用 with 语句；

7.`__exit__` 具有三个参数，exc_type， exc_value， exc_traceback；

<!--more-->

### 第十一章：函数和函数式编程

函数在 Python 中其实也是一个对象，保存了函数的相关内容，所以在 Python 中，函
数也和普通的对象一样，可以传给一个函数，也可以作为函数的返回值返回，因此也导
至了 Python 支持一部分函数式编程的特性。以下是要点：

1.Python 中的函数即使没有 return 语句，也会默认返回值为 None；

2.Python 中支持默认参数，但是非默认参数需要在默认参数前；

3.Python 中函数支持将参数放进元组或者字典中；

4.`func(*args)` 的形式是将参数放到元组中；

5.`func(**kwargs)` 的形式是将参数放到字典中，表示的是应对参数名及其值；

6.Python 支持在函数内部定义函数，并且内部函数可以调用包含函数的局部变量；

7.函数内部是一个局部空间；

8.装饰器函数接受一个函数返回另外一个装饰后的函数；

9.装饰器利用 `@` 来装饰函数，相当于：`foo = deco(foo)`；
