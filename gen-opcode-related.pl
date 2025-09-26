#! /usr/bin/env perl

use strict;
use warnings;

# generate opcode.h

sub ureg {}
sub freg {}
sub imm  {}
sub fimm {}
sub iimm {}

open our $header, '>', "./opcode.h"
  or die "cannot open opcode.h";

sub defop {
  my $code = shift;
  print $header "OPCODE(", $code, ")\n";
}

do "./opcode.pl" or die "unable to do opcode.el"
