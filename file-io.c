#include "file-io.h"

#include <stddef.h>
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include "vm.h"
#include "reinterpret_cast.h"
#include "utf64.h"
#include "thread_local.h"

const size_t FD_COUNT = 2048;

FILE *fds[FD_COUNT];

int vm_file_io_init() {
  int i;

  i = 0;
  while (i < FD_COUNT) {
    fds[i++] = NULL;
  }

  fds[0] = stdin;
  fds[1] = stdout;
  fds[2] = stderr;

  return 0;
}

struct vmcharplist {
  struct vmcharplist *next;
  size_t cnt;
  vmchar_t buf[BUFSIZ - sizeof(void *) - sizeof(size_t)];
};

void vmcharplist_init(struct vmcharplist *p) {
  p->cnt = 0;
  p->next = NULL;
}

static char *collmb(uint64_t *str, char *maybe_buf, size_t maybe_buf_len) {
  struct vmcharplist *cur, head, *tmp;
  ssize_t ret;
  size_t cnt, off, bufcnt;
  cur = &head;
  vmchar_t *buf;

  vmcharplist_init(&head);
  cnt = 0;

  for (;;) {
    bufcnt = sizeof(cur->buf);
    ret = vm_strc64tomb(cur->buf, &bufcnt, str);
    if (ret < 0)
      goto error;
    str += ret;
    cur->cnt = bufcnt;
    cnt += bufcnt;
    if (*str == '\0')
      break;
    if ((cur->next = malloc(sizeof(struct vmcharplist))) == NULL)
      goto error;
    vmcharplist_init(cur->next);
    cur = cur->next;
  };

  if (cnt + 1 <= maybe_buf_len) {
    buf = (vmchar_t *)maybe_buf;
  } else {
    buf = malloc(cnt + 1);
    if (buf == NULL)
      goto error;
  }

  cur = &head;
  off = 0;

  memcpy(&buf[0], cur->buf, cur->cnt);
  off += cur->cnt;
  cur = cur->next;
  while (cur != NULL) {
    tmp = cur->next;
    memcpy(&buf[off], cur->buf, cur->cnt);
    off += cur->cnt;
    free(cur);
    cur = tmp;
  }
  buf[cnt] = '\0';
  return (char *)buf;

error:
  cur = head.next;
  while (cur != NULL) {
    tmp = cur->next;
    free(cur);
    cur = tmp;
  }
  return NULL;
}

uint64_t vm_fopen(struct machine *vm) {
  uint64_t *name, *mode, i, fd;
  char _cname[BUFSIZ], *cname, _cmode[16], *cmode;
  FILE *f;

  name = (uint64_t *)vm->uregs[3];
  mode = (uint64_t *)vm->uregs[4];

  fd = -1;

  cname = collmb(name, _cname, sizeof(_cname));
  if (cname == NULL)
    goto exit1;
  cmode = collmb(mode, _cmode, sizeof(_cmode));
  if (cmode == NULL)
    goto exit2;

  f = fopen(cname, cmode);
  if (f == NULL)
    goto exit3;

  i = 0;
  while (i < FD_COUNT) {
    if (fds[i] == NULL) {
      fd = i;
      fds[i] = f;
      goto exit3;
    }
    i++;
  }
  /* buffer overflow when normal exit, so close the file */
  fclose(f);

exit3:
  if (cmode != &_cmode[0])
    free(cmode);
exit2:
  if (cname != &_cname[0])
    free(cname);
exit1:
  return fd;
}

uint64_t vm_fclose(struct machine *vm) {
  int64_t fd = rc_u2i(vm->uregs[3]);
  if (fd >= FD_COUNT)
    return -1;
  if (fds[fd] == NULL)
    return -1;
  if (fclose(fds[fd]) != 0)
    return -1;
  return 0;
}

uint64_t vm_fseek(struct machine *vm) {
  int64_t fd, offset, whence;

  fd = rc_u2i(vm->uregs[3]);
  offset = rc_u2i(vm->uregs[4]);
  whence = vm->uregs[5];

  if (fd >= FD_COUNT)
    return -1;
  if (fds[fd] == NULL)
    return -1;

  if (whence == 0)
    whence = SEEK_SET;
  else if (whence == 1)
    whence = SEEK_CUR;
  else if (whence == 2)
    whence = SEEK_END;
  else
    return -1;

  return rc_i2u(fseek(fds[fd], offset, whence));
}

