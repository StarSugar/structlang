#! /usr/bin/env python
from argparse import ArgumentParser as Parser;
import sys
import os
from pathlib import Path
from subprocess import Popen, PIPE
import struct

UIMM = struct.pack('<Q', 4)
REG3 = struct.pack('<Q', 3)
UST = struct.pack('<Q', 2)
PRESERVE_SPACE = 1000

script_dir = Path(__file__).resolve().parent

parser = Parser(prog='mkstrimg.py',
                description='read a file, convert it to utf64 code image, and output');
parser.add_argument('input', help='input file name, - means stdout');
parser.add_argument('position', type=int,
                    help='speicific position of the generated code image');
parser.add_argument('-o', '--output', nargs=1, default=['-'],
                    help='output file name, - means stdout, default is -');
parser.add_argument('-e', '--encode', nargs=1, default=['utf8'],
                    help='speicific input file encoding, default is utf8, support utf8 and utf64')

args = parser.parse_args();

def run_mbtoc64_and_pipe_to_a_new_self():
    global args, script_dir, fin;
    cmd_mbtoc64 = [script_dir / 'mbtoc64'];
    cmd_new_self = [sys.executable, __file__,
                    '-o', args.output[0],
                    '-e', 'utf64',
                    '-',
                    str(args.position)];
    new_self = Popen(cmd_new_self, stdin=PIPE);
    mbtoc64 = Popen(cmd_mbtoc64, stdin=PIPE, stdout=new_self.stdin);
    new_self.stdin.close();

    mbtoc64.stdin.write(fin.read())
    fin.close();
    mbtoc64.stdin.close();

    mbtoc64.wait();
    new_self.wait();

def iota(x=0):
    i = x;
    while True:
        yield i;
        i += 1;

def mkstrimg():
    global fin, fout, args, UST, UIMM, REG3, PRESERVE_SPACE;
    data = fin.read();
    for i, p in zip(range(0, len(data), 8), iota(args.position - PRESERVE_SPACE)):
        fout.write(UIMM);
        fout.write(REG3);
        fout.write(data[i:i+8].ljust(8, b'\x00'));
        fout.write(UST);
        fout.write(struct.pack('<Q', p));
        fout.write(REG3);
    fin.close();
    fout.close();

fin = sys.stdin.buffer if args.input == '-' else open(args.input, 'rb')

if args.encode[0] == 'utf8':
    if not Path(script_dir / 'mbtoc64').is_file():
        print('You need to `make` firstly to convert utf8 to utf64', file=sys.stderr);
        sys.exit(1);
    run_mbtoc64_and_pipe_to_a_new_self();
    sys.exit(0);
elif args.encode[0] != 'utf64':
    print('Unsupported encoding', args.encode[0], file=sys.stderr);
    sys.exit(1);
elif args.position < PRESERVE_SPACE:
    print('Bad position, position must be greater than or equal to', PRESERVE_SPACE, file=sys.stderr);
    sys.exit(1);
else:
    fout = sys.stdout.buffer if args.output[0] == '-' else open(args.output[0], 'wb')
    mkstrimg();
    sys.exit(0);
