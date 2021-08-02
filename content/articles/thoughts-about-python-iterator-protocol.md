title: 关于 Python iterator 协议的一点思考
date: 2015-04-06
category: python
tags: python, iterator, thoughts
slug: thoughts-about-python-iterator
author: tonychow
summary: 

Python 中有好几种容器或者序列类型：`list` `tuple` `dict` `set` `str`，对于这些类型中的内容，往往需要一种方式去遍历获取它们来进行操作。所以 Python 提供了迭代器的类型来对这些类型的内容进行迭代遍历，迭代类型新增于 Python 2.2。

 迭代器类型指的是遵循迭代器协议的类型，对于 Python2.x 版本来说就是实现了 `__iter__` 和 `next` 函数的对象类型。如果一个对象实现了迭代器协议，则可以用 `for` 语句遍历这个对象的内容。其中 `__iter__` 函数返回一个迭代器对象，而 `next` 函数则需要返回容器的下一个内容，如果没有下一个则抛出 StopIteration 异常，这个异常在 `for ... in` 语句中将会被捕获然后结束迭代。迭代器协议详细内容可以查看 [PEP234](https://www.python.org/dev/peps/pep-0234/) 。Python3.x 将 `next` 函数改成了 `__next__` 函数，以和其他内置的函数保持一致的双下划线风格。

以前看迭代器协议的时候，经常可以看到这样一个实现：

    :::python
    class Reverse(object):

        def __init__(self, data):
            self.data = data
            self.index = len(data)

        def __iter__(self):
            return self
            
        def next(self):
            if self.index == 0:
                raise StopIteration
            self.index -= 1
            return self.data[self.index]

最近看到了这么一个写法：

    :::python
    class IterObj(object):

        def __init__(self, data):
            self.data = data

        def __iter__(self):
            return iter(self.data)

这个写法没有 `next` 函数了，初看起来好像没有完全实现迭代器协议的样子，但是仔细考虑下的话，`__iter__` 函数内部调用了内置函数 `iter` ，实际上是返回了一个迭代器对象，而这个迭代器对象当然是实现了迭代器协议的。所以第二种写法也是完全可以的，并且对比第一种写法来说更加简单。

在官方文档 [迭代器类型](https://docs.python.org/2/library/stdtypes.html?highlight=iterator#iterator-types) 中可以看到，对于 `list` `dict` 等容器对象来说，它们的 `__iter__` 函数返回的不是其自身，而是一个迭代器对象： `container.__iter__()` 。所以当一个容器对象需要提供迭代的功能的时候，不是把这个容器对象变成一个迭代器对象，而是返回一个迭代器对象，将迭代的功能委托给这个迭代器对象。所以上面两种写法的区别在于一个是实现了迭代器对象，一个是实现了可迭代的容器对象。所以第二种写法如果稍稍微修改下：

    :::python
    class IterObj(object):

        def __init__(self, data):
            self.data = data

        def __iter__(self):
            return Reverse(self.data)

这样就利用了之前定义的迭代器对象 `Reverse` 来给对象 `IterObj` 提供了反向迭代的功能。可以看到，这样的处理方式将迭代的逻辑和容器对象分离了，更加的灵活，容器对象本身也更加精简。

Python 的迭代器协议统一了  Python 中容器对象进行迭代的方式，另一方面来说，也为用户自定义类型添加迭代的功能添加了方便的实现方式，所以无论是从语言的标准化来说还是从用户使用角度的来说都是非常有用的一个协议。
