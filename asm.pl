#! /usr/bin/perl

use bignum;

# general registers, or unsigned integer registers
our @uregs = qw(r0 r1 r2 r3 r4 r5 r6 r7);
our %uregs = map {$_ => $_} @uregs;
our %special_regs = (
  pc       => 'r0',
  base     => 'r1',
  frame    => 'r2',
  overflow => 'r3',
  cond     => 'r4'
);
%uregs = (%uregs, %special_regs);

our @fregs = qw(x0 x1 x2 x3 x4 x5 x6 x7);
our %fregs = map {$_ => $_} @fregs;

our $line_count = 0;

sub legal_uint_p {
  my $x = shift;
  $x =~ /^(\d+)$/ &&
      0 <= $x && $x <= 2**64-1;
}

sub legal_int_p {
  my $x = shift;
  $x =~ /^([+-]?\d+)$/ &&
      -(2**63) <= $x && $x <= 2**63 - 1;
}

sub legal_double_p {
  my $x = shift;
  $x =~ /^[+-]?\d*\.\d+([eE][+-]?\d+)?$/ ||
      $x =~ /^[+-]?\d+[Ee][+-]?\d+$/;
}

sub reg {
  my $regs = shift;
  my $regname = shift;
  exists $regs->{$regname} or die "bad register form \@ $line_count";
  my $r = $regs->{$regname};
  my $n = +substr($r, 1);
  print pack("Q<", $n);
}

sub ureg { sub { reg \%uregs, shift; } }

sub freg { sub { reg \%fregs, shift; } }

sub iimm {
  sub {
    my $x = shift;
    legal_int_p $x or die "bad integer \@ $line_count";
    print pack("Q<", $x >= 0 ? +$x : $x + 2**64);
  }
}

sub uimm {
  sub {
    my $x = shift;
    legal_uint_p $x or die "bad number \@ $line_count";
    print pack("Q<", +$x);
  }
}

sub imm {
  sub {
    my $x = shift;
    legal_int_p $x || legal_uint_p $x or die "bad integer \@ $line_count";
    print pack("Q<", $x >= 0 ? +$x : $x + 2**64);
  }
}

sub fimm {
  sub {
    my $x = shift;
    legal_double_p $x or die "bad real number \@ $line_count";
    print pack("d<", +$x);
  }
}

our %operations = ();

sub defop {
  my $name = shift;
  my $id = shift;
  my @operands = @_;
  $operations{$name} = {
    name => $name,
    id => $id,
    operands=>\@operands
  };
}

# for other details, see opcode.h
defop  "ULD",  0, ureg, ureg;
defop  "FLD",  1, freg, ureg;
defop  "UST",  2, ureg, ureg;
defop  "FST",  3, ureg, freg;
defop "UIMM",  4, ureg,  imm;
defop "FIMM",  5, freg, fimm;
defop "UMOV",  6, ureg, ureg;
defop "FMOV",  7, freg, freg;
defop  "U2F",  8, freg, ureg;
defop  "I2F",  9, freg, ureg;
defop  "F2U", 10, ureg, freg;
defop  "F2I", 11, ureg, freg;
defop   "BT", 12, iimm;
defop   "BF", 13, iimm;
defop  "UEQ", 14, ureg, ureg;
defop  "FEQ", 15, freg, freg;
defop  "UGT", 16, ureg, ureg;
defop  "IGT", 17, ureg, ureg;
defop  "FGT", 18, freg, freg;
defop  "ULT", 19, ureg, ureg;
defop  "ILT", 20, ureg, ureg;
defop  "FLT", 21, freg, freg;
defop "UADD", 22, ureg, ureg;
defop "FADD", 23, freg, freg;
defop "USUB", 24, ureg, ureg;
defop "FSUB", 25, freg, freg;
defop "UMUL", 26, ureg, ureg;
defop "IMUL", 27, ureg, ureg;
defop "FMUL", 28, freg, freg;
defop "UDIV", 29, ureg, ureg;
defop "IDIV", 30, ureg, ureg;
defop "FDIV", 31, freg, freg;
defop "CALL", 32, ureg, ureg;
defop "STOP", 33, ureg;

sub trans_a_line {
  my $line = @_ ? $_[0] : $_;
  return if $line =~ /^ \s*(;.*)?$/;
  chomp $line;
  $line = lc($line);

  my $re = qr/
    ^
    (\w+)                       # operator
    \s*([\w+-.]+)               # first operand
    (?=(?: \s*,\s*[\w+-.]+)*    # check the other operands and comment syntax
       (?: \s*;.*$              # and check the comment
         | \s*$))               # and if no comment, it should be end of line
    ([\s\w,+-.]*)               # the other operands
    (?:;.*)?                    # optional comment
    $
  /x;

  my ($op, $rand1, $rands) = $line =~ $re
      or die "Bad Assembly Form \@ $line_count";
  $op = uc($op);
  exists $operations{$op}
      or die "No Such Operation $op \@ $line_count";

  my @rands = ($rand1, grep { length } split(/\s*,\s*|\s+/, $rands));

  my $i = 0;
  foreach my $f (@{ $operations{$op}->{operands} }) {
    $f->($rands[$i++]);
  }
}

binmode STDOUT, ':raw';
while (<>) {
  $line_count++;
  trans_a_line;
}
