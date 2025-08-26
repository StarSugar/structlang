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
- vm.h -- used by vm.c.