uint64_t vm_writetxt(struct machine *vm) {
  int64_t fd, ret;
  uint64_t *data, len, wrtcnt, transcnt;
  vmchar_t buf[BUFSIZ];
  FILE *f;
  size_t bufcnt;

  fd = rc_u2i(vm->uregs[3]);
  data = (uint64_t *)vm->uregs[4];
  len = vm->uregs[5];

  if (fd >= FD_COUNT)
    return 0;
  if (fds[fd] == NULL)
    return 0;

  f = fds[fd];
  wrtcnt = 0;

  while (wrtcnt < len) {
    bufcnt = BUFSIZ;
    transcnt = vm_mc64tomb(buf, &bufcnt, &data[wrtcnt], len - wrtcnt);
    if (transcnt < 0)
      return -1;
    ret = fwrite(buf, sizeof(char), bufcnt, f);
    if (ret != bufcnt) {
      /* ignore truncated tail utf-8 bytes, count length */
      while (ret >= 0 && (transcnt = vm_strlen_mb(buf, ret, 0)) < 0) ret--;
      return wrtcnt + transcnt;
    }
    wrtcnt += transcnt;
  }

  return wrtcnt;
}

uint64_t vm_writebytes(struct machine *vm) {
  int64_t fd;
  uint64_t *data, len;

  fd = rc_u2i(vm->uregs[3]);
  data = (uint64_t *)vm->uregs[4];
  len = vm->uregs[5];

  if (fd >= FD_COUNT)
    return -1;
  if (fds[fd] == NULL)
    return -1;

  return fwrite(data, sizeof(uint64_t), len, fds[fd]);
}

int skip_bad_char(FILE *f) {
  vmchar_t x, i;
  int r;
  do {
    x = rc_c2vc(fgetc(f));
    if (x == rc_c2vc(EOF))
      return 0;
  }while (vm_mblen(x) < 0);

  i = 0;
  /* ungetc returns EOF means error, try at most 8 times */
  while (i++ < 8 && (r = ungetc(rc_vc2c(x), f)) == EOF);
  return r == EOF ? -1 : 0;
}

uint64_t vm_readtxt(struct machine *vm) {
  int64_t fd, bufcnt, ret;
  uint64_t *dst, len, readcnt, i;
  vmchar_t buf[16];
  FILE *f;

  fd = rc_u2i(vm->uregs[3]);
  dst = (uint64_t *)vm->uregs[4];
  len = vm->uregs[5];

  if (fd >= FD_COUNT)
    return -1;
  if (fds[fd] == NULL)
    return -1;

  f = fds[fd];
  readcnt = 0;

retry:
  if (readcnt >= len)
    goto done;

  /* get first byte and the length of a character */
  if (skip_bad_char(f) < 0)
    return -1;
  buf[0] = rc_c2vc(fgetc(f));
  if (buf[0] == rc_c2vc(EOF))
    return readcnt;
  bufcnt = vm_mblen(buf[0]);

  /* collect the rest of the characters */
  for (i = 1; i < bufcnt; i++) {
    buf[i] = rc_c2vc(fgetc(f));
    if (buf[i] == rc_c2vc(EOF))
      return readcnt;
    if ((buf[i] >> 6 & 0b11) != 0b10)
      goto retry;
  }

  ret = vm_mbtoc64(&dst[readcnt], buf, sizeof(buf));
  if (ret >= 0)
    readcnt++;
  goto retry;
done:

  return readcnt;
}

uint64_t vm_readbytes(struct machine *vm) {
  int64_t fd;
  uint64_t *dst, len;

  fd = rc_u2i(vm->uregs[3]);
  dst = (uint64_t *)vm->uregs[4];
  len = vm->uregs[5];

  if (fd >= FD_COUNT)
    return -1;
  if (fds[fd] == NULL)
    return -1;

  return fread(dst, sizeof(uint64_t), len, fds[fd]);
}
