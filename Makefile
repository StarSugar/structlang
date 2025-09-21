.PHONY: clean

CFLAGS = -Og -c
LDFLAGS = -Og
CC = gcc

all: vm mbtoc64

vm: file-io.o printf.o utf64.o vm.o
	$(CC) $^ $(LDFLAGS) -o $@

mbtoc64: mbtoc64.c utf64.o
	$(CC) $^ $(LDFLAGS) -o $@

*.o: *.c *.h
	$(CC) *.c $(CFLAGS)

clean:
	rm -rf vm mbtoc64 *.o *.gch *.s
