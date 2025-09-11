#ifndef FILE_IO_H_
#define FILE_IO_H_

#include <stdint.h>
#include "vm.h"

int vm_file_io_init();

uint64_t vm_fopen(struct machine *vm);
uint64_t vm_fclose(struct machine *vm);
uint64_t vm_fseek(struct machine *vm);
uint64_t vm_writetxt(struct machine *vm);
uint64_t vm_writebytes(struct machine *vm);
uint64_t vm_readtxt(struct machine *vm);
uint64_t vm_readbytes(struct machine *vm);

#endif // FILE-IO_H_
