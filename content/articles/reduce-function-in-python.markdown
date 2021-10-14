title: Python 内置函数 reduce
date: 2013-3-18
category: python
tags: python
slug: reduce-function-in-python
author: tonychow
summary: 

####原型

reduce 函数原型是 reduce(function, iterable[, initializer]),返回值是一个单值.使用例子如下:

    :::python
    >>> print reduce(lambda x, y: x + y, [1, 2, 3, 4, 5])
    15

可以看到通过传入一个函数和一个 list , reduce 函数返回的是这个 list 的元素的相加值.注意 lambda 函数是有两个参数的,如果我们改成一个参数会怎么样?如下:

    :::python
    >>> print reduce(lambda x: x, [1, 2, 3, 4, 5])
    Traceback (most recent call last):
    File "<stdin>", line 1, in <module>
    TypeError: <lambda>() takes exactly 1 argument (2 given)

结果是抛出了错误,提示 <lambda>() 函数只接受一个参数缺给了两个参数.所以在 reduce 内部中,我们可以知道对于作为参数的 function ,接受了两个值作为参数的.



####深入

第一个例子中, reduce 函数返回的是 list 变量元素的和,那 reduce 函数是如何实现将这个 list 变量元素相加起来呢?考虑到定义的匿名函数体中将 x 的值和 y 的值加起来了,所以应该和这个函数是相关的,那 reduce 函数给赋给这个 lambda 函数的两个参数分别是什么呢?

    :::python
    >>> l = []
    >>> def fun(x, y):
    ...     l.append((x, y))
    ...     return x + y
    ... 
    >>> result = reduce(fun, [1, 2, 3, 4, 5])
    >>> result
    15
    >>> l
    [(1, 2), (3, 3), (6, 4), (10, 5)]

通过这个例子,可以看出答案已经很明显了.在 reduce 函数内部,对 lambda 函数的调用一共有四次:

    :::python
    fun(1, 2)     #x = 1, y = 2,x 是列表的第一个元素,y是第二个元素
    fun(3, 3)     #x = 3, y = 3,x 是上一次调用返回值 1+2 , y 是第三个元素
    fun(6, 4)     #x = 6, y = 4,同上, y 是第四个元素
    fun(10, 5)    #x = 10, y = 5,同上, y 是第五个元素

最后得到 reduce 函数的返回值 15,也就是 fun 函数的第四次调用的返回值.所以现在我们知道了,reduce 函数对作为参数的函数是有要求的,要求这个函数接受两个参数.第一个参数的值是累积的值,而第二个参数的值是 reduce 函数参数中的序列的下一个元素.其实 reduce 函数中还有第三个可选的参数初始值,如果这个参数为空则初始值默认为序列的第一个元素,所以上面可以看到第一次调用这个函数是以序列的第一个和第二个元素作为参数的.最终,最后一次调用返回的值作为 reduce 函数的返回值.

#### 定义

reduce 函数可以参考下面的定义(来自官网):

    :::python
    def reduce(function, iterable, initializer=None):
        it = iter(iterable)
        if initializer is None:
            try:
                initializer = next(it)
            except StopIteration:
                raise TypeError('reduce() of empty sequence with no initial value')
        accum_value = initializer
        for x in it:
            accum_value = function(accum_value, x)
        return accum_value

reduce 函数对 function 的调用次数为 iterable 参数的长度n减1.
    
参考资料:

- [[1]官网: python build-in function reduce](http://docs.python.org/2/library/functions.html#reduce)
- [[2]Python 函数式编程: python functional programming](http://www.secnetix.de/olli/Python/lambda_functions.hawk)
