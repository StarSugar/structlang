#! /usr/bin/env python

from __future__ import annotations
import string
import sys
import os
import re
from dataclasses import dataclass
from typing import List, Any, Tuple
from functools import reduce

def die(x):
    print(x, file=sys.stderr)
    sys.exit(1)

SPACES = tuple(string.whitespace)

@dataclass
class Syntax:
    line: int

@dataclass
class IDInLib(Syntax):
    ids: List[str]

@dataclass
class Array(Syntax):
    dims: List[IntLit]
    type: Type

@dataclass
class Pointer(Syntax):
    type: Type

@dataclass
class Record(Syntax):
    types: List[VarDecl | ConstVarDecl]

@dataclass
class Type(Syntax):
    type: Array | Pointer | Record | IDInLib | ID

@dataclass
class ID(Syntax):
    id: str

@dataclass
class IntLit(Syntax):
    val: int

@dataclass
class RealLit(Syntax):
    val: float

@dataclass
class StrLit(Syntax):
    val: str

@dataclass
class ArrAccessExpr(Syntax):
    base: Expr
    idx: Expr

@dataclass
class CallExpr(Syntax):
    func: Expr
    args: List[Expr]

@dataclass
class RecordAccessExpr(Syntax):
    rcd: Expr
    id: ID

@dataclass
class OppoExpr(Syntax):
    expr: Expr

@dataclass
class RefExpr(Syntax):
    expr: Expr

@dataclass
class NotExpr(Syntax):
    expr: Expr

@dataclass
class DerefExpr(Syntax):
    expr: Expr

@dataclass
class PowerExpr(Syntax):
    x: Expr
    y: Expr

@dataclass
class ProductExpr(Syntax):
    x: Expr
    y: Expr

@dataclass
class QuotientExpr(Syntax):
    x: Expr
    y: Expr

@dataclass
class SumExpr(Syntax):
    x: Expr
    y: Expr

@dataclass
class DiffExpr(Syntax):
    x: Expr
    y: Expr

@dataclass
class GreatExpr(Syntax):
    x: Expr
    y: Expr

@dataclass
class LessExpr(Syntax):
    x: Expr
    y: Expr

@dataclass
class GreatEqualExpr(Syntax):
    x: Expr
    y: Expr

@dataclass
class LessEqualExpr(Syntax):
    x: Expr
    y: Expr

@dataclass
class EqualExpr(Syntax):
    x: Expr
    y: Expr

@dataclass
class NotEqualExpr(Syntax):
    x: Expr
    y: Expr

@dataclass
class IntersecExpr(Syntax):
    x: Expr
    y: Expr

@dataclass
class UnionExpr(Syntax):
    x: Expr
    y: Expr

@dataclass
class IfExpr(Syntax):
    cond: Expr
    then: Expr
    els : Expr


@dataclass
class Expr(Syntax):
    expr: \
        ArrAccessExpr | \
        CallExpr | \
        RecordAccessExpr | \
        OppoExpr | \
        RefExpr | \
        NotExpr | \
        DerefExpr | \
        PowerExpr | \
        ProductExpr | \
        QuotientExpr | \
        SumExpr | \
        DiffExpr | \
        GreatExpr | \
        LessExpr | \
        GreatEqualExpr | \
        LessEqualExpr | \
        EqualExpr | \
        NotEqualExpr | \
        IntersecExpr | \
        UnionExpr | \
        IDInLib | \
        ID | \
        IntLit | \
        RealLit | \
        StrLit

@dataclass
class LabelSttmt(Syntax):
    label: str
    sttmt: Statement

@dataclass
class BeginSttmt(Syntax):
    sttmts: List[Statement]

@dataclass
class BeginWhileSttmt(Syntax):
    sttmts: List[Statement]
    cond: Expr

@dataclass
class BeginUntilSttmt(Syntax):
    sttmts: List[Statement]
    cond: Expr

@dataclass
class WhileSttmt(Syntax):
    cond: Expr
    body: Statement

@dataclass
class UntilSttmt(Syntax):
    cond: Expr
    body: Statement

@dataclass
class LValue(Syntax):
    expr: Expr

