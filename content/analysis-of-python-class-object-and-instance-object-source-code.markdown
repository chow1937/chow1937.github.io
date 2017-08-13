title: Python 类对象与实例对象源码分析
date: 2013-10-2
category: python
tags: python, source-reading
slug: python-class-object-source-code
author: tonychow
summary: 

### 一个有趣的现象

最近在翻 Python 的 Tutorial 的对象一章，随手在 Python 的交互 Shell 中敲了几段代码测试一下，发现了一个有趣的情况。代码如下：

    :::python
        >>> class TestCls(object):
        ...     
        ...     def say_hi(self):
        ...         print 'Hi!'
        ... 
        >>> t = TestCls()
        >>> t.say_hi()
        Hi!
        >>> t.ins_new_var = 101
        >>> t.ins_new_var
        101
        >>> TestCls.ins_new_var
        Traceback (most recent call last):
          File "<stdin>", line 1, in <module>
        AttributeError: type object 'TestCls' has no attribute 'ins_new_var'
        >>> TestCls.new_var = 100
        >>> TestCls.new_var
        100
        >>> t.new_var
        100

<!--more-->
这段代码中，定义了一个类 TestCls ，然后实例化了一个 TestCls 的对象 t。在 Python 中，一切皆对象，这是老生长谈了。而 Python 中的对象还有另外一个特性，就是可以在创建之后修改这个对象的属性和方法。如上所示，我们可以在创建了一个类对象 TestCls 和一个实例对象 t 之后，修改这两个对象，给它们分别添加了 `new_var` 和 `ins_new_var` 属性。从上面的运行结果可以看到，当我们给实例对象 t 添加属性 `ins_new_var` 之后，类对象 TestCls 中访问不了这个属性，但是对于类对象 TestCls 添加的新属性 `new_var` ，这个类对象的实例 t 却可以访问到。

从 Python 代码的这个表现，我们可以推测出一些事情。那就是 Python 中，对一个对象的属性的访问会首先在这个对象的命名空间搜索，如果找不到，那就去搜索这个对象的类的命名空间，直到找到，然后取值，或者抛出没有这个属性的异常。很明显， Python 中一个对象的实例，同时还共享了这个对象的命名空间。如下：

    :::python
        >>> dir(t)
        ['__class__', '__delattr__', '__dict__', '__doc__', '__format__',
        '__getattribute__', '__hash__', '__init__', '__module__', '__new__',
        '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__',
        '__str__', '__subclasshook__', '__weakref__', 'ins_new_var', 'new_var',
        'say_hi']
        >>> dir(TestCls)
        ['__class__', '__delattr__', '__dict__', '__doc__', '__format__',
        '__getattribute__', '__hash__', '__init__', '__module__', '__new__',
        '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__',
        '__str__', '__subclasshook__', '__weakref__', 'new_var', 'say_hi']
        >>> 

可以看到，dir 函数搜索到的实例对象 t 和类对象 TestCls 的基本一致，但是区别在于 t 比 TestCls 多了一个 `ins_new_var`。

    :::python
        >>> t.__dict__
        {'ins_new_var': 101}
        >>> TestCls.__dict__
        dict_proxy({'__module__': '__main__', 'say_hi': <function say_hi at
        0xb771e95c>, '__dict__': <attribute '__dict__' of 'TestCls' objects>,
        '__weakref__': <attribute '__weakref__' of 'TestCls' objects>, '__doc__':
        None, 'new_var': 100})
        >>> t.new_var = 100
        >>> t.__dict__
        {'ins_new_var': 101, 'new_var': 100}
        >>> 

从这里看到，当我们试图对 `t.new_var` 进行赋值时，t 的 `__dict__` 增加了一个 `new_var`。

上面的推测是否正确？也许直接去查看源码会得到答案。在本文中， Python 的源码均指 CPython 源码，版本为 2.7.4。

注1：一般是代码片段在上，分析在下。

### 数据结构

CPython 是 C 写的(很明显)，类对象和实例对象的数据结构都是 struct，定义在 CPython 源码目录的 Include/classobject.h 中：

    :::c
    typedef struct {
        PyObject_HEAD
        PyObject    *cl_bases;	/* A tuple of class objects */
        PyObject	*cl_dict;	/* A dictionary */
        PyObject	*cl_name;	/* A string */
        /* The following three are functions or NULL */
        PyObject	*cl_getattr;
        PyObject	*cl_setattr;
        PyObject	*cl_delattr;
        PyObject    *cl_weakreflist; /* List of weak references */
    } PyClassObject;
    
    typedef struct {
        PyObject_HEAD
        PyClassObject *in_class;	/* The class object */
        PyObject	  *in_dict;	/* A dictionary */
        PyObject	  *in_weakreflist; /* List of weak references */
    } PyInstanceObject;

