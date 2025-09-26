defop  "ULD", ureg, ureg; # ld(reg_t, ureg_t) regs[$1] = mem[regs[$2]]
defop  "FLD", freg, ureg;
defop  "UST", ureg, ureg; # st(ureg_t, reg_t) mem[regs[$1] = regs[$2]
defop  "FST", ureg, freg;
defop "UIMM", ureg,  imm; # imm(ureg_t, uimm_t/iimm_t/fimm_t) regs[$1] = $2
defop "FIMM", freg, fimm;
defop "UMOV", ureg, ureg; # mov(reg_t, reg_t) regs[$1] = regs[$2]
defop "FMOV", freg, freg;
defop  "U2F", freg, ureg; # x2y(reg_t, reg_t) regs[$1) = (type)regs[$2]
defop  "I2F", freg, ureg;
defop  "F2U", ureg, freg;
defop  "F2I", ureg, freg;
defop   "BT", iimm;       # bt(ptrdiff_t) branch, jump relatively to $1 if true
defop   "BF", iimm;       # to jump absolutely, set pc
defop  "UEQ", ureg, ureg; # eq(reg_t, reg_t) regs[$1] == regs[$2]
defop  "FEQ", freg, freg;
defop  "UGT", ureg, ureg; # gt(reg_t, reg_t) regs[$1] > regs[$2]
defop  "IGT", ureg, ureg;
defop  "FGT", freg, freg;
defop  "ULT", ureg, ureg; # lt(reg_t, reg_t) regs[$1] < regs[$2]
defop  "ILT", ureg, ureg;
defop  "FLT", freg, freg;
defop "UADD", ureg, ureg; # add(reg_t, reg_t) regs[$1] += regs[$2]
defop "FADD", freg, freg;
defop "USUB", ureg, ureg; # sub(reg_t, reg_t) regs[$1] -= regs[$2]
defop "FSUB", freg, freg;
defop "UMUL", ureg, ureg; # mul(reg_t, reg_t) regs[overflow], regs[$1] *= regs[$2]
defop "IMUL", ureg, ureg;
defop "FMUL", freg, freg; # mul(freg_t, freg_t) regs[$1] *= regs[$2]
defop "UDIV", ureg, ureg; # div(reg_t, reg_t) regs[$1], regs[overflow] (/, %)= regs[$2]
defop "IDIV", ureg, ureg;
defop "FDIV", freg, freg; # div(freg_t, freg_t) regs[$1] /= regs[$2]
defop "CALL", ureg, ureg; # call(ureg_t, ureg_t) regs[$1] = regs[$2](current_machine)
                          # well, this is actually system call
defop "STOP", ureg;       # STOP(ureg_t) stop the machine, return regs[$1]
