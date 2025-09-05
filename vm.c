#include "vm.h"
#include "switch.h"
#include <stddef.h>
#include <getopt.h>
#include <string.h>
#include <stdlib.h>
#include <errno.h>
#include <stdio.h>
#include <sys/mman.h>

// sc stand for static cast

int64_t sc_u2i(uint64_t x) {
  return *((int64_t *)&x);
}

double sc_u2f(uint64_t x) {
  return *((double *)&x);
}

double sc_i2f(int64_t x) {
  return *((double *)&x);
}

uint64_t sc_i2u(int64_t x) {
  return *((uint64_t *)&x);
}

uint64_t sc_f2u(double x) {
  return *((uint64_t *)&x);
}

int64_t sc_f2i(double x) {
  return *((int64_t *)&x);
}

char sc_vc2c(vmchar_t x) {
  return *((char *)&x);
}

vmchar_t sc_c2vc(char x) {
  return *((vmchar_t *)&x);
}

int vm_mblen(vmchar_t x) {
  if (x >> 7 == 0)
    return 1;
  if ((x >> 6 & 1) == 0)
    return -1;
  return __builtin_clz(~x);
}

int vm_strlen_mb(vmchar_t *x, int xlen, int nullendp) {
  int y, i, chlen;
  i = y = 0;
  while (nullendp ? x[i] : i < xlen) {
    chlen = vm_mblen(x[i]);
    if (chlen < 0)
      return -1;
    i += chlen;
    y += 1;
  }
  return y;
}

int vm_mbtoc64(uint64_t *restrict dst, vmchar_t *restrict src, int len) {
  uint64_t acc, chlen;
  chlen = vm_mblen(src[0]);
  if (chlen < 0)
    return -1;
  if (len < chlen) {
    return 0;
  }
  if (chlen == 1) {
    dst[0] = src[0];
    return 1;
  }
  acc = src[0] & (1u << (7 - chlen)) - 1;
  for (int i = 1;i < chlen;i++) {
    if ((src[i] >> 6) != 0b10)
      return -1;
    acc <<= 6;
    acc |= src[i] & ((1u << 6) - 1);
  }
  dst[0] = acc;
  return chlen;
}

int vm_c64tomb(vmchar_t *restrict dst, uint64_t src, int len) {
  if (src <= 0x7f) {
    if (len < 1)
      return 0;
    dst[0] = src;
    return 1;
  } else if (src <= 0x7ff) {
    if (len < 2)
      return 0;
    dst[0] = 0xc0 | (src >> 6);
    dst[1] = 0x80 | (src & 0x3f);
    return 2;
  } else if (src <= 0xffff) {
    if (len < 3)
      return 0;
    dst[0] = 0xe0 | (src >> 12);
    dst[1] = 0x80 | ((src >> 6) & 0x3f);
    dst[2] = 0x80 | (src & 0x3f);
    return 3;
  } else if (src <= 0x10ffff) {
    if (len < 4)
      return 0;
    dst[0] = 0xf0 | (src >> 18);
    dst[1] = 0x80 | ((src >> 12) & 0x3f);
    dst[2] = 0x80 | ((src >> 6) & 0x3f);
    dst[3] = 0x80 | (src & 0x3f);
    return 4;
  }
  return -1;
}