这两个结构体并不复杂，除了所有 Python 对象都有的 `PyObject_HEAD` 宏之外，类对象 PyClassObject 中还有几个属性，分别是： `cl_bases` ，保存了这个类对象的所有父类(如果有的话)，这个属性是一个元组;`cl_dict` ，一个字典，保存的是属于这个类对象的属性和方法;`cl_name` ，保存的是这个类对象的名称，此外还有几个对象 `cl_getattr`, `cl_setattr`, `cl_delattr` ，。而实例对象则有 `in_class` 表示从哪个类对象实例化而来，还有 `in_dict` 同样是一个字典对象，保存了这个实例对象的属性和方法。可以看到，一个类的实例对象保存了这个实例对象实例化自哪个类对象。

`PyObject_HEAD` 的相关定义如下：

    :::c
     /* Define pointers to support a doubly-linked list of all live heap objects. */
    #define _PyObject_HEAD_EXTRA            \
    struct _object *_ob_next;           \
    struct _object *_ob_prev;
    
    /* PyObject_HEAD defines the initial segment of every PyObject. */
    #define PyObject_HEAD                   \
    _PyObject_HEAD_EXTRA                \
    Py_ssize_t ob_refcnt;               \
    struct _typeobject *ob_type;

可以看到这两个宏定义了 Python 中一个对象的常见属性，包括对象类型 `ob_type` 和对象的引用计数 `ob_refcnt`，这是因为 Python 的 GC 方式是引用计数。

### 创建函数

在 Python 中对于类对象 (PyClassObject) 和实例对象 (PyInstanceObject) 的相关函数有很多，在这里我们只是简单分析下创建类对象及实例对象的函数和关于查找属性部分的函数。

注2：这里对这几个函数的代码引用不是完全的。

#### 实例对象的创建函数

首先是创建类对象的函数：

    :::c
    static PyObject *
    class_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
    {

创建类对象的函数是 `class_new` ，参数是类型 type，还有多个参数元组对象 args 和多个关键字参数字典对象 kwds。

    :::c
    PyObject *name, *bases, *dict;
    static char *kwlist[] = {"name", "bases", "dict", 0};

这里新建了几个 PyObject 类型的指针，分别是 name， bases 和 dict ，分别用来保存类对象的名称，继承的父类和属性方法字典。此外还有一个字符串数组 kwlist。

    :::c
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "SOO", kwlist,
                                     &name, &bases, &dict))
        return NULL;
    return PyClass_New(bases, dict, name);

