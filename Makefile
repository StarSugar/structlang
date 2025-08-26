.PHONY: clean

vm: vm.c vm.h opcode.h switch.h
	cc vm.c -Og -o vm

clean:
	rm vm
