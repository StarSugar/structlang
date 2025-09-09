.PHONY: clean

vm: *.o
	gcc $^ -Og -o $@

*.o: *.c
	gcc $^ -Og -c

clean:
	rm -rf vm *.o
