#ifndef STATIC_CONVERT_H__
#define STATIC_CONVERT_H__

#include <stdint.h>
#include "vm.h"
#include "utf64.h"

static inline char sc_vc2c(vmchar_t x) {
  return *((char *)&x);
}

static inline vmchar_t sc_c2vc(char x) {
  return *((vmchar_t *)&x);
}

static inline int64_t sc_u2i(uint64_t x) {
  return *((int64_t *)&x);
}

static inline double sc_u2f(uint64_t x) {
  return *((double *)&x);
}

static inline double sc_i2f(int64_t x) {
  return *((double *)&x);
}

static inline uint64_t sc_i2u(int64_t x) {
  return *((uint64_t *)&x);
}

static inline uint64_t sc_f2u(double x) {
  return *((uint64_t *)&x);
}

static inline int64_t sc_f2i(double x) {
  return *((int64_t *)&x);
}

#endif
