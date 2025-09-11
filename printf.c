#include <stdint.h>
#include <stdio.h>
#include <inttypes.h>
#include "vm.h"
#include "reinterprete_cast.h"
#include "utf64.h"
#include "thread_local.h"

#define SSSIZ 256 /* small string size */

/* NOTE: make sure smallstrbuf could fit a big float number string */
thread_local char buf[BUFSIZ], smallstrbuf[SSSIZ];
thread_local int bufcnt, cnt;
thread_local uint64_t ch;

static int vm_print_buf() {
  buf[bufcnt] = '\0';
  return printf("%s", buf);
}

static int put() {
  int i = 0, ret;
  while (smallstrbuf[i] != '\0') {
    cnt += 1;
    if (bufcnt >= BUFSIZ - 1) {
      ret = vm_print_buf();
      if (ret < 0)
        return ret;
      bufcnt = 0;
    }
    buf[bufcnt++] = smallstrbuf[i++];
  }
  return 0;
}

static int put_ch() {
  int ret;
  ret = vm_c64tomb((vmchar_t *)smallstrbuf, ch, SSSIZ);
  if (ret <= 0) {
    fprintf(stderr, "vm: String Conversion Error!\n");
    return ret;
  }
  return put();
}

uint64_t vm_printf(struct machine *machine) {
  int nth_int, nth_flo, nth_arg, ret, i, j;
  uint64_t *str, uint;
  double flo;

  nth_int = 4; nth_flo = 0; nth_arg = 1; cnt = 0;
  bufcnt = 0;
  str = &machine->mem[machine->uregs[3]];

  /* the following code use computed goto simulate nested function */

  for (; *str != '\0'; str++) {
    if ((ch = *str) != '%') {
      if ((ret = put_ch()) < 0) return ret;
    } else {
      /* extract the next possible `variable length' argument */
      uint = nth_int <= 7
        ? machine->uregs[nth_int]
        : machine->mem[machine->uregs[1] - nth_arg + 3];
      flo = nth_flo <= 7
        ? machine->fregs[nth_flo]
        : rc_u2f(machine->mem[machine->uregs[1] - nth_arg + 8]);
      switch (*(++str)) {
      case '%':
        ch = '%';
        if ((ret = put_ch()) < 0) return ret;
        break;
      case 's':
        nth_int += 1;
        nth_arg += 1;
        for (j = uint; machine->mem[j] != '\0'; j++) {
          ch = machine->mem[j];
          if ((ret = put_ch()) < 0) return ret;
        }
        break;
      case 'd':
        nth_int += 1;
        nth_arg += 1;
        sprintf(smallstrbuf, "%"PRId64, rc_u2i(uint));
        if ((ret = put()) < 0) return ret;
        break;
      case 'c':
        nth_int += 1;
        nth_arg += 1;
        ch = uint;
        if ((ret = put_ch()) < 0) return ret;
        break;
      case 'u':
        nth_int += 1;
        nth_arg += 1;
        ret = sprintf(smallstrbuf, "%"PRIu64, uint);
        if ((ret = put()) < 0) return ret;
        break;
      case 'f':
        nth_flo += 1;
        nth_arg += 1;
        ret = sprintf(smallstrbuf, "%lf", flo);
        if ((ret = put()) < 0) return ret;
        break;
      case 'x':
        nth_int += 1;
        nth_arg += 1;
        ret = sprintf(smallstrbuf, "%"PRIx64, uint);
        if ((ret = put()) < 0) return ret;
        break;
      case '\0':
        goto done;
      default:
        ch = *str;
        if ((ret = put_ch()) < 0) return ret;
        break;
      }
    }
  }

done:

  if ((ret = vm_print_buf()) < 0) return ret;
  return cnt;
}
