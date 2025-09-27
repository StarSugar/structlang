  ;; string
uimm r3, 72	; character(H)
uimm r4, 8000
ust r4, r3
uimm r3, 101	; character(e)
uimm r4, 8001
ust r4, r3
uimm r3, 108	; character(l)
uimm r4, 8002
ust r4, r3
uimm r3, 108	; character(l)
uimm r4, 8003
ust r4, r3
uimm r3, 111	; character(o)
uimm r4, 8004
ust r4, r3
uimm r3, 32	; character( )
uimm r4, 8005
ust r4, r3
uimm r3, 119	; character(w)
uimm r4, 8006
ust r4, r3
uimm r3, 111	; character(o)
uimm r4, 8007
ust r4, r3
uimm r3, 114	; character(r)
uimm r4, 8008
ust r4, r3
uimm r3, 108	; character(l)
uimm r4, 8009
ust r4, r3
uimm r3, 100	; character(d)
uimm r4, 8010
ust r4, r3
uimm r3, 33	; character(!)
uimm r4, 8011
ust r4, r3
uimm r3, 10	; character(\n)
uimm r4, 8012
ust r4, r3
uimm r3, 37	; character(%)
uimm r4, 8013
ust r4, r3
uimm r3, 100	; character(d)
uimm r4, 8014
ust r4, r3
uimm r3, 10	; character(\n)
uimm r4, 8015
ust r4, r3
uimm r3, 37	; character(%)
uimm r4, 8016
ust r4, r3
uimm r3, 102	; character(f)
uimm r4, 8017
ust r4, r3
uimm r3, 10	; character(\n)
uimm r4, 8018
ust r4, r3
uimm r3, 37	; character(%)
uimm r4, 8019
ust r4, r3
uimm r3, 99	; character(c)
uimm r4, 8020
ust r4, r3
uimm r3, 10	; character(\n)
uimm r4, 8021
ust r4, r3
uimm r3, 37	; character(%)
uimm r4, 8022
ust r4, r3
uimm r3, 120	; character(x)
uimm r4, 8023
ust r4, r3
uimm r3, 10	; character(\n)
uimm r4, 8024
ust r4, r3
uimm r3, 89	; character(Y)
uimm r4, 8025
ust r4, r3
uimm r3, 101	; character(e)
uimm r4, 8026
ust r4, r3
uimm r3, 115	; character(s)
uimm r4, 8027
ust r4, r3
uimm r3, 33	; character(!)
uimm r4, 8028
ust r4, r3
uimm r3, 10	; character(\n)
uimm r4, 8029
ust r4, r3
  ;; printf
uimm r3, 8000
uimm r4, 3
uimm r7, 8
uadd r4, r7
fimm x0, 10.8
fimm x1, 25.3
fmul x0, x1
uimm r5, 65
uimm r6, 65
uimm r7, 1
call r3, r7
stop r3