// ensure that a machine is running in only one place at a time
uint64_t execute(struct machine *machine) {
  uint64_t            uregs[8];
  double              fregs[8];
  uint64_t           *mem;
  size_t              memlen;
  __int128            ibignum;
  unsigned __int128   ubignum;
  ptrdiff_t           ptrdiff;

  for (size_t i = 0;i < 8;i++) {
    uregs[i] = machine->uregs[i];
    fregs[i] = machine->fregs[i];
  }
  mem = machine->mem;
  memlen = machine->memlen;

#ifdef __GNUC__
# define OPCODE(x) &&__LABEL__ ## x, 
#else
# define OPCODE(x)
#endif

#define pc       uregs[PC]
#define base     uregs[BASE]
#define frame    uregs[FRAME]
#define overflow uregs[OVERFLOW]
#define cond     uregs[COND]

#define op1 mem[pc+1]
#define op2 mem[pc+2]

  for (;;) {
    SWITCH_WITH
#include "opcode.h"
    BEGIN_SWITCH(pc)
    CASE(ULD):
      uregs[op1] = mem[uregs[op2]];
      pc += 3;
      BREAK;
    CASE(FLD):
      fregs[op1] = sc_u2f(mem[uregs[op2]]);
      pc += 3;
      BREAK;
    CASE(UST):
      mem[uregs[op1]] = uregs[op2];
      pc += 3;
      BREAK;
    CASE(FST):
      mem[uregs[op1]] = sc_f2u(fregs[op2]);
      pc += 3;
      BREAK;
    CASE(UIMM):
      uregs[op1] = op2;
      pc += 3;
      BREAK;
    CASE(FIMM):
      fregs[op1] = sc_u2f(op2);
      pc += 3;
      BREAK;
    CASE(UMOV):
      uregs[op1] = uregs[op2];
      pc += 3;
      BREAK;
    CASE(FMOV):
      fregs[op1] = fregs[op2];
      pc += 3;
      BREAK;
    CASE(U2F):
      fregs[op1] = (double)uregs[op2];
      pc += 3;
      BREAK;
    CASE(I2F):
      fregs[op1] = (double)sc_u2i(uregs[op2]);
      pc += 3;
      BREAK;
    CASE(F2U):
      uregs[op1] = (uint64_t)fregs[op2];
      pc += 3;
      BREAK;
    CASE(F2I):
      uregs[op1] = sc_i2u((int64_t)fregs[op2]);
      pc += 3;
      BREAK;
    CASE(BT):
      ptrdiff = sc_u2i(op1);
      pc += cond ? ptrdiff : 2;
      BREAK;
    CASE(BF):
      ptrdiff = sc_u2i(op1);
      pc += cond ? 2 : ptrdiff;
      BREAK;
    CASE(UEQ):
      cond = uregs[op1] == uregs[op2];
      pc += 3;
      BREAK;
    CASE(FEQ):
      cond = fregs[op1] == fregs[op2];
      pc += 3;
      BREAK;
    CASE(UGT):
      cond = uregs[op1] > uregs[op2];
      pc += 3;
      BREAK;
    CASE(IGT):
      cond = sc_u2i(uregs[op1]) > sc_u2i(uregs[op2]);
      pc += 3;
      BREAK;
    CASE(FGT):
      cond = fregs[op1] > fregs[op2];
      pc += 3;
      BREAK;
    CASE(ULT):
      cond = uregs[op1] < uregs[op2];
      pc += 3;
      BREAK;
    CASE(ILT):
      cond = sc_u2i(uregs[op1]) < sc_u2i(uregs[op2]);
      pc += 3;
      BREAK;
    CASE(FLT):
      cond = fregs[op1] < fregs[op2];
      pc += 3;
      BREAK;
    CASE(UADD):
      uregs[op1] += uregs[op2];
      pc += 3;
      BREAK;
    CASE(FADD):
      fregs[op1] += fregs[op2];
      pc += 3;
      BREAK;
    CASE(USUB):
      uregs[op1] -= uregs[op2];
      pc += 3;
      BREAK;
    CASE(FSUB):
      fregs[op1] -= fregs[op2];
      pc += 3;
      BREAK;
    CASE(UMUL):
      ubignum = (unsigned __int128)uregs[op1] * (unsigned __int128)uregs[op2];
      uregs[op1] = (uint64_t)ubignum;
      overflow = (uint64_t)(ubignum >> 64);
      pc += 3;
      BREAK;
    CASE(IMUL):
      ibignum = (__int128)sc_u2i(uregs[op1]) * (__int128)sc_u2i(uregs[op2]);
      uregs[op1] = sc_i2u((int64_t)ibignum);
      overflow = sc_i2u((int64_t)(ibignum >> 64));
      pc += 3;
      BREAK;
    CASE(FMUL):
      fregs[op1] *= fregs[op2];
      pc += 3;
      BREAK;
    CASE(UDIV): {
      uint64_t x;
      x = uregs[op1] % uregs[op2];
      uregs[op1] /= uregs[op2];
      overflow = x;
      pc += 3;
      BREAK;
    }
    CASE(IDIV): {
      int64_t t1, t2;
      t1 = sc_u2i(uregs[op1]);
      t2 = sc_u2i(uregs[op2]);
      uregs[op1] = sc_i2u(t1/t2);
      overflow = sc_i2u(t1%t2);
      pc += 3;
      BREAK;
    };
    CASE(FDIV):
      fregs[op1] /= fregs[op2];
      pc += 3;
      BREAK;
    CASE(CALL): {
      ureg_t r = op1;
      cfunc f = (void *)uregs[op2];
      pc += 3;

      // store
      for (size_t i = 0;i < 8;i++) {
        machine->uregs[i] = uregs[i];
        machine->fregs[i] = fregs[i];
      }
      machine->mem = mem;
      machine->memlen =memlen;

      uregs[r] = f(machine);

      // restore
      for (size_t i = 0;i < 8;i++) {
        uregs[i] = machine->uregs[i];
        fregs[i] = machine->fregs[i];
      }
      mem = machine->mem;
      memlen = machine->memlen;
      BREAK;
    }
    CASE(STOP):
      return uregs[op1];
    END_SWITCH
  }
}

