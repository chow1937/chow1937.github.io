title: Python 中 sqlite3 模块使用小记
date: 2013-5-12
category: python
tags: python, sqlite3
slug: sqlite3-in-python
author: tonychow
summary: 

### 前记

Python 的标准库中包含了对 sqlite 这个轻巧的数据库的支持模块，也就是 sqlite3 模块。sqlite 数据库的好处我就不多说了，小型而强大，适合很多小型或者中型的数据库应用。最近在使用 sqlite3 模块遇到一些问题，解决了，顺便就记下来。



### 问题

sqlite3 模块的使用很简单，如下这段测试代码，创建一个 person 数据表然后进行一次数据库查询操作。

    :::python
    #!/usr/bin/env pypthon
    #_*_ coding: utf-8 _*_


    import sqlite3
    
    SCHEMA = """
             CREATE TABLE person (
                 p_id int,
                 p_name text
             )
             """
    
    def init():
        data = [(1, 'tony'), (1, 'jack')]
        conn = sqlite3.connect(':memory:')
        c = conn.cursor()
        try:
            c.execute(SCHEMA)
            for person in data:
                c.execute('insert into person values(?, ?)', person)
            conn.commit()
        except sqlite3.Error as e:
            print 'error!', e.args[0]
        return conn


    if __name__ =='__main__':
        conn = init()
        c = conn.cursor()
        #Do a query.
        c.execute('select * from person where p_name = ?', 'tony')
        person = c.fetchone()
        print person

运行这段代码，抛出了个异常，如下提示：

    :::shell
    Traceback (most recent call last):
          File "sqlite3_test.py", line 32, in <module>
              c.execute('select * from person where p_name = ?', 'tony')
              sqlite3.ProgrammingError: Incorrect number of bindings supplied. The current statement uses 1, and there are 4 supplied.

很莫名奇妙是不？明明我提供的占位符?绑定只有一个字符串参数，可是却说我提供了四个。再看仔细点，说提供了四个，正好字符串 'tony' 是四个字符。

### 解决

翻了翻文档，发现也给出了一个占位符查询的例子如下：

    :::python
    t = (’RHAT’,)
    c.execute(’SELECT * FROM stocks WHERE symbol=?’, t)

所以将字符参数放到元组中就可以了，修改如下：

    :::python
    c.execute('select * from person where p_name = ?', ('tony'))

结果依旧是抛出了同样的异常。再仔细看下，漏了个','，于是加上：

    :::python
    c.execute('select * from person where p_name = ?', ('tony',))

这次终于得到最终的结果了,其中的字符为 unicode 类型：

    :::python
    (1, u'tony')

### 原因

但是为什么？ Python 中的 sqlite3 模块提供了对 sqlite 数据操作的 API，执行查询的函数是在 sqlite3 模块源码中定义的，很明显想要知道为啥，最好的方式是去看 sqlite3 模块的源码。我手上的 Python 源码是 Python-2.7.4，在源码 Python-2.7.4/Modules/_sqlite/cursor.c 的函数 PyObject* _pysqlite_query_execute(pysqlite_Cursor* self, int multiple, PyObject* args) 中 497-529 行：

    :::c
    ...
    
    /* execute() */
    if (!PyArg_ParseTuple(args, "O|O", &operation, &second_argument)) {
        goto error;
    }
    
    if (!PyString_Check(operation) && !PyUnicode_Check(operation)) {
        PyErr_SetString(PyExc_ValueError, "operation parameter must be str or unicode");
        goto error;
    }
    
    parameters_list = PyList_New(0);
    if (!parameters_list) {
        goto error;
    }
    
    if (second_argument == NULL) {
        second_argument = PyTuple_New(0);
        if (!second_argument) {
            goto error;
        }
    } else {
        Py_INCREF(second_argument);
    }
    if (PyList_Append(parameters_list, second_argument) != 0) {
        Py_DECREF(second_argument);
        goto error;
    }
    Py_DECREF(second_argument);
    
    parameters_iter = PyObject_GetIter(parameters_list);
    if (!parameters_iter) {
        goto error;
    }
    
    ...

从这段源码中可以看到这段代码将参数 args 解析成为 Python 的一个元组作为 parameters_list ，然后最这个得到的元组进行 iter 操作，不断地读取这个元组的元素作为参数，而 Python 中对一个字符串进行 parse tuple 会怎样？我觉得 PyArg_ParseTuple 这个函数的操作和以下代码会是类似的：

    :::python
    ...
    >>> tuple('test')
    ('t', 'e', 's', 't')
    ...

所以现在我们可以看到我们的答案了，sqlite3 模块中，cursor 对象的 execute 方法会接受两个参数，第二个参数会被 PyArg_ParseTuple 函数转化成为 Python中 的 tuple。而对一个字符进行 tuple parse 导致的结果是将这个字符串的每个字符作为 tuple 的一个元素，所以上面抛出错误的时候提示的提供了四个所以错误也可以理解了。那为什么'('tony')'同样是错误呢？如下：

    :::python
    >>> type(('tony'))
    <type 'str'>
    >>> type(('tony',))
    <type 'tuple'>

很明显，('tony')是一个 str 也就是一个字符串，相当于是 'tony'，而 ('tony',) 才是一个单元素的 tuple 。同样，因为：

    :::python
    >>> tuple(['tony'])
    ('tony',)

所以如果那一行查询执行改为：

    :::python
    c.execute('select * from person where p_name = ?', ['tony'])

同样也是可以执行成功的。