然后这里是调用 `PyArg_ParseTupleAndKeywords` 函数，这个函数的主要效果是解析参数 args 和 kwds ，得到创建新的类对象的参数 bases，dict，name，然后调用真正创建一个类对象的函数 `PyClass_New`。

    :::c
    PyObject *
    PyClass_New(PyObject *bases, PyObject *dict, PyObject *name)
         /* bases is NULL or tuple of classobjects! */
    {

`PyClass_New` 函数的有三个参数，分别是父类们 bases，类的属性方法字典 dict 和 类的名称 name。

接下来很长的一段代码都是对参数的解析及检查参数是否合法，比如 name 必须是一个字符串， dict 必须是一个字典等等，在这里略去。

    :::c
    if (PyDict_GetItem(dict, docstr) == NULL) {
        if (PyDict_SetItem(dict, docstr, Py_None) < 0)
            return NULL;
    }
    if (PyDict_GetItem(dict, modstr) == NULL) {
        PyObject *globals = PyEval_GetGlobals();
        if (globals != NULL) {
            PyObject *modname = PyDict_GetItem(globals, namestr);
            if (modname != NULL) {
                if (PyDict_SetItem(dict, modstr, modname) < 0)
                    return NULL;
            }
        }
    }

检查参数 dict 中是否有 `__doc__` 和 `__module__` 这两个键，如果 `__doc__` 不存在则设置并将其值设置为 `Py_None`，如果 `__module__` 也不存在则获取当前范围的全局变量，从中取得 `__module__` 所对应的值，赋给这个新类对象的 `__module__`。

    :::c
    if (bases == NULL) {
        bases = PyTuple_New(0);
        if (bases == NULL)
            return NULL;
    }
    else {
        Py_ssize_t i, n;
        PyObject *base;
        if (!PyTuple_Check(bases)) {
            PyErr_SetString(PyExc_TypeError,
                            "PyClass_New: bases must be a tuple");
            return NULL;
        }
        n = PyTuple_Size(bases);
        for (i = 0; i < n; i++) {
            base = PyTuple_GET_ITEM(bases, i);
            if (!PyClass_Check(base)) {
                if (PyCallable_Check(
                    (PyObject *) base->ob_type))
                    return PyObject_CallFunctionObjArgs(
                        (PyObject *) base->ob_type,
                        name, bases, dict, NULL);
                PyErr_SetString(PyExc_TypeError,
                    "PyClass_New: base must be a class");
                return NULL;
            }
        }
        Py_INCREF(bases);
    }

检查 bases 参数是否为空，如果为空则新建一个值为 0 的元组赋给 bases。不为空，则 bases 应该是一个类对象的元组，依次对这个元组中的类对象进行检测，是否为类对象，如果不是类对象，则检测是否可调用 (callable) ，然后返回相应的错误信息或者一个可调用函数对象的执行结果(可调用)。

最后如果 bases 参数合法，这个参数对象的引用计数加一。

    :::c
    if (getattrstr == NULL) {
        getattrstr = PyString_InternFromString("__getattr__");
        if (getattrstr == NULL)
            goto alloc_error;
        setattrstr = PyString_InternFromString("__setattr__");
        if (setattrstr == NULL)
            goto alloc_error;
        delattrstr = PyString_InternFromString("__delattr__");
        if (delattrstr == NULL)
            goto alloc_error;
    }

`getattrstr` ，`setattrstr` 和 `delattrstr` 是三个全局的 static PyObject 指针变量，上面这一段分别给它们赋值字符串对象。

    :::c
        op = PyObject_GC_New(PyClassObject, &PyClass_Type);
        if (op == NULL) {
    alloc_error:
            Py_DECREF(bases);
            return NULL;
        }

给这个类对象分配内存，这个内存是在堆分配的而且受到 CPython 的 GC 管理的。

    :::c
    op->cl_bases = bases;
    Py_INCREF(dict);
    op->cl_dict = dict;
    Py_XINCREF(name);
    op->cl_name = name;
    op->cl_weakreflist = NULL;

将三个参数分别赋给这个新建的类对象 op。

    :::c
        op->cl_getattr = class_lookup(op, getattrstr, &dummy);
        op->cl_setattr = class_lookup(op, setattrstr, &dummy);
        op->cl_delattr = class_lookup(op, delattrstr, &dummy);
        Py_XINCREF(op->cl_getattr);
        Py_XINCREF(op->cl_setattr);
        Py_XINCREF(op->cl_delattr);
        _PyObject_GC_TRACK(op);
        return (PyObject *) op;
    }

然后分别设置这个新类对象的 getattr , setattr 和 delattr 函数，增加这几个函数的引用计数等等，最后返回这个新建的类对象的指针。

#### 实例对象的创建函数

实例对象 PyInstanceObject 同样也有个类似的 `instance_new` 函数：

    :::c
    static PyObject *
    instance_new(PyTypeObject* type, PyObject* args, PyObject *kw)
    {

参数也和 `class_new` 类似，三个参数分别为 type ， args 和 kw，

    :::c
    PyObject *klass;
    PyObject *dict = Py_None;

    if (!PyArg_ParseTuple(args, "O!|O:instance",
                          &PyClass_Type, &klass, &dict))
        return NULL;

解析参数，

    :::c
    if (dict == Py_None)
        dict = NULL;
    else if (!PyDict_Check(dict)) {
        PyErr_SetString(PyExc_TypeError,
              "instance() second arg must be dictionary or None");
        return NULL;
    }

检查 dict 参数的合法性，

    :::c
        return PyInstance_NewRaw(klass, dict);
    }

