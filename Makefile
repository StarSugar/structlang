.PHONY: clean

CFLAGS = -c -g
LDFLAGS = -g
CC = cc

OBJS = file-io.o mbtoc64.o printf.o utf64.o vm.o
SRCS = file-io.c mbtoc64.c printf.c utf64.c vm.c

all: vm mbtoc64

vm: file-io.o printf.o utf64.o vm.o
	$(CC) $^ $(LDFLAGS) -o $@

mbtoc64: mbtoc64.o utf64.o
	$(CC) $^ $(LDFLAGS) -o $@

$(OBJS): $(SRCS) *.h opcode.h
	$(CC) $(filter %.c, $^) $(CFLAGS)

opcode.h:./gen-opcode-related.pl
	./gen-opcode-related.pl

clean:
	rm -rf vm mbtoc64 *.o *.gch *.s opcode.h
