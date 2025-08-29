.PHONY: clean

vm: vm.c vm.h opcode.h switch.h
	gcc vm.c -Og -o vm

clean:
	rm vm
