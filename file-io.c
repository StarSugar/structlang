#include "file-io.h"

#include <stddef.h>
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include "vm.h"
#include "reinterpret_cast.h"
#include "utf64.h"

const size_t FD_COUNT = 2048;

FILE *fds[FD_COUNT];

int vm_file_io_init() {
  int i;

  fds[0] = stdin;
  fds[1] = stdout;
  fds[2] = stderr;

  i = 0;
  while (i < FD_COUNT) {
    fds[i] = NULL;
  }

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
  size_t cnt, off;
  cur = &head;
  vmchar_t *buf;

  vmcharplist_init(&head);
  cnt = 0;

  for (;;) {
    ret = vm_strc64tomb(cur->buf, str, sizeof(cur->buf));
    if (ret < 0)
      goto error;
    str += ret;
    cur->cnt = ret;
    cnt += ret;
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

  cname = collmb(name, _cname, BUFSIZ);
  if (cname == NULL)
    goto exit1;
  cmode = collmb(mode, _cmode, BUFSIZ);
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
  uint64_t fd = vm->uregs[3];
  if (fds[fd] == NULL)
    return -1;
  if (fclose(fds[fd]) != 0)
    return -1;
  return 0;
}