调用 `PyInstance_NewRaw` 函数，这个才是返回新实例对象的函数：

    :::c
    PyObject *
    PyInstance_NewRaw(PyObject *klass, PyObject *dict)
    {
        PyInstanceObject *inst;

参数只有所实例化自的类对象和属性方法字典 dict ，

    :::c
    if (!PyClass_Check(klass)) {
        PyErr_BadInternalCall();
        return NULL;
    }
    if (dict == NULL) {
        dict = PyDict_New();
        if (dict == NULL)
            return NULL;
    }
    else {
        if (!PyDict_Check(dict)) {
            PyErr_BadInternalCall();
            return NULL;
        }
        Py_INCREF(dict);
    }

检查参数的合法性，如果 dict 为空 (NULL) 则调用 `PyDict_New` 参数新建一个字典对象赋给 dict，否则检查 dict 是否是一个 CPython 的字典对象，

    :::c
    inst = PyObject_GC_New(PyInstanceObject, &PyInstance_Type);
    if (inst == NULL) {
        Py_DECREF(dict);
        return NULL;
    }

同样是调用 `PyObject_GC_New` 函数，给这个新建的实例对象分配内存，`PyInstance_Type` 是一个全局的 PyTypeObject 类型的变量，

    :::c
        inst->in_weakreflist = NULL;
        Py_INCREF(klass);
        inst->in_class = (PyClassObject *)klass;
        inst->in_dict = dict;
        _PyObject_GC_TRACK(inst);
        return (PyObject *)inst;
    }

最后给新建的实例对象赋值相关属性，然后返回这个新建实例对象的指针。

对于 CPython 的实例对象而言，除了 `instance_new` 之外，还有另外的一个函数也可以创建一个实例对象：

    :::c
    PyObject *
    PyInstance_New(PyObject *klass, PyObject *arg, PyObject *kw)
    {
        register PyInstanceObject *inst;
        PyObject *init;
        static PyObject *initstr;

`PyInstance_New` 函数也有三个参数，除了第一个是 klass 表示类对象之外，另外两个和 `instance_new` 函数类似，

    :::c
        if (initstr == NULL) {
            initstr = PyString_InternFromString("__init__");
            if (initstr == NULL)
                return NULL;
        }
        inst = (PyInstanceObject *) PyInstance_NewRaw(klass, NULL);

可以看到在这里调用了 `PyInstance_NewRaw` 函数创建一个新的实例对象，区别在于 dict 参数为 NULL ，这意味着新建的实例对象没有自己的属性和方法，

    :::c
        if (inst == NULL)
            return NULL;
        init = instance_getattr2(inst, initstr);
        if (init == NULL) {
            if (PyErr_Occurred()) {
                Py_DECREF(inst);
                return NULL;
            }
            if ((arg != NULL && (!PyTuple_Check(arg) ||
                                 PyTuple_Size(arg) != 0))
                || (kw != NULL && (!PyDict_Check(kw) ||
                                  PyDict_Size(kw) != 0))) {
                PyErr_SetString(PyExc_TypeError,
                           "this constructor takes no arguments");
                Py_DECREF(inst);
                inst = NULL;
            }
        }

在新建的实例对象中查找初始化函数 init ，如果不存在 (init 为 NULL) 且发生错误，则返回 NULL ，没有错误则检查 arg 和 kw 这两个参数，设置错误字符串，同样将新建实例对象 inst 置为 NULL，

    :::c
        else {
            PyObject *res = PyEval_CallObjectWithKeywords(init, arg, kw);
            Py_DECREF(init);
            if (res == NULL) {
                Py_DECREF(inst);
                inst = NULL;
            }
            else {
                if (res != Py_None) {
                    PyErr_SetString(PyExc_TypeError,
                               "__init__() should return None");
                    Py_DECREF(inst);
                    inst = NULL;
                }
                Py_DECREF(res);
            }
        }

init 不为空即意味找到了初始化实例的函数，将初始化函数和参数 arg ，kw 作为参数调用，初始化这个实例对象，

    :::c
        return (PyObject *)inst;
    }

最后返回这个新建的实例对象。

### 查找函数与 getattr， setattr 函数

分析完创建类对象和实例对象的函数之后，我们来分析相关的查找函数，然后还有最重要的 getattr 和 setattr。类对象和实例对象都有自己特有的 getattr 和 setattr 函数，这两类函数正是 Python 中使用 dot 操作符取对象的属性值或者给对象属性赋值所调用的函数。

#### 类对象的查找函数

