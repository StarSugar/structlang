# STRUCTLANG

A structure language virtual machine and compiler.

To build the virtual machine, use `make vm`.

To clean the directory, use `make clean`.

## FILES
- Makefile -- well, the Makefile, see make(1);
- opcode.h -- x-macro and description for opcodes;
- README -- this file;
- switch.h -- a _thread code_ style `switch` statement defnition;
- vm.c -- the virtual machine, include a `main` function;
- vm.h -- used by vm.c;
- ams.pl -- a perl scirpt assembler;
- complr.py -- the compiler.

## ABI

### BASICS
Since the virtual machine can deal with at least 64 bit value, we name 64-bit-value _byte_.

At very beginning, the `pc` is 1024, and other registers are zero. This means the program entry locates at byte 1024, and the stack need to be initializes manually.

As `r0` is `pc`, `r3` stores remainder and 64-127 bits part of product, and `r4` is used by comparison and branch, we use `r1` as stack base pointer, and `r2` as stack frame pointer.

We suggest using the stack of 1048576 bytes, which is 1024 x 1024. We suggest the stack be at least 1024 bytes after the code image, aligned to 1024, and grow downward.

We suggest the heap be at least 1024 bytes after the stack, and grow upward.

### CALLING CONVENTION
All registers not used as argument register are callee-saved.

In function calls, `r7` always stores the [static chain](https://devblogs.microsoft.com/oldnewthing/20231204-00/?p=109095); `r3`-`r6` pass the first four integer arguments, and real arguments come in via `x0`-`x7`. Any object larger than two bytes is passed by its pointer and treated as an extra integer argument, which follows all ordinary integer arguments. The remaining integer arguments and real arguments, with two bytes arguments, are mixed together and pushed onto the stack in reversed order.

Functions produce integers to `r3`, and output reals to `x0`. After ordinary integers and objects larger than two bytes, the caller have to pass an extra pointer, which points to a place with enough space for the callee to stores results larger than two bytes into.

### C CALL
The ABI for calling **C** functions is same as calling general functions except that standard **C** functions don't accept any value larger than one byte, and r7 is the location of a **C** function in virtual machine Memory.

All of these functions may return -1 to indicate an error.

| C Call List | Position in Memory | Argument List                    | Result       | Description                                                                                                                                                                                                                                                                                                                                                          |
|:-----------:|:------------------:|:---------------------------------|:-------------|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| printf      | 1                  | `uint *fmt, ...`                 | `int length` | The stdio printf function, only support `%s`, `%d`, `%c`, `%u`, `%f` and `%x`.                                                                                                                                                                                                                                                                                       |
| fopen       | 2                  | `uint *name`                     | `int fd`     | the stdio fopen function, return a integer as fd.                                                                                                                                                                                                                                                                                                                    |
| fseek       | 3                  | `int fd, int offset, int whence` | `int newpos` | Seems like the stdio fseek function. The `fseek` sets the file position of fd. The new position measured in the virtual machine bytes, and `whence` is set to **0**, **1**, **2**, means the `offset` is relative to the start of the file, the current position, or end-of-file. The function generates current offset upon to successful completion, -1 otherwise. |
| writetxt    | 4                  | `int fd, uint *data, int len`    | `int ok`     | Write a sequence of letters `datas` to `fd`. The length of sequence is `len`. The function returns how many letters actually writted if successful, -1 otherwise.                                                                                                                                                                                                    |
| writebytes  | 5                  | `int fd, uint *data, int len`    | `int ok`     | Write a sequence of bytes `datas` to `fd`. The length of sequence is `len`. The function returns how many bytes actually writted if successful, -1 otherwise.                                                                                                                                                                                                        |
| readtxt     | 6                  | `int fd, uint *data, int len`    | `int ok`     | Read a sequence of letters `datas` to `fd`. The max length of sequence is `len`. The function returns how many letters actually readed if successful, -1 otherwise.                                                                                                                                                                                                  |
| readbytes   | 7                  | `int fd, uint *data, int len`    | `int ok`     | Read a sequence of bytes `datas` to `fd`. The max length of sequence is `len`. The function returns returns how many bytes actually readed if successful, -1 otherwise.                                                                                                                                                                                              |
| stdin       | 8                  |                                  |              | The stdio stdin variable.                                                                                                                                                                                                                                                                                                                                            |
| stdout      | 9                  |                                  |              | The stdio stdout variable.                                                                                                                                                                                                                                                                                                                                           |
| stderr      | 10                 |                                  |              | The stdio stderr variable.                                                                                                                                                                                                                                                                                                                                           |
| bytes       | 11                 |                                  | `int bytes`  | Output how many bytes the virtual machine has.                                                                                                                                                                                                                                                                                                                       |
| imgsiz      | 12                 |                                  | `int bytes`  | Output how many bytes the image used.                                                                                                                                                                                                                                                                                                                                |
