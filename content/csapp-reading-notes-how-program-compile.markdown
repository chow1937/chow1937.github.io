title: CSAPP读书笔记- 一个C程序的编译
date: 2012-10-9
category: readings
tags: csapp, reading-notes
slug: csapp-reading-notes-how-program-compile
author: tonychow
summary: 

CSAPP中，1.2节讲到了程序的编译:

> Programs Are Translated By Other Programs into Different Forms.

程序由其他程序翻译成不同的形式，其实看下面这张图应该可以很清晰地了解上面这一句：

![c程序编译](http://om3cpjyz4.bkt.clouddn.com/articles/c-program-compilation.jpg)

上图是一个 hello 的 C 程序由 GCC 编译器从源码文件 hello.c 中读取内容并将其翻译成为一个可执行的对象文件 hello 的过程。这个过程包含了几个阶段：

首先是源文件，此时是处于文本类型：

    :::c
    1 // C 代码
    2 #include <stdio.h>
    3 int main(int argc, char** argvs)
    4 {
    5     printf("hello, world\n");
    6 }

然后是预处理阶段，将对以#开始的指令进行修改，比如对于`#include <stdio.h>`指令，预处理器将会读取系统头文件 stdio.h 内容，然后将其内容直接插入到程序源码文本中，经过预处理之后源码文件被翻译成 hello.i 文件，此时得到的仍然是一个文本类型的 C 源码文件：

    :::c
    ......
    844
    845 extern void funlockfile (FILE *__stream) __attribute__ ((__nothrow__));
    846 # 938 "/usr/include/stdio.h" 3 4
    847
    848 # 2 "hello.c" 2
    849
    850 int main(int argc, char** argvs)
    851 {
    852     printf("hello, world\n");
    853 }

以上部分代码可以看出除了`#include <stdio.h>`指令之外其他指令并未被改变。

接下来的是编译阶段。在这个阶段中，前一阶段得到的c程序代码将会被编译器翻译成汇编语言的形式，每个汇编语言声明都对应一个机器语言指令。这个阶段得到的是一个文本类型的汇编语言源码文件 hello.s ：

    :::c
     1     .file   "hello.c"
     2     .section    .rodata
     3 .LC0:
     4     .string "hello, world"
     5     .text
     6 .globl main
     7     .type   main, @function
     8 main:
     9 .LFB0:
    10     .cfi_startproc
    11     pushq   %rbp
    12     .cfi_def_cfa_offset 16
    13     movq    %rsp, %rbp
    14     .cfi_offset 6, -16
    15     .cfi_def_cfa_register 6
    16     subq    $16, %rsp
    17     movl    %edi, -4(%rbp)
    18     movq    %rsi, -16(%rbp)
    19     movl    $.LC0, %edi
    20     call    puts
    21     leave
    22     .cfi_def_cfa 7, 8
    23     ret
    24     .cfi_endproc
    25 .LFE0:
    26     .size   main, .-main
    27     .ident  "GCC: (GNU) 4.4.4 20100726 (Red Hat 4.4.4-13)"
    28     .section    .note.GNU-stack,"",@progbits

之后是汇编器将上个阶段得到的汇编程序源码中的每条指令都翻译成机器代码，也就是 01 的形式，生成一个对象类型的文件 hello.o ，在这里用`objdump`查看下这个文件的内容：

    :::c
    hello.o:     file format elf64-x86-64

    Contents of section .text:
     0000 554889e5 4883ec10 897dfc48 8975f0bf  UH..H....}.H.u..
     0010 00000000 e8000000 00c9c3             ...........
    Contents of section .rodata:
     0000 68656c6c 6f2c2077 6f726c64 00        hello, world.
    Contents of section .comment:
     0000 00474343 3a202847 4e552920 342e342e  .GCC: (GNU) 4.4.
     0010 34203230 31303037 32362028 52656420  4 20100726 (Red
     0020 48617420 342e342e 342d3133 2900      Hat 4.4.4-13).
    Contents of section .eh_frame:
     0000 14000000 00000000 017a5200 01781001  .........zR..x..
     0010 1b0c0708 90010000 1c000000 1c000000  ................
     0020 00000000 1b000000 00410e10 4386020d  .........A..C...
     0030 06560c07 08000000                    .V......

最后一个阶段是链接阶段，链接程序将上一个步骤产生的hello.o文件与 C 编译器提供的 printf.o 文件合并到一起，因为 hello 代码中调用了标准 C 库中的 printf 函数。这两个对象文件将会被合并成为一个可执行的对象文件，这个文件可以加载到内存中执行。下面继续用`objdump`查看下这个 hello 对象文件的内容:

    :::c
    hello:     file format elf64-x86-64

    Contents of section .interp:
     400200 2f6c6962 36342f6c 642d6c69 6e75782d  /lib64/ld-linux-
     400210 7838362d 36342e73 6f2e3200           x86-64.so.2.
    Contents of section .note.ABI-tag:
     40021c 04000000 10000000 01000000 474e5500  ............GNU.
     40022c 00000000 02000000 06000000 12000000  ................
    Contents of section .note.gnu.build-id:
     40023c 04000000 14000000 03000000 474e5500  ............GNU.
     40024c 20b51099 4bd53844 69dcba88 4bf11585   ...K.8Di...K...
     40025c 599dda4e                             Y..N
    Contents of section .gnu.hash:
     400260 01000000 01000000 01000000 00000000  ................
     400270 00000000 00000000 00000000           ............
    ......
    ......
     600788 07000000 00000000 48034000 00000000  ........H.@.....
     600798 08000000 00000000 18000000 00000000  ................
     6007a8 09000000 00000000 18000000 00000000  ................
     6007b8 feffff6f 00000000 28034000 00000000  ...o....(.@.....
     6007c8 ffffff6f 00000000 01000000 00000000  ...o............
     6007d8 f0ffff6f 00000000 1e034000 00000000  ...o......@.....
     6007e8 00000000 00000000 00000000 00000000  ................
     6007f8 00000000 00000000 00000000 00000000  ................
     600808 00000000 00000000 00000000 00000000  ................
     600818 00000000 00000000 00000000 00000000  ................
     600828 00000000 00000000 00000000 00000000  ................
     600838 00000000 00000000 00000000 00000000  ................
    Contents of section .got:
     600848 00000000 00000000                    ........
    Contents of section .got.plt:
     600850 b8066000 00000000 00000000 00000000  ..`.............
     600860 00000000 00000000 be034000 00000000  ..........@.....
     600870 ce034000 00000000                    ..@.....
    Contents of section .data:
     600878 00000000                             ....
    Contents of section .comment:
     0000 4743433a 2028474e 55292034 2e342e34  GCC: (GNU) 4.4.4
     0010 20323031 30303732 36202852 65642048   20100726 (Red H
     0020 61742034 2e342e34 2d313329 00        at 4.4.4-13).

以上就是一个简单 C 语言 hello 程序的编译过程，已夜，晚安。