首先是类对象的查找函数 `class_lookup`，在类对象的创建函数中也曾调用这个函数：

    :::c
    static PyObject *
    class_lookup(PyClassObject *cp, PyObject *name, PyClassObject **pclass)
    {

`class_lookup` 函数有三个参数，分别是类对象指针 cp，查找的属性名称 name 和指向类对象指针的指针变量 pclass，

    :::c
        Py_ssize_t i, n;
        PyObject *value = PyDict_GetItem(cp->cl_dict, name);
        if (value != NULL) {
            *pclass = cp;
            return value;
        }

首先查找的是类对象 cp 的 `cl_dict` 字典，如果找到的值 value 不为空，即已经找到了这个属性的值，则将 pclass 所指向的地址为 cp 类对象的地址，然后返回这个 value，

    :::c
        n = PyTuple_Size(cp->cl_bases);

否则计算类对象 cp 的父类的个数，也就是 `cl_bases` 元组的大小，

    :::c
        for (i = 0; i < n; i++) {
            /* XXX What if one of the bases is not a class? */
            PyObject *v = class_lookup(
                (PyClassObject *)
                PyTuple_GetItem(cp->cl_bases, i), name, pclass);
            if (v != NULL)
                return v;
        }

对 cp 的所有父类递归调用 `class_lookup` 函数，直到找到这个 name 属性的值，返回到 v 变量，如果 v 非 NULL 则返回 v，

    :::c
        return NULL;
    }

否则返回 NULL ，表示查找不到这个 name 属性的值。

#### 类对象的 getattr 函数

类对象的 getattr 函数实际上调用了 `class_lookup`函数，如下：

    :::c
    static PyObject *
    class_getattr(register PyClassObject *op, PyObject *name)
    {
        register PyObject *v;
        register char *sname;
        PyClassObject *klass;
        descrgetfunc f;

有两个参数，分别为类对象指针 op 和 所要获取的属性名称 name,

    :::c
        if (!PyString_Check(name)) {
            PyErr_SetString(PyExc_TypeError, "attribute name must be a string");
            return NULL;
        }

首先也是检查参数的合法性，确定 name 为 PyString 对象，以防错误，

    :::c
        sname = PyString_AsString(name);
        if (sname[0] == '_' && sname[1] == '_') {
            if (strcmp(sname, "__dict__") == 0) {
                if (PyEval_GetRestricted()) {
                    PyErr_SetString(PyExc_RuntimeError,
                   "class.__dict__ not accessible in restricted mode");
                    return NULL;
                }
                Py_INCREF(op->cl_dict);
                return op->cl_dict;
            }
            if (strcmp(sname, "__bases__") == 0) {
                Py_INCREF(op->cl_bases);
                return op->cl_bases;
            }
            if (strcmp(sname, "__name__") == 0) {
                if (op->cl_name == NULL)
                    v = Py_None;
                else
                    v = op->cl_name;
                Py_INCREF(v);
                return v;
            }
        }

这一段首先是检查要获取的是否为特殊属性 `__dict__`, `__bases__` 和 `__name__`，如果是则返回这个类对象的那个特殊属性。之所以作这样的检查是因为接下来就要执行 `class_lookup` 函数查找，从上面的分析可以知道， `class_lookup` 函数还会查找其父类，而这些特殊属性每个类对象都有的，所以先做检查可以防止返回错误的属性值，

    :::c
        v = class_lookup(op, name, &klass);
        if (v == NULL) {
            PyErr_Format(PyExc_AttributeError,
                         "class %.50s has no attribute '%.400s'",
                         PyString_AS_STRING(op->cl_name), sname);
            return NULL;
        }

通过 `class_lookup` 函数查找这个值，如果找不到则返回 NULL，

    :::c
        f = TP_DESCR_GET(v->ob_type);
        if (f == NULL)
            Py_INCREF(v);
        else
            v = f(v, (PyObject *)NULL, (PyObject *)op);
            
        return v;
    }

如果找到则尝试获取这个属性值对象的描述符，如果找到(实现了 `__get__` 方法)，则调用这个描述符方法，因为是类对象，所以第二个参数为 NULL。最后返回值 v 。

#### 类对象的 setattr 函数

