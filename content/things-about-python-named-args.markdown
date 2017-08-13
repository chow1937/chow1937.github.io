title: Python 函数的命名参数相关
date: 2013-5-15
category: python
tags: python
slug: things-about-python-named-args
author: tonychow
summary: 

### 起因

今天师弟问了一个关于 Python 函数参数的一个问题：

    :::python
    #1
    def func(x, l=[]):
        pass

    #2
    def func(x, l=None):
        if l is None:
            l = []

> 为啥第一个函数会把 l 每次调用完的值保留下来？

起初我认为问的是这两个函数使用的时候，为何会保持对传入的参数 l 的修改。从这个方面来讲，是因为 Python 对于数据赋值的处理的原因。

<!--more-->

在 Python 中，赋值是传引用的。一个列表，比如 [1, 2, 3]，或者一个字符串，'tonychow'，这些对象在创建的时候会在内存中分配一段空间。如果将这些对象赋值给一个变量名，那就会导致在 Python 的命名空间中该变量名指向内存中这个对象。对该变量名的操作就是对内存中这个对象的操作。所以如果尝试直接将一个变量 a 赋值给另外一个变量 b ，导致的后果是，命名空间中，这两个变量名 a 和 b 指向内存中同样一个对象，也就是所谓传引用赋值。对其中任意一个变量的操作，实质是对该对象进行操作，所以同样的操作后结果也会可以在另外一个变量中看到。如下：

    :::shell
    >>> a = [1, 2, 3]
    >>> b = a
    >>> a.pop()
    3
    >>> b
    [1, 2]
    >>> a
    [1, 2]
    >>> 

从上面的代码可以看到，在将 a 赋值给 b 之后，对 a 列表调用 pop 方法，导致的是 b 列表也发生了变化。我们还可以通过 Python 内置的 globals 函数和 id 函数来加深这个理解。globals 函数将会返回一个字典，这个字典是当前的全局符号表。而 id 函数则会返回一个对象的标识，可以将其返回值看作是这个对象在内存中的地址。

    :::python
    >>> globals()
    {'a': [1, 2], 'b': [1, 2],
    '__builtins__': <module '__builtin__' (built-in)>,
    'value': None, '__package__': None, 
    'key': '__doc__', '__name__': '__main__', '__doc__': None}
    >>> id(a)
    3077280588L
    >>> id(b)
    3077280588L
    >>> 

可以看到，a 和 b 都在当前的全局字符表中，他们的值也都是一致的。此外，id 函数的结果明确地说明了 a 和 b 这两个变量名都是指向了内存中的同一个对象。而在 Python 中，调用函数的时候，传入参数，也是进行传引用的赋值。所以我师弟说的这两个函数都会保留对于传入参数的修改，也就是：

    :::python
    >>> def func(l=None):
    ...     if l is None:
    ...         l = []
    ...     l.append(1)
    ... 
    >>> bar = [2]
    >>> bar
    [2]
    >>> func(bar)
    >>> func(bar)
    >>> bar
    [2, 1, 1]
    >>> 

题外话，在 Python 内置的数据类型中，有两种不同的数据类型。一种是可变类型(mutable)，比如 list ， dict 等;另外一种就是不可变类型(immutable)，比如字符串或者 tuple。

可是后来师弟贴出了另外一段代码：

    :::python
    >>> def func2(items=None):
    ...     if items == None:
    ...         items = []
    ...     items.append(1)
    ...     return items
    ... 
    >>> func2()
    [1]
    >>> func2()
    [1]
    >>> 

这下我明白了，师弟说的不是我想到的那个问题，而是命名参数的问题。

### 解决

说实话这个问题一开始我也没有想到答案。大家在学习 Python 的时候，无论看的是哪本入门书，应该在开始的时候都会看到一句话“ Python 中一切都是对象”。看代码：

    :::python
    >>> isinstance(1, int)
    True
    >>> isinstance('test', str)
    True
    >>> def func():
    ...     pass
    ... 
    >>> type(func)
    <type 'function'>
    >>> dir(func)
    ['__call__', '__class__', '__closure__', '__code__', '__defaults__',
    '__delattr__', '__dict__', '__doc__', '__format__', '__get__', 
    '__getattribute__', '__globals__', '__hash__', '__init__', 
    '__module__', '__name__', '__new__', '__reduce__', '__reduce_ex__',
    '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__',
    'func_closure', 'func_code', 'func_defaults', 'func_dict', 'func_doc',
    'func_globals', 'func_name']
    >>> func.__code__
    <code object func at 0xb76c8410, file "<stdin>", line 1>
    >>> func.__name__
    'func'
    >>> 

