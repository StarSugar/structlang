/* read utf8 string, convert them to utf64, and output them  */

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <stdarg.h>
#include <errno.h>
#include "utf64.h"

static void die(char *fmt, ...) {
  va_list va;
  va_start(va, fmt);
  vfprintf(stderr, fmt, va);
  va_end(va);
  exit(1);
}

int main(int argc, char *argv[]) {
  vmchar_t in[BUFSIZ];
  uint64_t out[BUFSIZ];
  int in_len, out_len, ret, in_transed;

  in_len = out_len = 0;

read_print_loop:
  in_len += fread(in + in_len, sizeof(char), BUFSIZ - in_len, stdin);
  if (ferror(stdin))
    die("%s: %s: while reading from stdin\n", argv[0], strerror(errno));
  in_transed = 0;

  for(;;) {
    if (out_len == BUFSIZ) {
      ret = fwrite(out, sizeof(uint64_t), BUFSIZ, stdout);
      if (ret != BUFSIZ)
        die("%s: %s: while writing to stdout\n", argv[0], strerror(errno));
      out_len = 0;
    }

    /* if the next utf8 character is not completely read */
    if (vm_mblen(*(in + in_transed)) > in_len - in_transed) {
      memmove(in, in + in_transed, in_len - in_transed);
      in_len = in_len - in_transed;
      break;
    }

    ret = vm_mbtoc64(out + out_len, in + in_transed, in_len - in_transed);
    if (ret <= 0)
      die("%s: not a valid utf8 character", argv[0]);
    out_len++;
    in_transed += ret;
  }

  if (!feof(stdin)) {
    goto read_print_loop;
  }

  if (in_len != 0)
    die("%s: not a valid utf8 character", argv[0]);

  return fwrite(out, sizeof(uint64_t), out_len, stdout) != out_len;
}
