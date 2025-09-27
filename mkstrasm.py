#!/usr/bin/env python3

import sys;
from pathlib import Path
from argparse import ArgumentParser as Parser

def iota(s=0):
    x = s;
    while True:
        yield x;
        x += 1;

script_dir = Path(__file__).resolve().parent;
PRESERVE_SPACE = 1024

parser = Parser(prog='mkstrasm.py',
                description='Read a file, convert its contents to assembly codes\
                ,and output. The codes put utf64 string at specific location.');
parser.add_argument('input', help='input file name, - means stdin');
parser.add_argument('position', type=int,
                    help='speicific position');
parser.add_argument('-o', '--output', nargs=1, default=['-'],
                    help='output file name, - means stdout, default is -');
parser.add_argument('-e', '--encode', nargs=1, default=['utf8'],
                    help='speicific input file encoding, default is utf8, support utf8 and utf64');

args = parser.parse_args();

if args.position <= PRESERVE_SPACE:
    print("bad position, first 1024 bytes are preserved", file=sys.stderr);
    sys.exit(1);

if args.encode[0] == 'utf8':
    inf = sys.stdin if args.input == '-' else open(args.input, "r", encoding='utf-8');
    out = [ord(ch) for ch in inf.read()];
elif args.encode[0] == 'utf64':
    inf = sys.stdin.buffer if args.input == '-' else open(args.input, "rb");
    data = inf.read();
    out = [int.from_bytes(data[i:i+8].ljust(8, b'\x00'), 'little') for i in range(0, len(data), 8)];
else:
    print("unsupported encoding", file=sys.stderr);
    sys.exit(1);

outf = sys.stdout if args.output[0] == '-' else open(args.output[0], "w");
for x, p in zip(out, iota(args.position)):
    ch = chr(x) if chr(x) != "\n" else "\\n"
    print(f"uimm r3, {x}\t; character({ch})", file=outf);
    print(f"uimm r4, {p}", file=outf);
    print(f"ust r4, r3", file=outf);

inf.close();
outf.close();