@dataclass
class Assignment(Syntax):
    names: List[LValue]
    vals:  List[Expr]

@dataclass
class AssignForClause(Syntax):
    assign: Assignment

@dataclass
class IterateByForClause(Syntax):
    var:  LValue
    expr: Expr

@dataclass
class IterateAsForClause(Syntax):
    var:  LValue
    expr: Expr

@dataclass
class ThenForClause(Syntax):
    assign: Assignment
    thens: List[Expr]

@dataclass
class StepForClause(Syntax):
    assign: Assignment
    steps: List[Expr]

@dataclass
class StepToForClause(Syntax):
    assign: Assignment
    steps: List[Expr]
    tos: List[Expr]

@dataclass
class ToForClause(Syntax):
    assign: Assignment
    tos: List[Expr]

@dataclass
class UntilForClause(Syntax):
    cond: Expr

@dataclass
class WhileForClause(Syntax):
    cond: Expr

@dataclass
class ForSttmt(Syntax):
    clauses: List[
        AssignForClause |
        IterateAsForClause |
        IterateByForClause |
        StepForClause |
        StepToForClause |
        ToForClause |
        UntilForClause |
        WhileForClause
    ]
    body: Expr

@dataclass
class IfSttmt(Syntax):
    cond: Expr
    Then: Expr

@dataclass
class IfElseSttmt(Syntax):
    cond: Expr
    Then: Expr
    els : Expr

@dataclass
class GoToSttmt(Syntax):
    id: ID | IDInLib

@dataclass
class BreakSttmt(Syntax):
    pass

@dataclass
class ContinueSttmt(Syntax):
    pass

@dataclass
class VoidSttmt(Syntax):
    pass

@dataclass
class ExprSttmt(Syntax):
    expr: Expr

@dataclass
class AssignmentSttmt(Syntax):
    expr: Assignment

@dataclass
class Statement(Syntax):
    statement: \
        LabelSttmt | \
        BeginSttmt | \
        BeginWhileSttmt | \
        BeginUntilSttmt | \
        WhileSttmt | \
        UntilSttmt

@dataclass
class VarDecl(Syntax):
    names: List[ID]
    type: Type

@dataclass
class ConstVarDecl(Syntax):
    names: List[ID]
    type: Type

@dataclass
class ConstDecl(Syntax):
    binds: List[Tuple[ID, Expr]]

@dataclass
class ArgList(Syntax):
    arglist: List[VarDecl | ConstVarDecl]

@dataclass
class FuncDecl(Syntax):
    name: ID
    arglist: ArgList | None
    resvar: ID
    resvartype: Type
    decls: List[Any]
    body: Statement

@dataclass
class ProcDecl(Syntax):
    name: ID
    arglist: ArgList | None
    decls: List[Any]
    body: Statement

@dataclass
class TypeDecl(Syntax):
    types: List[Tuple[ID, Type]]

@dataclass
class Program(Syntax):
    name: ID
    decls: List[Any]
    body: Statement

@dataclass
class Library(Syntax):
    name: ID
    decls: List[Any]
    body: Statement

