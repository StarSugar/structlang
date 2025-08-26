OPCODE(ULD) // ld(reg_t, ureg_t) regs[$1] = mem[regs[$2]]
OPCODE(FLD)
OPCODE(UST) // st(ureg_t, reg_t) mem[regs[$1] = regs[$2]
OPCODE(FST)
OPCODE(UIMM) // imm(ureg_t, uimm_t/iimm_t/fimm_t) regs[$1] = $2
OPCODE(FIMM)
OPCODE(UMOV) // imm(reg_t, reg_t) regs[$1] = regs[$2]
OPCODE(FMOV)
OPCODE(U2F) // x2y(reg_t, reg_t) regs[$1) = (type)regs[$2]
OPCODE(I2F)
OPCODE(F2U)
OPCODE(F2I)
OPCODE(BT) // bt(ptrdiff_t) branch, jump relatively to $1 if true
OPCODE(BF) // bf(ptrdiff_t) branch, jump relatively to $1 if false
           // for regular jump) set pc
OPCODE(UEQ) // eq(reg_t, reg_t) regs[$1] == regs[$2]
OPCODE(FEQ)
OPCODE(UGT) // gt(reg_t, reg_t) regs[$1] > regs[$2]
OPCODE(IGT)
OPCODE(FGT)
OPCODE(ULT) // lt(reg_t, reg_t) regs[$1] < regs[$2]
OPCODE(ILT)
OPCODE(FLT)
OPCODE(UADD) // add(reg_t, reg_t) regs[$1] += regs[$2]
OPCODE(FADD)
OPCODE(USUB) // sub(reg_t, reg_t) regs[$1] -= regs[$2]
OPCODE(FSUB)
OPCODE(UMUL) // mul(reg_t, reg_t) regs[overflow], regs[$1] *= regs[$2]
OPCODE(IMUL)
OPCODE(FMUL) // mul(freg_t, freg_t) regs[$1] *= regs[$2]
OPCODE(UDIV) // div(reg_t, reg_t) regs[$1], regs[overflow] (/, %)= regs[$2]
OPCODE(IDIV)
OPCODE(FDIV) // div(freg_t, freg_t) regs[$1] /= regs[$2]
OPCODE(CALL) // call(ureg_t, ureg_t) regs[$1] = regs[$2](current_machine)
OPCODE(STOP) // STOP(ureg_t) stop the machine, return regs[$1]