void *chunk_alloc(size_t x) {
  if (x % BUFSIZ != 0) {
    size_t n = x / BUFSIZ;
    x = (n + 1) * BUFSIZ;
  }

  void   *no_addr, *addr, *chunk;
  size_t len, alloc_len;
  int    prot, prop, no_fd, no_off, ret;

  no_addr  = NULL;
  alloc_len = x + BUFSIZ * 2;
  prot      = PROT_READ | PROT_WRITE;
  prop      = MAP_ANON | MAP_PRIVATE;
  no_fd     = -1;
  no_off    = 0;
  chunk     = mmap(no_addr, alloc_len, prot, prop, no_fd, no_off);

  if (chunk == MAP_FAILED) {
    return NULL;
  }

  addr = chunk;
  len = BUFSIZ;
  prot = PROT_NONE;
  ret = mprotect(addr, len, prot);

  if (ret == -1) {
    munmap(chunk, alloc_len);
    return NULL;
  }

  addr = chunk + BUFSIZ + x;
  mprotect(addr, len, prot);

  if (ret == -1) {
    munmap(chunk, alloc_len);
    return NULL;
  }

  return chunk + BUFSIZ;
}

void chunk_free(void *chunk, size_t x) {
  if (x % BUFSIZ != 0) {
    size_t n = x / BUFSIZ;
    x = (n + 1) * BUFSIZ;
  }

  void   *addr;
  size_t len;
  
  addr = chunk - BUFSIZ;
  len = x + BUFSIZ * 2;
  munmap(addr, len);
}

void usage(const char *prog) {
  fprintf(stderr,
    "Usage:\t%s [-b bytes | --bytes bytes] file\n"
    "-b --bytes\tspecify bytes number of the vm, the vm use 64 bit byte\n",
    prog
  );
  exit(0);
}

static struct option opts[] = {
  {"bytes", required_argument, NULL, 'b'},
  {NULL,    0,                 NULL, 0},
};

int main(int argc, char *argv[]) {
  size_t bytes = 64 * 1024 * 1024;
  char ch;

  char *prog = argv[0];

  while ((ch = getopt_long(argc, argv, "m:", opts, NULL)) != -1) {
    switch (ch) {
    case 'b':
      errno = 0;
      bytes = atoll(optarg);
      if (errno) {
        fprintf(stderr, "%s: invalid byte count: %s", prog, strerror(errno));
        exit(errno);
      }
      break;
    default:
      usage(prog);
    }
  }

  if (argc == 1 || optind == argc)
    usage(prog);

  char *fname = argv[optind];

  FILE *f;
  if (strcmp(fname, "-"))
    f = stdin;
  else
    f = fopen(fname, "r");
  if (f == NULL) {
    perror(prog);
    exit(errno);
  }

  struct machine machine;
  memset(&machine, 0, sizeof(machine));
  machine.memlen = bytes;
  machine.mem = chunk_alloc(bytes);
  if (machine.mem == NULL) {
    perror(prog);
    exit(errno);
  }
  memset(machine.mem, 0, sizeof(int64_t) * bytes);

  size_t sret = fread(machine.mem + 1024, sizeof(int64_t), bytes - 1024, f);
  if (ferror(f)) {
    perror(prog);
    exit(errno);
  }
  if (feof(f)) {
    fprintf(stderr, "vm: address space is full\n");
    exit(errno);
  }

  machine.imglen = sret;

  machine.uregs[PC] = 1024;
  return execute(&machine);
}