接下来的是类对象的 setattr 函数：

    :::c
    static int
    class_setattr(PyClassObject *op, PyObject *name, PyObject *v)
    {

`class_setattr` 函数有三个参数，分别是类对象指针 op，属性名称 name 和属性的值 v，

    :::c
        char *sname;
        if (PyEval_GetRestricted()) {
            PyErr_SetString(PyExc_RuntimeError,
                       "classes are read-only in restricted mode");
            return -1;
        }

注意到这里首先检查了此时是否处于受限制模式，如果处于受限制模式，此时类对象是只读的，函数将返回错误码 -1。受限模式下，不受信任的代码的执行将会受到限制。

    :::c
        if (!PyString_Check(name)) {
            PyErr_SetString(PyExc_TypeError, "attribute name must be a string");
            return -1;
        }
        sname = PyString_AsString(name);

然后是同样检查 name 参数是否为一个 PyString 对象，是则根据这个字符串对象返回一个 C 中的字符串，方便下面的比较。

接下来的一大段代码都是检查上面得到的这个 sname 字符串是否为特殊方法或者特殊的属性，比如 `__dict__` 或者 `__getattr__` 等，如果是则调用相关的函数 `set_dict` 等，一般来说这些特殊属性是不可以修改的，所以会返回错误提示。

    :::c
        if (v == NULL) {
            int rv = PyDict_DelItem(op->cl_dict, name);
            if (rv < 0)
                PyErr_Format(PyExc_AttributeError,
                             "class %.50s has no attribute '%.400s'",
                             PyString_AS_STRING(op->cl_name), sname);
            return rv;
        }

参数 v 为空则将这个保存在类对象结构体 `cl_dict` 成员中的 name 属性删除掉，

    :::c
        else
            return PyDict_SetItem(op->cl_dict, name, v);
    }

否则，给这个属性 name 赋值 v，保存在类对象的 `cl_dict` 中。`PyDict_SetItem` 函数将会检测第一个字典参数中是否具有第二个参数 name 这个键，存在则更新其对应的值为 v，不存在则新建一个键，其值也是 v。

#### 实例对象的 getattr 函数

实例对象只有一个简单地搜索属性字典 dict 的函数 `_PyInstance_Lookup`，这个函数很简单，就是里面做了一点的检查，然后就调用了 `PyDict_GetItem` 函数从实例对象的 dict 中获取这个值。

而实例对象的 getattr 函数则更多地调用到了`class_lookup` 函数。CPython 的源码中，关于实例对象的 getattr 和 setattr 函数灰常蛋疼，getattr 函数有三个，分别是 `instance_getattr` ，`instance_getattr1` 和 `instance_getattr2`...而 setattr 函数也有两个，分别是 `instance_setattr1` 和 `instance_setattr`。如下：

    :::c
    static PyObject *
    instance_getattr(register PyInstanceObject *inst, PyObject *name)
    {

参数是实例对象指针 inst 和属性名称 name，

    :::c
        register PyObject *func, *res;
        res = instance_getattr1(inst, name);

其实在这里就调用 `instance_getattr1` 函数了，参数是一致的，如果 `instance_getattr1` 函数的返回非 NULL，则直接会返回这个结果，下面一段不会执行，

    :::c
        if (res == NULL && (func = inst->in_class->cl_getattr) != NULL) {
            PyObject *args;
            if (!PyErr_ExceptionMatches(PyExc_AttributeError))
                return NULL;
            PyErr_Clear();
            args = PyTuple_Pack(2, inst, name);
            if (args == NULL)
                return NULL;
            res = PyEval_CallObject(func, args);
            Py_DECREF(args);
        }

如果 `isntance_getattr1` 函数的返回值为 NULL 并且实例对象的类的 getattr 函数存在，则调用这个类对像的 getattr 函数，参数是将实例对象指针 inst 和属性名称 name 打包成的元组。

    :::c
        return res;
    }

最后返回结果。

`instance_getattr1` 函数如下：

    :::c
    static PyObject *
    instance_getattr1(register PyInstanceObject *inst, PyObject *name)
    {

参数同样是 inst 和 name，

    :::c
        register PyObject *v;
        register char *sname;
    
        if (!PyString_Check(name)) {
            PyErr_SetString(PyExc_TypeError, "attribute name must be a string");
            return NULL;
        }
    
        sname = PyString_AsString(name);

例行检查参数的合法性，合法则将 name 参数转化为 C 的字符串，

    :::c
        if (sname[0] == '_' && sname[1] == '_') {
            if (strcmp(sname, "__dict__") == 0) {
                if (PyEval_GetRestricted()) {
                    PyErr_SetString(PyExc_RuntimeError,
                "instance.__dict__ not accessible in restricted mode");
                    return NULL;
                }
                Py_INCREF(inst->in_dict);
                return inst->in_dict;
            }
            if (strcmp(sname, "__class__") == 0) {
                Py_INCREF(inst->in_class);
                return (PyObject *)inst->in_class;
            }
        }

同样是检查是否为特殊的属性，主要是以 `__` 作为开头的属性，这里处理的只有 `__dict__` 和 `__class__`。如果是 `__dict__` ，在受限模式下，会抛出错误表明不可以读取，非受限模式下则返回这个实例对象的属性字典 dict。如果是 `__class__` ，也是对应地返回实例对象的类。 

    :::c
        v = instance_getattr2(inst, name);
        if (v == NULL && !PyErr_Occurred()) {
            PyErr_Format(PyExc_AttributeError,
                         "%.50s instance has no attribute '%.400s'",
                         PyString_AS_STRING(inst->in_class->cl_name), sname);
        }
        return v;
    }