对的，数字1是一个对象，字符串 'test' 也是一个对象，甚至一个函数也是一个类型为 function 的对象，也有一堆的属性和方法。对于 function 对象而言，有一个特殊属性 __defaults__ ，这个属性用一个元组保存了是这个 function 对象的命名参数的缺省值，如下：

    :::python
    >>> def func(a=1, b=2):
    ...     pass
    ...
    >>> func.__defaults__
    (1, 2)
    >>> def foo(a, b):
    ...     pass
    ...
    >>> foo.__defaults__ is None
    True
    >>> def func_no():
    ...     pass
    ...
    >>> func_no.__defaults__ is None
    True
    >>>
    
如果一个函数有命名参数，则按顺序保存了命名参数的缺省值。如果这个函数命名参数没有缺省值或者没有命名参数，则为 None 。回到问题，为什么第一个函数中指定缺省值为 [] 会导致随着执行过程中，缺省参数的值会被保留下来呢？代码如下：

    :::python
    >>> def foo(l=[]):
    ...     l.append(1)
    ...     return l
    ... 
    >>> foo()
    [1]
    >>> foo()
    [1, 1]
    >>> foo()
    [1, 1, 1]
    >>> 

其实通过上面的罗嗦一大堆，答案很容易就可以得到了：foo 是一个 function 类型的对象，这个对象中有个 __defaults__ 属性，保存了命名参数 l 的值，而在一次次的调用过程中，因为没有传入参数，所以实际上 foo 函数改变的是命名参数的缺省值。也就是师弟所说的这个函数在一次次调用中保留了对命名参数l的结果的修改。而师弟贴出的第二个函数的命名参数缺省值是 None ，实质上就是没有缺省值，所以l的值修改没有在调用中保留下来。是不是真的这样？我们来看下：

    :::python
    >>> def foo(l=[]):
    ...     print 'default_arg_addr:' + str(id(l))
    ...     l.append(1)
    ...     print 'changed_var_addr:' + str(id(l))
    ...     print l
    ... 
    >>> id(foo.__defaults__[0])
    3077402860L
    >>> foo()
    default_arg_addr:3077402860
    changed_var_addr:3077402860
    [1]
    >>> foo()
    default_arg_addr:3077402860
    changed_var_addr:3077402860
    [1, 1]
    >>> foo.__defaults__
    ([1, 1],)
    >>> 

上面这个函数 foo 有一个命名参数 l ，它的命名参数缺省值是一个空的列表，虽然是空列表，可是它确确实实是一个对象，已经在内存给它分配了空间。我们可以通过 id 函数的结果看出来。然后是两次的调用 foo 函数可以看到，因为没有传入参数，所以这两次修改的都是这个缺省的命名参数的值，所以可以得到所谓的对 l 的值的修改保留下来了的感觉。

### 深入

首先我们应该明白，在 Python 中，一个对象的实例化和初始化是不同的。一个对象实例化调用的是对象的 __new__ 函数，而初始化调用的是 __init__ 函数。所以，要深入地去看在 Python 中，函数在实例化的时候到底发生了什么，我们应该要去看 Python 源码。如下，源码版本为 Python2.7.4。

Python2.7.4/Objects/funcobject.c, func_new, L436-L439

    :::c
    if (defaults != Py_None) {
        Py_INCREF(defaults);
        newfunc->func_defaults  = defaults;
    }

Python2.7.4/Include/object.h, L765-L767

    :::c
    #define Py_INCREF(op) (                     \
    _Py_INC_REFTOTAL  _Py_REF_DEBUG_COMMA       \
    ((PyObject*)(op))->ob_refcnt++)

上面第一段代码是 funcobject 的 func_new 中的代码，也就应该是 functions 对象的 __new__ 函数代码。可以看到，如果 defaults 不是 None，也就是说有值，而我们上面也提到 Python 中一切都是对象，所以就会对这个对象进行 Py_INCREF 操作，并且将这个 defaults 值设定为 func_defaults。Py_INCREF 操作是什么？从第二段代码可以看到，这是一个宏定义，将参数 op 的 ob_refcnt 值加一。ob_refcnt 是什么？refcnt----reference count，这样明白了，就是将该对象的引用计数值加一。在执行了函数函数之后，该命名函数的缺省值对象并没有被销毁，而是随着该函数对象的存在而存在。对这个缺省之对象的修改当然也会被保留下来。
