title: Python 中的 New-style 和 Old-style classes
date: 2013-4-6
category: python
tags: python
slug: class-in-python
author: tonychow
summary:

###使用 super() 的错误

super 函数是 Python 中的一个内置函数,提供对继承的类的函数调用,特别是在子类中被 overridden 的父类函数,比如 

    :::python
    __init__()

最近在使用 super 函数的时候出现了个错误,例如下:

    :::python
    >>> class Base:
    ...     def __init__(self):
    ...         self.num = 1
    ... 
    >>> class Next(Base):
    ...     def __init__(self):
    ...         super(Next, self).__init__()
    ... 
    >>> obj = Next()
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "<stdin>", line 3, in __init__
    TypeError: must be type, not classobj

可以看到抛出了参数类型错误的错误.一开始完全不知所措,然后将出错信息 google 了一下,找到了解决方式:

    :::python
    >>> class Base(object):
    ...     def __init__(self):
    ...         self.num = 1
    ... 
    >>> class Next(Base):
    ...     def __init__(self):
    ...         super(Next, self).__init__()
    ... 
    >>> obj = Next()
    >>> obj.num
    1
    >>> 

简单地将 Base 继承 object 就可以解决这个错误.其实这是 Python 中的 NewStyle classes 和 OldStyle classes 而导致的一个问题. super() 函数只适用于 NewStyle classes.

### Newstyle 和 Oldstyle

Python 中,直至 Python2.1 ,类和类型是两种不相关的概念,例如:

    :::python
    >>> class Test:
    ...     pass
    ... 
    >>> Test().__class__
    <class __main__.Test at 0xb77373ec>
    >>> type(Test())
    <type 'instance'>
    >>> type(type(Test()))
    <type 'type'>
    >>> 

在这里 Test 类是 Oldstyle 的类.可以看到,Test 类的一个实例,它的类是 Test,但是类型却是 instance.这是因为 Oldstyle 的类与类型是不统一的概念, Oldstyle 类的实例是独立于它们的类,由一个 Python 内置类型 instance 实现的.

从2.2开始, Python 开始使用 New-style 类来统一类和类型.对于一个 New-style 的类,它的实例的类型和类都是一致的.为了兼容之前的代码,在 Python2.2 之后,默认的类定义还是 Old-style 的类.而一个 New-style 的类可以通过继承一个 New-style 的类或者在类继承中最顶端继承 object 来实现,如下:

    :::python
    >>> class Test(object):
    ...     pass
    ... 
    >>> Test().__class__
    <class '__main__.Test'>
    >>> type(Test())
    <class '__main__.Test'>
    >>> type(type(Test()))
    <type 'type'>
    >>> 

New-style 类的提出是为了统一 Python的 对象模型.在 Python3 中,Old-style 类已经完全移除了.

参考资料:

- http://docs.python.org/2/library/functions.html#super
- http://docs.python.org/2/reference/datamodel.html#newstyle
- http://stackoverflow.com/questions/9698614/super-raises-typeerror-must-be-type-not-classobj-for-new-style-class
- http://stackoverflow.com/questions/9699591/instance-is-an-object-but-class-is-not-a-subclass-of-object-how-is-this-po/9699961#9699961