def parse_toplevel(s):
    s += ' .';
    line_count = 0;
    idx = 0;
    def check_empty():
        nonlocal s, line_count
        if s == "":
            die(f"Bad End Of File @ {line_count}")
    def spacep():
        nonlocal s;
        global SPACES;
        check_empty()
        return s[0] in SPACES
    def eat_spaces():
        nonlocal s, line_count
        global SPACES;
        check_empty()
        while s[0] in SPACES:
            if s.startswith("\n"):
                line_count += 1
            s = s[1:];
            check_empty()
    def eat_word(ss):
        nonlocal s, line_count
        if not s.startswith(ss):
            die(f"Bad Syntax {ss}, @ {line_count}")
        line_count += ss.count("\n")
        s = s.removeprefix(ss)
    def eat_spaces_and_check_empty():
        eat_spaces(); check_empty();
    def expect_eat_spaces_and_check_empty(name):
        nonlocal line_count
        if not s.startswith(SPACES):
            die(f"{name}: No Space @ {line_count}")
        eat_spaces_and_check_empty()
    def expect_eat_spaces_or_smei_and_check_empty(name):
        nonlocal line_count, s;
        xs = list(SPACES);
        xs.append(';');
        check_empty();
        if not s.startswith(tuple(xs)):
            die(f"{name}: No Space @ {line_count}")
        while s[0] in xs:
            if s.startswith("\n"):
                line_count += 1;
            s = s[1:];
            check_empty();
    def idp():
        nonlocal s;
        return bool(re.match(r'([a-zA-Z_][a-zA-Z0-9_]*)', s));
    def parse_id():
        nonlocal s, line_count;
        lc = line_count;
        ident = re.match(r'([a-zA-Z_][a-zA-Z0-9_]*)', s)
        if not bool(ident):
            die(f"A identifier is expected @ {line_count}")
        ident = ident.group(0)
        s = s[len(ident):]
        return ID(lc, ident)
    def match_integer():
        nonlocal s;
        if i := re.match(r'0+|[1-9][0-9]*', s):
            return i.group(0);
    def parse_integer():
        nonlocal s, line_count;
        lc = line_count;
        i = re.match(r'0+|[1-9][0-9]*', s);
        if not bool(i):
            die(f"An INTEGER is expected @ {line_count}");
        i = i.group(0);
        s = s[len(i):];
        return IntLit(lc, int(i));
    def parse_array():
        nonlocal s, line_count
        lc = line_count;
        eat_word("ARRAY")
        expect_eat_spaces_and_check_empty("ARRAY");
        dims = [parse_integer()];
        eat_spaces_and_check_empty();
        while s[0] == ',':
            eat_word(',')
            eat_spaces_and_check_empty();
            dims.append(parse_integer());
            eat_spaces_and_check_empty();
        eat_word("OF");
        expect_eat_spaces_and_check_empty("ARRAY");
        type = parse_type();
        return Array(lc, dims, type);
    def parse_pointer():
        nonlocal line_count
        lc = line_count;
        eat_word("POINTER")
        expect_eat_spaces_and_check_empty("POINTER");
        eat_word("TO");
        expect_eat_spaces_and_check_empty("POINTER");
        type = parse_type();
        return Pointer(lc, type);
    def parse_var_const_decl(which, build):
        nonlocal s, line_count
        lc = line_count;
        eat_word(which);
        expect_eat_spaces_and_check_empty(which);
        idents = [parse_id()];
        eat_spaces_and_check_empty();
        while s[0] == ',':
            eat_word(',')
            eat_spaces_and_check_empty();
            idents.append(parse_id())
            eat_spaces_and_check_empty();
        eat_word(':');
        eat_spaces_and_check_empty();
        type = parse_type();
        eat_spaces_and_check_empty();
        eat_word(';');
        return build(lc, idents, type)
    def parse_var_decl():
        return parse_var_const_decl("VAR", VarDecl);
    def parse_const_var_decl():
        return parse_var_const_decl("CONST", ConstVarDecl);
    def parse_a_bind(parse_val):
        name = parse_id();
        eat_spaces_and_check_empty();
        eat_word("=");
        eat_spaces_and_check_empty();
        val = parse_val();
        eat_spaces_and_check_empty();
        return (name, val)
    def parse_const_decl():
        nonlocal s, line_count
        lc = line_count
        eat_word("CONST");
        expect_eat_spaces_and_check_empty("CONST");
        binds = [parse_a_bind(parse_expr)];
        eat_spaces_and_check_empty();
        while s[0] == ',':
            eat_word(',');
            eat_spaces_and_check_empty();
            binds.append(parse_a_bind(parse_expr));
            eat_spaces_and_check_empty();
        eat_word(';');
        return ConstDecl(lc, binds)
    def parse_arglist():
        nonlocal s, line_count
        lc = line_count;
        eat_word('(');
        eat_spaces_and_check_empty();
        arglist = [];
        while s.startswith(('VAR', 'CONST')):
            if s.startswith('VAR'):
                arglist.append(parse_var_decl());
            if s.startswith('CONST'):
                arglist.append(parse_const_var_decl());
            eat_spaces_and_check_empty();
        eat_word(')');
        return ArgList(lc, arglist);
    def parse_record():
        nonlocal line_count
        lc = line_count;
        eat_word("RECORD")
        eat_spaces_and_check_empty();
        return Record(lc, parse_arglist().arglist);
    def match_id_in_lib():
        nonlocal s;
        return re.match(r'[A-Za-z_][A-Za-z0-9_]*(\.[A-Za-z_][A-Za-z0-9_]*)+', s)
    def id_in_lib_p():
        return bool(match_id_in_lib());
    def parse_id_in_lib():
        nonlocal s, line_count;
        lc = line_count;
        ids = match_id_in_lib().group(0);
        s = s[len(ids):];
        return IDInLib(lc, ids.split('.'))
    def parse_type():
        nonlocal s, line_count;
        lc = line_count;
        if s.startswith("ARRAY"):
            type =  parse_array();
        elif s.startswith("POINTER"):
            type =  parse_pointer();
        elif s.startswith("RECORD"):
            type = parse_record();
        elif id_in_lib_p():
            type = parse_id_in_lib();
        else:
            type = parse_id();
        return Type(lc, type);
    def match_label():
        nonlocal s;
        return re.match(r'[A-Za-z_][A-Za-z0-9_]*:', s);
    def labelp():
        nonlocal s;
        return bool(match_label());
    def parse_label():
        nonlocal s, line_count;
        lc = line_count;
        label = match_label().group(0);
        s = s[len(label):];
        label = label[:-1];
        eat_spaces_and_check_empty();
        sttmt = parse_statement();
        return LabelSttmt(lc, label, sttmt);
    def parse_begin():
        nonlocal s, line_count;
        lc = line_count;
        eat_word('BEGIN');
        eat_spaces_and_check_empty();
        sttmts = [parse_statement()];
        eat_spaces_and_check_empty();
        while not s.startswith('END'):
            sttmts.append(parse_statement())
            eat_spaces_and_check_empty();
        eat_word('END');
        eat_spaces_and_check_empty();
        if s.startswith(';'):
            eat_word(';');
            return BeginSttmt(lc, sttmts);
        elif s.startswith('WHILE'):
            eat_word('WHILE');
            expect_eat_spaces_and_check_empty("BEGIN ... END WHILE ...;");
            cond = parse_expr();
            expect_eat_spaces_or_smei_and_check_empty();
            return BeginWhileSttmt(lc, sttmts, cond);
        elif s.startswith('UNTIL'):
            eat_word('UNTIL');
            expect_eat_spaces_and_check_empty('BEGIN ... END UNTIL ...;');
            cond = parse_expr();
            expect_eat_spaces_or_smei_and_check_empty();
            return BeginUntilSttmt(lc, sttmts, cond);
        else:
            die(f"Bad BEGIN END @ {line_count}");
    def parse_simple_loop(name, build):
        nonlocal line_count;
        lc = line_count;
        eat_word(name);
        eat_spaces_and_check_empty()
        cond = parse_expr();
        eat_spaces_and_check_empty()
        eat_word("DO")
        eat_spaces_and_check_empty()
        body = parse_statement();
        eat_spaces_and_check_empty();
        eat_word(';');
        return build(lc, cond, body);
    def parse_while():
        return parse_simple_loop('WHILE', WhileSttmt);
    def parse_until():
        return parse_simple_loop('UNTIL', UntilSttmt);
    def parse_expr():
        nonlocal s, line_count;
        def parse_binop(x, parse_next_level, ops):
            nonlocal s, line_count;
            lc = line_count;
            if not s.startswith(tuple(lit for lit, _ in ops)):
                return x;
            for lit, build in ops:
                if s[0] == lit:
                    eat_word(lit);
                    eat_spaces_and_check_empty();
                    y = parse_next_level();
                    res = build(lc, x, y);
                    break;
            eat_spaces_and_check_empty();
            return parse_binop(Expr(lc, res), parse_next_level, ops);
        def parse_level_0():
            nonlocal s, line_count;
            if not s.startswith("IF"):
                return parse_level_1();
            lc = line_count;
            eat_word("IF");
            expect_eat_spaces_and_check_empty("IF expression");
            cond = parse_level_0();
            expect_eat_spaces_and_check_empty("IF expression");
            eat_word("THEN");
            expect_eat_spaces_and_check_empty("IF expression");
            then = parse_level_0();
            expect_eat_spaces_and_check_empty("IF expression");
            eat_word("ELSE");
            expect_eat_spaces_and_check_empty("IF expression");
            els  = parse_level_0();
            return IfExpr(lc, cond, then, els);
        def parse_level_1():
            parse_right = lambda x: parse_binop(
                x, parse_level_2, (('|', UnionExpr),)
            );
            x = parse_level_2();
            eat_spaces_and_check_empty();
            return parse_right(x);
        def parse_level_2():
            parse_right = lambda x: parse_binop(
                x, parse_level_3, (('&', IntersecExpr),)
            );
            x = parse_level_3();
            eat_spaces_and_check_empty();
            return parse_right(x);
        def parse_level_3():
            parse_right = lambda x: parse_binop(
                x, parse_level_4, (('=', EqualExpr), ('<>', NotEqualExpr))
            );
            x = parse_level_4();
            eat_spaces_and_check_empty();
            return parse_right(x);
        def parse_level_4():
            parse_right = lambda x: parse_binop(
                x, parse_level_5,
                (('>', GreatExpr), ('<', LessExpr),
                 ('>=', GreatEqualExpr), ('<=', LessEqualExpr))
            );
            x = parse_level_5();
            eat_spaces_and_check_empty();
            return parse_right(x);
        def parse_level_5():
            parse_right = lambda x: parse_binop(
                x, parse_level_6, (('+', SumExpr), ('-', DiffExpr))
            );
            x = parse_level_6();
            eat_spaces_and_check_empty();
            return parse_right(x);
        def parse_level_6():
            parse_right = lambda x: parse_binop(
                x, parse_level_7, (('*', ProductExpr), ('/', QuotientExpr))
            );
            x = parse_level_7();
            eat_spaces_and_check_empty();
            return parse_right(x);
        def parse_level_7():
            parse_right = lambda x: parse_binop(
                x, parse_level_8, (('^', PowerExpr),)
            );
            x = parse_level_8();
            eat_spaces_and_check_empty();
            return parse_right(x);
        def parse_level_8():
            nonlocal s, line_count;
            lc = line_count;
            if s[0] == '-':
                eat_word('-');
                resf = OppoExpr;
            elif s[0] == '@':
                eat_word('@');
                resf = RefExpr;
            elif s[0] == '~':
                eat_word('~');
                resf = NotExpr;
            elif s.startswith('!'):
                eat_word('!');
                resf = DerefExpr;
            else:
                x = parse_level_9();
                return x;
            eat_spaces_and_check_empty();
            return Expr(lc, resf(lc, parse_level_8()));
        def parse_level_9():
            nonlocal s;
            def parse_right(x):
                nonlocal s, line_count;
                lc = line_count;
                if not s.startswith(('[', '(', '#')):
                    return x;
                if s[0] == '[':
                    eat_word('[')
                    eat_spaces_and_check_empty();
                    y = parse_level_0();
                    eat_spaces_and_check_empty();
                    eat_word(']');
                    res = ArrAccessExpr(lc, x, y);
                elif s[0] == '(':
                    eat_word('(')
                    eat_spaces_and_check_empty();
                    args = []
                    if s[0] == ')':
                        eat_word(')');
                        res = CallExpr(lc, x, args);
                    else:
                        args = [parse_level_0()];
                        eat_spaces_and_check_empty();
                        while s[0] != ')':
                            eat_word(',');
                            eat_spaces_and_check_empty();
                            args.append(parse_level_0());
                            eat_spaces_and_check_empty();
                        eat_word(')');
                        res = CallExpr(lc, x, args);
                elif s[0] == '#':
                    eat_word('#')
                    id = parse_id();
                    res = RecordAccessExpr(lc, x, id);
                eat_spaces_and_check_empty();
                return parse_right(Expr(lc, res));
            x = parse_level_10();
            eat_spaces_and_check_empty();
            return parse_right(x);
        def match_real():
            nonlocal s;
            if res := re.match(r'\d*\.\d+([eE][+-]?\d+)?', s):
                return res.group(0);
            if res := re.match(r'\d+[Ee][+-]?\d+', s):
                return res.group(0);
            return False;
        def match_str():
            nonlocal s;
            if res := re.match(r'"((?:[^"]|\\.)*)"', s):
                return res.group(1);
            return False;
        def parse_level_10():
            nonlocal s, line_count;
            lc = line_count;
            if s[0] == '(':
                eat_word('(');
                eat_spaces_and_check_empty();
                res = parse_level_1();
                eat_spaces_and_check_empty();
                eat_word(')');
                return res;
            elif match_str():
                x = match_str();
                s = s[len(x)+2:];
                return Expr(lc, StrLit(lc, re.sub(r'\\(.)', r'\1', x)));
            elif match_real():
                x = match_real();
                s = s[len(x):];
                return Expr(lc, RealLit(lc, float(x)));
            elif match_integer():
                return Expr(lc, parse_integer());
            elif id_in_lib_p():
                return Expr(lc, parse_id_in_lib());
            else:
                return Expr(lc, parse_id());
        return parse_level_0();
    def lvaluep(x):
        return type(x) in (ID, IDInLib, DerefExpr, ArrAccessExpr, RecordAccessExpr);
    def parse_lvalue():
        nonlocal line_count;
        lc = line_count;
        expr = parse_expr();
        if lvaluep(expr.expr):
            return LValue(lc, expr);
        die(f"Expected a lvalue @ {lc}")
    def parse_assignment(names=[]):
        nonlocal line_count, s;
        lc = line_count;
        if names == []:
            names = [parse_lvalue()];
        eat_spaces_and_check_empty();
        while s.startswith(','):
            eat_word(',');
            eat_spaces_and_check_empty();
            names.append(parse_lvalue());
            eat_spaces_and_check_empty();
        eat_word(':=');
        eat_spaces_and_check_empty();
        vals = [parse_expr()];
        eat_spaces_and_check_empty();
        for _ in range(len(names)-1):
            eat_word(',');
            eat_spaces_and_check_empty();
            vals.append(parse_expr());
            eat_spaces_and_check_empty();
        return Assignment(lc, names, vals);
    def parse_for():
        nonlocal line_count, s;
        lc = line_count;
        clauses = [];
        def parse_clause():
            nonlocal s, line_count;
            def iterate_as_p():
                nonlocal s;
                return re.match(r'[A-Za-z_][A-Za-z0-9_]*\s*ITERATE\s*AS', s);
            def iterate_by_p():
                nonlocal s;
                return re.match(r'[A-Za-z_][A-Za-z0-9_]*\s*ITERATE\s*BY', s);
            def parse_iterate(which, build):
                nonlocal line_count, clauses, s;
                lc = line_count;
                id = parse_lvalue();
                eat_spaces_and_check_empty();
                eat_word("ITERATE");
                expect_eat_spaces_and_check_empty("ITERATE " + which);
                eat_word(which);
                expect_eat_spaces_and_check_empty("ITERATE " + which);
                expr = parse_expr();
                clauses.append(build(lc, id, expr));
                eat_spaces_and_check_empty()
                return parse_toplevel();
            def parse_expr_list(assign, name, which):
                nonlocal s, clauses;
                eat_word(which);
                expect_eat_spaces_and_check_empty("FOR " + which);
                exprs = [parse_expr()];
                eat_spaces_and_check_empty();
                for _ in range(len(assign.names)-1):
                    eat_word(',');
                    eat_spaces_and_check_empty();
                    exprs.append(parse_expr());
                    eat_spaces_and_check_empty();
                return exprs;
            def parse_then(lc, assign):
                nonlocal s, clauses;
                tos = parse_expr_list(assign, "THEN", "THEN");
                clauses.append(ThenForClause(lc, assign, tos));
                eat_spaces_and_check_empty()
                return parse_toplevel();
            def parse_step(lc, assign):
                nonlocal s, clauses;
                steps = parse_expr_list(assign, "STEP", "STEP");
                if s.startswith("TO"):
                    return parse_step_to(lc, assign, steps);
                else:
                    clauses.append(StepForClause(lc, assign, steps));
                    eat_spaces_and_check_empty()
                    return parse_toplevel();
            def parse_step_to(lc, assign, steps):
                nonlocal s, clauses;
                tos = parse_expr_list(assign, "STEP TO", "TO");
                clauses.append(StepToForClause(lc, assign, tos, steps));
                eat_spaces_and_check_empty()
                return parse_toplevel();
            def parse_to(lc, assign):
                nonlocal s, clauses;
                tos = parse_expr_list(assign, "TO", "TO");
                clauses.append(ToForClause(lc, assign, tos));
                eat_spaces_and_check_empty()
                return parse_toplevel();
            if iterate_as_p():
                return parse_iterate("AS", IterateAsForClause);
            elif iterate_by_p():
                return parse_iterate("BY", IterateByForClause);
            else:
                lc = line_count;
                assign = parse_assignment();
                eat_spaces_and_check_empty();
                if s.startswith("THEN"):
                    return parse_then(lc, assign);
                elif s.startswith("STEP"):
                    return parse_step(lc, assign);
                elif s.startswith("TO"):
                    return parse_to(lc, assign);
                else:
                    clauses.append(AssignForClause(lc, assign))
                    eat_spaces_and_check_empty()
                    return parse_toplevel();
        def parse_loop(which, build):
            nonlocal line_count, clauses;
            lc = line_count;
            eat_word(which);
            expect_eat_spaces_and_check_empty(which);
            cond = parse_expr();
            clauses.append(build(lc, cond));
            eat_spaces_and_check_empty()
            return parse_toplevel();
        def parse_while():
            return parse_loop("WHILE", WhileForClause);
        def parse_until():
            return parse_loop("UNTIL", UntilForClause);
        def parse_toplevel():
            nonlocal s;
            if s.startswith("DO"):
                return
            elif s.startswith("AS"):
                eat_word('AS');
                expect_eat_spaces_and_check_empty('AS');
                return parse_clause();
            elif s.startswith("WHILE"):
                return parse_while();
            elif s.startswith("UNTIL"):
                return parse_until();
            else:
                die(f"Bad FOR Syntax @ {line_count}");
        eat_word('FOR');
        expect_eat_spaces_and_check_empty('FOR');
        parse_clause();
        eat_spaces_and_check_empty();
        body = parse_statement();
        return ForSttmt(lc, clauses, body);
    def parse_if():
        nonlocal s, line_count;
        lc = line_count;
        eat_word('IF');
        eat_spaces_and_check_empty();
        cond = parse_expr();
        eat_spaces_and_check_empty();
        eat_word("THEN");
        eat_spaces_and_check_empty();
        then = parse_statement();
        eat_spaces_and_check_empty();
        if s.startswith("ELSE"):
            eat_word("ELSE");
            expect_eat_spaces_and_check_empty("IF statement");
            els  = parse_statement();
            eat_spaces_and_check_empty();
            eat_word(';');
            return IfElseSttmt(lc, cond, then, els);
        elif s.startswith(";"):
            eat_word(';');
            return IfSttmt(lc, cond, then);
        else:
            die(f"Bad IF, neither ; or ELSE after THEN statement @ {line_count}");
    def parse_goto():
        nonlocal line_count;
        lc = line_count;
        eat_word("GOTO");
        expect_eat_spaces_and_check_empty();
        if id_in_lib_p():
            id = parse_id_in_lib();
        elif idp():
            id = parse_id();
        else:
            die(f"Bad ID @ {line_count}");
        return GoToSttmt(lc, id);
    def parse_simple_sttmt(which, build):
        nonlocal line_count;
        lc = line_count;
        eat_word(which);
        expect_eat_spaces_or_smei_and_check_empty(which);
        return build(lc);
    def parse_break():
        return parse_simple_sttmt("BREAK", BreakSttmt);
    def parse_continue():
        return parse_simple_sttmt("CONTINUE", ContinueSttmt);
    def parse_void():
        return parse_simple_sttmt("VOID", VoidSttmt);
    def parse_assign_or_expr_sttmt():
        nonlocal s, line_count;
        lc = line_count;
        x = parse_expr();
        eat_spaces_and_check_empty();
        if s[0] == ',' or s.startswith(':='):
            return AssignmentSttmt(lc, parse_assignment([x]));
        else:
            return ExprSttmt(lc, x);
    def parse_statement():
        nonlocal line_count;
        lc = line_count
        if labelp():
            statement = parse_label();
        elif s.startswith('BEGIN'):
            statement = parse_begin();
        elif s.startswith('WHILE'):
            statement = parse_while();
        elif s.startswith('UNTIL'):
            statement = parse_until();
        elif s.startswith('FOR'):
            statement = parse_for();
        elif s.startswith('IF'):
            statement = parse_if();
        elif s.startswith('GOTO'):
            statement = parse_goto();
        elif s.startswith('BREAK'):
            statement = parse_break();
        elif s.startswith('CONTINUE'):
            statement = parse_continue();
        elif s.startswith('VOID'):
            statement = parse_void();
        else:
            statement = parse_assign_or_expr_sttmt();
        return Statement(lc, statement);
    def parse_name_arglist():
        nonlocal s;
        name = parse_id();
        eat_spaces_and_check_empty();
        arglist = None
        if s.startswith('('):
            arglist = parse_arglist();
        return name, arglist
    def parse_decls_and_statement():
        eat_spaces_and_check_empty();
        decls = parse_decls();
        eat_spaces_and_check_empty();
        body = parse_statement();
        return decls, body
    def parse_func_decl():
        nonlocal line_count
        lc = line_count
        eat_word("FUNCTION");
        expect_eat_spaces_and_check_empty("FUNCTION");
        name, arglist = parse_name_arglist();
        eat_spaces_and_check_empty();
        resvar = parse_id();
        eat_spaces_and_check_empty();
        eat_word(":");
        eat_spaces_and_check_empty();
        resvartype = parse_type();
        eat_spaces_and_check_empty();
        eat_word(";");
        decls, expr = parse_decls_and_statement();
        return FuncDecl(lc, name, arglist, resvar, resvartype, decls, expr);
    def parse_proc_decl():
        nonlocal line_count
        lc = line_count
        eat_word("PROCEDURE");
        expect_eat_spaces_and_check_empty("PROCEDURE");
        name, arglist = parse_name_arglist();
        eat_word(";");
        decls, expr = parse_decls_and_statement();
        return ProcDecl(lc, name, arglist, decls, expr);
    def parse_type_decl():
        nonlocal s, line_count;
        lc = line_count
        eat_word("TYPE");
        expect_eat_spaces_and_check_empty("TYPE");
        typedecls = [parse_a_bind(parse_type)];
        eat_spaces_and_check_empty();
        while s[0] == ',':
            eat_word(',');
            typedecls.append(parse_a_bind(parse_type));
            eat_spaces_and_check_empty();
        eat_word(';');
        return TypeDecl(lc, typedecls);
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
        nonlocal line_count;
        lc = line_count;
        eat_word(which);
        expect_eat_spaces_and_check_empty(which)
        name = parse_id();
        eat_spaces_and_check_empty();
        eat_word(';');
        decls, body = parse_decls_and_statement();
        return build(lc, name, decls, body);
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


x = parse_toplevel('''
PROGRAM test;
  FUNCTION blahblah(
  VAR x, y :
      ARRAY 2, 3 OF
      POINTER TO
      RECORD(VAR re, vi : REAL;);
  VAR a, b, c :
      INTEGER;
  ) res : INTEGER;
  TYPE blahtype = PROCEDURE;
  CONST blahconst1 = 2, blahconst2 = 3;
  BEGIN
    IF x > 0 THEN
      a[b#c](x)#a[@abc] := (a * b + c * d + c*d^e > 0 < 1 = 0)(abc)
    ELSE
      x := x + 1;
    FOR x, y := 1, 2 STEP 3, 4 TO 10, 20
    AS a ITERATE BY update
    AS b ITERATE AS a + 5
    AS c := 20 THEN c + 1 DO
      print(x+ y + a +b +c)
    a()
    b()
  END;
VOID
''')

print(x);
