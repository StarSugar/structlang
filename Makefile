.PHONY: clean

CFLAGS = -Og -c
LDFLAGS = -Og
CC = gcc

vm: *.o
	$(CC) $^ $(LDFLAGS) -o $@

*.o: *.c *.h
	$(CC) *.c $(CFLAGS)

clean:
	rm -rf vm *.o *.gch *.s
