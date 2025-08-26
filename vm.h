#ifndef VM_H_
#define VM_H_

#include <stdint.h>
#include <stdio.h>

struct machine;

typedef uint64_t uimm_t;
typedef int64_t  iimm_t;
typedef double   fimm_t;

typedef size_t ureg_t;
typedef size_t ireg_t;
typedef size_t freg_t;

typedef uint64_t(*cfunc)(struct machine*);

#define OPCODE(x) x,
enum opcode {
  #include "opcode.h"
};
#undef OPCODE

// except PC, other registers can used generally
enum special_regs {
  PC       = 0,
  BASE     = 1,
  FRAME    = 2,
  OVERFLOW = 3,
  COND     = 4,
};

// ensure that a machine is running in only one place at a time
struct machine {
  uint64_t  uregs[8];
  double    fregs[8];
  uint64_t *mem;
  size_t    memlen;
};

#endif /* VM_H_ */
