from __future__ import annotations
import string
import sys
import os
import re
from dataclasses import dataclass
from typing import List, Any, Tuple

SPACES = tuple(string.whitespace)

def die(x):
    print(x, file=sys.stderr)
    sys.exit(1)

@dataclass
class Array:
    dims: List[int]
    type: Type
@dataclass
class Pointer:
    type: Type
@dataclass
class Record:
    types: List[Any]
@dataclass
class Type:
    type: Array | Pointer | Record | str
@dataclass
class Expr:
    expr: Any
@dataclass
class VarDecl:
    names: List[str]
    type: Type
@dataclass
class ConstDecl:
    names: List[str]
    type: Type
@dataclass
class FuncDecl:
    name: str
    arglist: List[Any]
    resvar: str
    resvartype: Type
    decls: List[Any]
    body: Expr
@dataclass
class ProcDecl:
    name: str
    arglist: List[Any]
    decls: List[Any]
    body: Expr
@dataclass
class TypeDecl:
    types: List[Tuple[str, Type]]
@dataclass
class Program:
    name: str
    decls: List[Any]
    body: Expr
@dataclass
class Library:
    name: str
    decls: List[Any]
    body: Expr

def parse_toplevel(s):
    line_count = 0
    idx = 0
    def check_empty():
        nonlocal s, line_count
        if s == "":
            die(f"Bad End Of File @ {line_count}")
    def eat_spaces():
        nonlocal s, line_count
        check_empty()
        while s[0] in SPACES:
            if s.startswith("\n"):
                line_count += 1
            s = s[1:];
            check_empty()
    def eat_word(ss):
        nonlocal s, line_count
        if not s.startswith(ss):
            die(f"Bad {ss}, @ {line_count}")
        line_count += ss.count("\n")
        s = s.removeprefix(ss)
    def eat_spaces_and_check_empty():
        eat_spaces(); check_empty();
    def expect_eat_spaces_and_check_empty(name):
        nonlocal line_count
        if not s.startswith(SPACES):
            die(f"{name}: no space @ {line_count}")
        eat_spaces_and_check_empty()
    def parse_id():
        nonlocal s, line_count;
        ident = re.match(r'([a-zA-Z_]+[a-zA-Z0-9_]*)', s)
        if not bool(ident):
            die(f"A identifier is expected @ {line_count}")
        ident = ident.group(0)
        s = s[len(ident):]
        return ident
    def parse_integer():
        nonlocal s, line_count;
        i = re.match(r'[1-9][0-9]*', s)
        if not bool(i):
            die(f"An INTEGER is expected @ {line_count}")
        i = i.group(0)
        s = s[len(i):]
        return int(i)
    def parse_array():
        nonlocal s
        eat_word("ARRAY")
        expect_eat_spaces_and_check_empty();
        dims = [parse_integer()];
        eat_spaces_and_check_empty();
        while s[0] == ',':
            eat_word(',')
            dims.append(parse_integer());
            eat_spaces_and_check_empty();
        eat_word("OF");
        expect_eat_spaces_and_check_empty();
        type = parse_type();
        return Array(dims, type);
    def parse_pointer():
        eat_word("POINTER")
        expect_eat_spaces_and_check_empty();
        eat_word("TO");
        expect_eat_spaces_and_check_empty();
        type = parse_type();
        return Pointer(type);
    def parse_var_const_decl(which, build):
        nonlocal s, line_count
        eat_word(which);
        expect_eat_spaces_and_check_empty(which);
        idents = [parse_id()];
        eat_spaces_and_check_empty();
        # TODO: add initialization support here
        while s[0] != ':':
            if not s.startswith(','):
                die(f"Bad {which} {line_count}")
            eat_word(',')
            eat_spaces_and_check_empty();
            idents.append(parse_id())
            eat_spaces_and_check_empty();
        eat_word(':');
        eat_spaces_and_check_empty();
        type = parse_type();
        eat_spaces_and_check_empty();
        eat_word(';');
        return build(idents, type)
    def parse_var_decl():
        return parse_var_const_decl("VAR", VarDecl);
    def parse_const_decl():
        return parse_var_const_decl("CONST", ConstDecl);
    def parse_arglist():
        nonlocal s, line_count
        eat_word('(');
        eat_spaces_and_check_empty();
        arglist = [];
        while s.startswith(('VAR', 'CONST')):
            if s.startswith('VAR'):
                arglist.append(parse_var_decl());
            if s.startswith('CONST'):
                arglist.append(parse_const_decl());
            eat_spaces_and_check_empty();
        eat_word(')');
        return arglist
    def parse_record():
        eat_word("RECORD")
        expect_eat_spaces_and_check_empty();
        return Record(parse_arglist());
    def parse_type():
        nonlocal s;
        if s.startswith("ARRAY"):
            type =  parse_array();
        elif s.startswith("POINTER"):
            type =  parse_pointer();
        elif s.startswith("RECORD"):
            type = parse_record();
        else:
            type = parse_id();
        return Type(type);
    def parse_name_arglist():
        name = parse_id();
        eat_spaces_and_check_empty();
        arglist = parse_arglist();
        return name, arglist
    def parse_expr():
        assert False, "Unimplemented parse_expr"
    def parse_decls_and_expr():
        eat_spaces_and_check_empty();
        decls = parse_decls();
        eat_spaces_and_check_empty();
        body = parse_expr();
        return decls, body
    def parse_func_decl():
        eat_word("FUNCTION");
        expect_eat_spaces_and_check_empty("FUNCTION");
        name, arglist = parse_name_arglist();
        eat_spaces_and_check_empty();
        resvar = parse_id();
        eat_spaces_and_check_empty();
        eat_word(":");
        resvartype = parse_type();
        eat_spaces_and_check_empty();
        eat_word(";");
        decls, expr = parse_decls_and_expr();
        return FuncDecl(name, arglist, resvar, resvartype, decls, expr);
    def parse_proc_decl():
        eat_word("PROCEDURE");
        expect_eat_spaces_and_check_empty("PROCEDURE");
        name, arglist = parse_name_arglist();
        eat_word(";");
        decls, expr = parse_decls_and_expr();
        return ProcDecl(name, arglist, decls, expr);
    def parse_a_type_decl():
        name = parse_id();
        eat_spaces_and_check_empty();
        eat_word("=");
        eat_spaces_and_check_empty();
        type = parse_type();
        eat_spaces_and_check_empty();
        return (name, type)
    def parse_type_decl():
        nonlocal s, line_count;
        eat_word("TYPE");
        expect_eat_spaces_and_check_empty("TYPE");
        typedecls = [parse_a_type_decl()];
        eat_spaces_and_check_empty();
        while s[0] == ',':
            eat_word(',');
            typedecls.append(parse_a_type_decl());
            eat_spaces_and_check_empty();
        eat_word(';');
        return TypeDecl(typedecls);
    def parse_decls():
        nonlocal s;
        eat_spaces_and_check_empty();
        decls = []
        while s.startswith(('VAR', 'CONST', 'FUNCTION', 'PROCEDURE', 'TYPE', 'LIBRARY')):
            if s.startswith('VAR'):
                decls.append(parse_var_decl())
            elif s.startswith('CONST'):
                decls.append(parse_const_decl())
            elif s.startswith('FUNCTION'):
                decls.append(parse_func_decl())
            elif s.startswith('PROCEDURE'):
                decls.append(parse_proc_decl())
            elif s.startswith('TYPE'):
                decls.append(parse_type_decl())
            elif s.startswith('LIBRARY'):
                decls.append(parse_library())
            eat_spaces_and_check_empty();
        return decls
    def parse_lib_program(which, build):
        eat_word(which);
        expect_eat_spaces_and_check_empty(which)
        name = parse_id();
        eat_spaces_and_check_empty();
        eat_word(';');
        decls, body = parse_decls_and_expr();
        return build(name, decls, body);
    def parse_program():
        return parse_lib_program("PROGRAM", Program)
    def parse_library():
        return parse_lib_program("LIBRARY", Library)
    eat_spaces()
    if s.startswith("PROGRAM"):
        return parse_program();
    if s.startswith("LIBRARY"):
        return parse_library();
    die(f"Bad Toplevel @ {line_count}");
