#include <stdint.h>
#include "vm.h"
#include "utf64.h"

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

int vm_strlen_c64(uint64_t *x) {
  int n = 0;
  while (*x++ != 0) n++;
  return n;
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
