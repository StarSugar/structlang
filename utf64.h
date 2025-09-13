#ifndef UTF64_H__
#define UTF64_H__

#include <stdint.h>
#include "vm.h"

int vm_mblen(vmchar_t x);
int vm_strlen_mb(vmchar_t *x, int xlen, int nullendp);
int vm_strlen_c64(uint64_t *x);
int vm_mbtoc64(uint64_t *restrict dst, vmchar_t *restrict src, int len);
int vm_c64tomb(vmchar_t *restrict dst, uint64_t src, int len);
ssize_t vm_strc64tomb(vmchar_t *dst, size_t *dstlen, uint64_t *src);
ssize_t vm_mc64tomb(vmchar_t *dst, size_t *dstlen, uint64_t *src, size_t srclen);
#endif
