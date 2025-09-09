.PHONY: clean

vm: *.o
	gcc $^ -Og -o $@

*.o: *.c *.h
	gcc *.c -Og -c

clean:
	rm -rf vm *.o *.gch