然后调用了 `instance_getattr2` 函数，如果其返回值为 NULL 则表示不存在这个属性，输出提示，否则返回这个结果 v。

    :::c
    static PyObject *
    instance_getattr2(register PyInstanceObject *inst, PyObject *name)
    {
        register PyObject *v;
        PyClassObject *klass;
        descrgetfunc f;

同样的， `instance_getattr2` 函数也是有两个参数 inst 和 name，

    :::c
        v = PyDict_GetItem(inst->in_dict, name);
        if (v != NULL) {
            Py_INCREF(v);
            return v;
        }

首先在这个实例对象的 in_dict 中查找这个属性，如果找到则直接返回其值，

    :::c
        v = class_lookup(inst->in_class, name, &klass);

没有找到则去查找这个实例对象的类对象 `in_class`，通过上面对 `class_lookup` 函数的分析我们可以知道，这个查找会一直从实例对象所属的类，其类的父类，父类的父类一直搜索，直到搜索完毕。如果找到了，则返回这个属性的值对象。

    :::c
        if (v != NULL) {
            Py_INCREF(v);
            f = TP_DESCR_GET(v->ob_type);
            if (f != NULL) {
                PyObject *w = f(v, (PyObject *)inst,
                                (PyObject *)(inst->in_class));
                Py_DECREF(v);
                v = w;
            }

在这里同样也试图获取这个实例对象对应类型的描述符方法，

    :::c
        }
        return v;
    }

返回结果 v ，有值或者 NULL。

从对上面三个 getattr 函数的分析可以看到，其实这三个函数各有其功能，比如 `instance_getattr1` 处理的是特殊属性，而 `instance_getattr2` 则是对应普通的属性，会一直搜索到其所属的类和其类的父类等等。如果这两个函数都没有结果，则会调用其类的 getattr 函数。

所以这三个函数其实是有其各自的职责的，当然它们三个是可以合并起来成为一个大函数的，但是估计就是不希望看到一个大函数的出现所以才分散为三个函数，这样职责更小更分明。

#### 实例对象的 setattr 函数

    :::c
    static int
    instance_setattr(PyInstanceObject *inst, PyObject *name, PyObject *v)
    {
        PyObject *func, *args, *res, *tmp;
        char *sname;

`instance_setattr` 函数有三个参数，毫无疑问分别是实例对象指针 inst ，属性名称 name 和值 v，

    :::c
        if (!PyString_Check(name)) {
            PyErr_SetString(PyExc_TypeError, "attribute name must be a string");
            return -1;
        }
    
        sname = PyString_AsString(name);


同样，惯例检查 name 参数的合法性，合法则转化为 C 的字符串类型变量，

    :::c
        if (sname[0] == '_' && sname[1] == '_') {
            Py_ssize_t n = PyString_Size(name);
            if (sname[n-1] == '_' && sname[n-2] == '_') {


判断是否为特殊属性，

    :::c
                if (strcmp(sname, "__dict__") == 0) {
                    if (PyEval_GetRestricted()) {
                        PyErr_SetString(PyExc_RuntimeError,
                     "__dict__ not accessible in restricted mode");
                        return -1;
                    }
                    if (v == NULL || !PyDict_Check(v)) {
                        PyErr_SetString(PyExc_TypeError,
                           "__dict__ must be set to a dictionary");
                        return -1;
                    }
                    tmp = inst->in_dict;
                    Py_INCREF(v);
                    inst->in_dict = v;
                    Py_DECREF(tmp);
                    return 0;
                }

是 `__dict__` 则检查是否为受限模式，检查传入的 v 参数是否为合法的 PyDict 对象，如果是则将 v 赋值给实例对象的 `in_dict`。可以注意到，这里用了一个 tmp 变量来保存实例对象之前的 `in_dict` 变量，然后将其引用计数减一。    

    :::c
    if (strcmp(sname, "__class__") == 0) {
        if (PyEval_GetRestricted()) {
            PyErr_SetString(PyExc_RuntimeError,
        "__class__ not accessible in restricted mode");
            return -1;
        }
        if (v == NULL || !PyClass_Check(v)) {
            PyErr_SetString(PyExc_TypeError,
               "__class__ must be set to a class");
            return -1;
        }
        tmp = (PyObject *)(inst->in_class);
        Py_INCREF(v);
        inst->in_class = (PyClassObject *)v;
        Py_DECREF(tmp);
        return 0;
    }

如果是 `__class__` 和上面的操作类似。通过这一段代码，我们可以看到在非受限模式的情况下，一个实例对象的类是可以被动态修改的。

    :::c
            }
        }
        if (v == NULL)
            func = inst->in_class->cl_delattr;
        else
            func = inst->in_class->cl_setattr;

如果参数 v 为 NULL，则表示要将实例对象的这个属性删除掉，试图去获取实例对象所对应的类对象的 delattr 函数。v 不为 NULL 则获取类对象的 setattr 函数，

    :::c
        if (func == NULL)
            return instance_setattr1(inst, name, v);

如果没有获取到任何的函数，则将会调用 `instance_setattr1` 函数。

    :::c
        if (v == NULL)
            args = PyTuple_Pack(2, inst, name);
        else
            args = PyTuple_Pack(3, inst, name, v);
        if (args == NULL)
            return -1;
        res = PyEval_CallObject(func, args);

无论得到的是类对象的 delattr 还是 setattr 函数，这里将会调用这个函数，区别在于调用 delattr 函数参数元组只有 inst 和 name 而调用 setattr 函数参数则是多了一个参数 v。根据上面对类对象的 setattr 的分析可以知道，如果这个类有 setattr 函数，则将会调用它的 setattr 函数。

    :::c
        Py_DECREF(args);
        if (res == NULL)
            return -1;
        Py_DECREF(res);
        return 0;
    }

执行成功则返回 0。

    :::c
    static int
    instance_setattr1(PyInstanceObject *inst, PyObject *name, PyObject *v)
    {
        if (v == NULL) {
            int rv = PyDict_DelItem(inst->in_dict, name);
            if (rv < 0)
                PyErr_Format(PyExc_AttributeError,
                             "%.50s instance has no attribute '%.400s'",
                             PyString_AS_STRING(inst->in_class->cl_name),
                             PyString_AS_STRING(name));
            return rv;
        }

如果参数 v 为空，则表示删除这个属性，所以将会调用 `PyDict_DelItem` 函数将这个属性从实例对象的 dict 字典中删除，

    :::c
        else
            return PyDict_SetItem(inst->in_dict, name, v);
    }

否则就直接调用 `PyDict_SetItem` 函数更新 dict 中的这个值或者添加进 dict 中。

从上面对这两个 setattr 函数的分析，同样可以知道，这两个函数各自有其职责。`instance_setattr` 主要是对特殊属性进行处理或者是调用其类对象的 setattr 或者 delattr 函数，而 `instance_setattr1` 函数则是对这个实例对象的 dict 进行 `set_item` 或者 `del_item` 操作。

### 总结

其实写到后面已经有点头大了，引用了一大堆源码更像是给源码注释了。但是既然已经写了，那就当给源码注释把它给写完了。

虽然是罗嗦了一堆，但是通过这个分析过程，对于文章开头的那几段代码的情况还是很清晰的：

* 首先，给实例对象 t 添加一个属性 `ins_new_var` 则将会保存到 t 的 `__dict__` 中;
* 而当试图在类对象 TestCls 中取 `ins_new_var` 的时候，只会去搜索这个类对象的 dict 和其父类的 dict ，这肯定是找不到的，所以返回属性错误;
* 当给类对象 TestCls 添加一个属性 `new_var` 的时候，同样，会在 `__dict__` 中添加一个 `new_var` 对象;
* 当访问 t.new_var 的时候，在 t 的命名空间中搜索不到 `new_var` 的时候，就回去搜索其实例化自的类对象的命名空间，所以，就可以得到这个值了。
