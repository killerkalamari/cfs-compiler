#!/usr/bin/env python
#
# Closed-Form Script Compiler
# Compiles Closed-Form Script to a Facer compatible closed-form expression
#
# Copyright (C) 2017 Jeffry Johnston
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import sys, argparse, re, inspect, os, math
from decimal import Decimal

VERSION = "1.0-4"

# token types
T_NAMES = ("OPERATOR", "NUMBER", "IDENTIFIER", "TAG", "(end of line)", "FUNCTION", "CONST")
T_OPER = 0
T_NUM = 1
T_ID = 2
T_TAG = 3
T_FUNC = 4
T_CONST = 5

# external consts
CONSTS = {
  "pi":math.pi,
  "e":math.e
}

# external function definitions
EXTERNS = [
  ("rand", ("min", "max")),
  ("stRand", ("min", "max")),
  ("wakeRand", ("min", "max")),
  ("abs", ("number",)),
  ("sin", ("number",)),
  ("cos", ("number",)),
  ("tan", ("number",)),
  ("asin", ("number",)),
  ("acos", ("number",)),
  ("atan", ("number",)),
  ("sinh", ("number",)),
  ("cosh", ("number",)),
  ("tanh", ("number",)),
  ("round", ("number",)),
  ("ceil", ("number",)),
  ("floor", ("number",)),
  ("log", ("number",)),
  ("log2", ("number",)),
  ("log10", ("number",)),
  ("sqrt", ("number",)),
  ("cbrt", ("number",)),
  ("exp", ("number",)),
  ("expm1", ("number",)),
  ("deg", ("radians",)),
  ("rad", ("degrees",)),
  ("clamp", ("current", "min", "max")),
  ("squareWave", ("current", "amplitude", "period", "xOffset")),
  ("interpAccel", ("current", "min", "max", "accelerationFactor")),
  ("interpDecel", ("current", "min", "max", "accelerationFactor")),
  ("interpAccelDecel", ("current", "min", "max")),
  ("gyroX", ()),
  ("gyroY", ()),
  ("accelerometerX", ()),
  ("accelerometerY", ()),
  ("gyroRawX", ()),
  ("gyroRawY", ()),
  ("accelerometerRawX", ()),
  ("accelerometerRawY", ())
]

LIBRARY = [
  ("asind", ("x",), [(T_ID, "deg"), (T_OPER, "("), (T_ID, "asin"), (T_OPER, "("), (T_ID, "x"), (T_OPER, ")"), (T_OPER, ")")]),
  ("acosd", ("x",), [(T_ID, "deg"), (T_OPER, "("), (T_ID, "acos"), (T_OPER, "("), (T_ID, "x"), (T_OPER, ")"), (T_OPER, ")")]),
  ("atand", ("x",), [(T_ID, "deg"), (T_OPER, "("), (T_ID, "atan"), (T_OPER, "("), (T_ID, "x"), (T_OPER, ")"), (T_OPER, ")")]),
  ("sind", ("angle",), [(T_ID, "sin"), (T_OPER, "("), (T_ID, "rad"), (T_OPER, "("), (T_ID, "angle"), (T_OPER, ")"), (T_OPER, ")")]),
  ("cosd", ("angle",), [(T_ID, "cos"), (T_OPER, "("), (T_ID, "rad"), (T_OPER, "("), (T_ID, "angle"), (T_OPER, ")"), (T_OPER, ")")]),
  ("tand", ("angle",), [(T_ID, "tan"), (T_OPER, "("), (T_ID, "rad"), (T_OPER, "("), (T_ID, "angle"), (T_OPER, ")"), (T_OPER, ")")]),
  ("signf", ("x",), [(T_ID, "abs"), (T_OPER, "("), (T_ID, "x"), (T_OPER, ")"), (T_OPER, "/"), (T_OPER, "("), (T_ID, "x"), (T_OPER, ")")]),
  ("sign", ("i",), [(T_ID, "signf"), (T_OPER, "("), (T_ID, "i"), (T_OPER, "+"), (T_NUM, 0.5), (T_OPER, ")")]),
  ("signn", ("i",), [(T_ID, "signf"), (T_OPER, "("), (T_ID, "i"), (T_OPER, "-"), (T_NUM, 0.5), (T_OPER, ")")]),
  ("int", ("x",), [(T_ID, "floor"), (T_OPER, "("), (T_ID, "x"), (T_OPER, ")"), (T_OPER, "+"), (T_OPER, "("), (T_NUM, 1), (T_OPER, "-"), (T_ID, "sign"), (T_OPER, "("), (T_ID, "floor"), (T_OPER, "("), (T_ID, "x"), (T_OPER, ")"), (T_OPER, ")"), (T_OPER, ")"), (T_OPER, "/"), (T_NUM, 2)]),
  ("__<=", ("l", "r"), [(T_OPER, "("), (T_NUM, 1), (T_OPER, "-"), (T_ID, "signn"), (T_OPER, "("), (T_ID, "l"), (T_OPER, "-"), (T_ID, "r"), (T_OPER, ")"), (T_OPER, ")"), (T_OPER, "/"), (T_NUM, 2)]),
  ("__>=", ("l", "r"), [(T_OPER, "("), (T_NUM, 1), (T_OPER, "+"), (T_ID, "sign"), (T_OPER, "("), (T_ID, "l"), (T_OPER, "-"), (T_ID, "r"), (T_OPER, ")"), (T_OPER, ")"), (T_OPER, "/"), (T_NUM, 2)]),
  ("__<:", ("l", "r"), [(T_OPER, "("), (T_NUM, 1), (T_OPER, "-"), (T_ID, "signf"), (T_OPER, "("), (T_ID, "l"), (T_OPER, "-"), (T_ID, "r"), (T_OPER, ")"), (T_OPER, ")"), (T_OPER, "/"), (T_NUM, 2)]),
  ("__>:", ("l", "r"), [(T_OPER, "("), (T_NUM, 1), (T_OPER, "+"), (T_ID, "signf"), (T_OPER, "("), (T_ID, "l"), (T_OPER, "-"), (T_ID, "r"), (T_OPER, ")"), (T_OPER, ")"), (T_OPER, "/"), (T_NUM, 2)]),
  ("__<", ("l", "r"), [(T_OPER, "("), (T_NUM, 1), (T_OPER, "-"), (T_ID, "sign"), (T_OPER, "("), (T_ID, "l"), (T_OPER, "-"), (T_ID, "r"), (T_OPER, ")"), (T_OPER, ")"), (T_OPER, "/"), (T_NUM, 2)]),
  ("__>", ("l", "r"), [(T_OPER, "("), (T_NUM, 1), (T_OPER, "+"), (T_ID, "signn"), (T_OPER, "("), (T_ID, "l"), (T_OPER, "-"), (T_ID, "r"), (T_OPER, ")"), (T_OPER, ")"), (T_OPER, "/"), (T_NUM, 2)]),
  ("__==", ("l", "r"), [(T_OPER, "("), (T_ID, "l"), (T_OPER, ">="), (T_ID, "r"), (T_OPER, ")"), (T_OPER, "*"), (T_OPER, "("), (T_ID, "l"), (T_OPER, "<="), (T_ID, "r"), (T_OPER, ")")]),
  ("__!=", ("l", "r"), [(T_OPER, "("), (T_NUM, 4), (T_OPER, "-"), (T_OPER, "("), (T_NUM, 1), (T_OPER, "+"), (T_ID, "sign"), (T_OPER, "("), (T_ID, "l"), (T_OPER, "-"), (T_ID, "r"), (T_OPER, ")"), (T_OPER, ")"), (T_OPER, "*"), (T_OPER, "("), (T_NUM, 1), (T_OPER, "-"), (T_ID, "signn"), (T_OPER, "("), (T_ID, "l"), (T_OPER, "-"), (T_ID, "r"), (T_OPER, ")"), (T_OPER, ")"), (T_OPER, ")"), (T_OPER, "/"), (T_NUM, 4)]),
  ("atan2", ("y", "x"), [(T_ID, "atan"), (T_OPER, "("), (T_ID, "y"), (T_OPER, "/"), (T_ID, "x"), (T_OPER, ")"), (T_OPER, "+"), (T_ID, "__<:"), (T_OPER, "("), (T_ID, "x"), (T_OPER, ","), (T_NUM, 0), (T_OPER, ")"), (T_OPER, "*"), (T_ID, "signf"), (T_OPER, "("), (T_ID, "y"), (T_OPER, ")"), (T_OPER, "*"), (T_NUM, "pi")]),
  ("atan2d", ("y", "x"), [(T_ID, "deg"), (T_OPER, "("), (T_ID, "atan2"), (T_OPER, "("), (T_ID, "y"), (T_OPER, ","), (T_ID, "x"), (T_OPER, ")"), (T_OPER, ")")])
]

# globals
cmdline = None
src = None
tokens = []
functions = {}
consts = {}
ti = 0
fn = "lexer"
line_no = None
col_no = None

def error(message):
  global line_no, col_no

  if line_no is None and ti < len(tokens):
    if len(tokens[ti]) == 2:
      token_type, value = tokens[ti]
      line_no = None
    else:
      token_type, value, l, c = tokens[ti]
      if l is not None:
        line_no = l
      if c is not None:
        col_no = c
  if line_no is not None:
    line = src[line_no - 1].rstrip("\r\n")
    posinfo = "Line {0}, Col {1}, `{2}':\n".format(line_no, col_no, line)
  else:
    posinfo = ""
  sys.exit("{0}{1}.".format(posinfo, message))

def debug_print(var, value=None):
  if cmdline.debug:
    if value is None:
      sys.stderr.write("[{0}] {1}\n".format(fn, var))
    else:
      if type(value).__name__ == "str":
        sys.stderr.write("[{0}] {1} = `{2}'\n".format(fn, var, value))
      else:
        sys.stderr.write("[{0}] {1} = {2}\n".format(fn, var, value))

def debug_parse(d):
  if not cmdline.debug:
    return
  if ti < len(tokens):
    token = tokens[ti]
    if len(token) == 2:
      token_type, value = token
      line_no = None
      col_no = None
      line = ""
    else:
      token_type, value, line_no, col_no = tokens[ti]
      line = src[line_no - 1]
      line = (line[:col_no - 1].strip() + " ===> " + line[col_no - 1:]).strip()
  else:
    token = None
    line = None
  sys.stderr.write("{0} ({1}): ti={2}, token={3}, fn={4}, line=`{5}'\n".format(inspect.stack()[2][3], d, ti, token, fn, line))

def debug_in():
  debug_parse("in")

def debug_out():
  debug_parse("out")

def lexer():
  global line_no, col_no

  WHITESPACE = " \t\r\n\f\v"
  OPERATORS = ("(", ")", "!=", "!", "^", "*", "/", "%", "+", "-", "<=", "<:", "<>", "<", ">=", ">:", ">", "&&", "||", "==", "=", "?", ":", ",", ";", "{", "}")
  RE_NUM = re.compile(r"\d*\.?\d+")
  RE_ID = re.compile("[A-Za-z_][0-9A-Za-z_]*")
  RE_TAG = re.compile(r"#[0-9A-Za-z_]*#")

  mlc = False
  for line_no, line in enumerate(src):
    line_no += 1
    line = line.rstrip("\r\n")
    i = 0
    while i < len(line):
      sub = line[i:]
      col_no = i + 1

      # multi-line comment (end)
      if mlc:
        i = line.find("*/", i)
        if i < 0:
          break
        mlc = False
        i += 2
        continue

      # whitespace
      if sub[0] in WHITESPACE:
        i += 1
        continue

      # line comment
      if sub.startswith("//"):
        break

      # multi-line comment (start)
      elif sub.startswith("/*"):
        mlc = True
        i += 2
        continue

      # number
      match = RE_NUM.match(sub)
      if match:
        s = match.group()

        # add a leading zero to bare decimal point
        if s[0] == ".":
          s = "0" + s

        num = float(s) if "." in s else int(s)
        tokens.append((T_NUM, num, line_no, col_no))
        i += len(s)
        continue

      # operator
      found_op = False
      for op in OPERATORS:
        if sub.startswith(op):
          tokens.append((T_OPER, op, line_no, col_no))
          i += len(op)
          found_op = True
          break
      if found_op:
        continue

      # name
      match = RE_ID.match(sub)
      if match:
        s = match.group()
        if s in CONSTS:
          tokens.append((T_NUM, s, line_no, col_no))
        else:
          tokens.append((T_ID, s, line_no, col_no))
        i += len(s)
        continue

      # external tag
      match = RE_TAG.match(sub)
      if match:
        s = match.group()
        tokens.append((T_TAG, s, line_no, col_no))
        i += len(s)
        continue

      error("Unrecognized input: `{0}'".format(sub))

def consume():
  global ti

  value = tokens[ti][1]
  ti += 1
  return value

def expect_list(expected):
  global line_no, col_no

  if ti >= len(tokens):
    error("Unexpected end of input")
  if len(tokens[ti]) == 2:
    token_type, value = tokens[ti]
  else:
    token_type, value, l, c = tokens[ti]
    if l is not None:
      line_no = l
    if c is not None:
      col_no = c
  expected_text = []
  for expected_option in expected:
    istype = type(expected_option).__name__ == "int"
    if istype:
      if token_type == expected_option:
        return consume()
      expected_text.append(T_NAMES[expected_option])
    elif value == expected_option:
      return consume()
    else:
      expected_text.append("`{0}'".format(expected_option))
  oneof = ""
  if len(expected_text) > 1:
    oneof = "one of "
  error("Expected {0}{1}, saw `{2}' ({3})".format(oneof, ", ".join(expected_text), value, T_NAMES[token_type]))

def expect(expected):
  return expect_list([expected])

def accepts(expected, discard=True):
  global line_no, col_no

  if ti >= len(tokens):
    return False
  if len(tokens[ti]) == 2:
    token_type, value = tokens[ti]
  else:
    token_type, value, l, c = tokens[ti]
    if l is not None:
      line_no = l
    if c is not None:
      col_no = c
  istype = type(expected).__name__ == "int"
  accepted = (istype and token_type == expected) or (not istype and value == expected)
  if accepted and discard:
    consume()
  return accepted

def getfunction(function_name):
  try:
    return functions[function_name]
  except:
    return None

def getconst(const_name):
  try:
    return consts[(fn, const_name)]
  except:
    return None

def is_num(expr1, expr2=None, expr3=None):
  if expr2 == None:
    return len(expr1) == 1 and expr1[0][0] == T_NUM
  if expr3 == None:
    return expr1[-1][0] == T_NUM and len(expr2) == 1 and expr2[0][0] == T_NUM
  return expr1[-1][0] == T_NUM and len(expr2) == 1 and expr2[0][0] == T_NUM and len(expr3) == 1 and expr3[0][0] == T_NUM

def is_tag(expr1):
  return expr1[-1][0] == T_TAG and len(expr1) == 1

def deref_function(function_name, args):
  value = []
  fn_parms, fn_value = functions[function_name]
  for fvalue in fn_value:
    if fvalue[0] == T_CONST and fvalue[1][0] == function_name:
      const_name = fvalue[1][1]
      try:
        fvalue = [(T_OPER, "(")] + args[fn_parms.index(const_name)] + [(T_OPER, ")")]
      except:
        if cmdline.allow_const:
          fvalue = [fvalue]
        else:
          error("Missing definition for const `{0}' in function `{1}'".format(const_name, function_name))
    else:
      fvalue = [fvalue]
    value += fvalue
  if not (is_num(value) or is_tag(value)):
    value = [(T_OPER, "(")] + value + [(T_OPER, ")")]
  return value

def serialize_float(value):
  # http://stackoverflow.com/questions/6416474
  p = ("%.*f" % (16, value)).partition(".")
  return "".join((p[0], p[1], p[2][0], p[2][1:].rstrip("0")))

def serialize_expression(expr, allow_const=True):
  # serialize expression
  expr_s = ""
  for value in expr:
    if value[0] == T_CONST:
      if allow_const:
        value = value[1][1]
      else:
        function_name, const_name = value[1]
        error("Missing definition for const `{0}' in function `{1}'".format(const_name, function_name))
    else:
      value = value[1]
    if type(value).__name__ == "float":
      value_s = serialize_float(value)
    else:
      value_s = str(value)
    if value_s.endswith(".0"):
      value_s = value_s[:-2]
    expr_s += value_s
  return expr_s

def simplify_expression(function_name, expr):
  global fn, tokens, ti
  for token in expr:
    if token[0] == T_CONST:
      return expr

  # save globals
  fn_orig = fn
  tokens_orig = tokens
  ti_orig = ti
  debug_orig = cmdline.debug

  # set new globals
  fn = function_name
  tokens = expr
  ti = 0
  cmdline.debug = False

  # replace functions with id's
  for i in range(len(tokens)):
    if tokens[i][0] == T_FUNC:
      tokens[i][0] = T_ID

  # parse expr
  expr = parse_expression()

  # restore globals
  fn = fn_orig
  tokens = tokens_orig
  ti = ti_orig
  cmdline.debug = debug_orig
  return expr

def calc_function(expr):
  args = expr[2:-1]
  if not is_num(args):
    return expr
  arg1 = args[0][1]
  function_name = expr[0][1]
  try:
    if function_name == "abs":
      token = [[T_NUM, abs(arg1)]]
    elif function_name == "sin":
      token = [[T_NUM, math.sin(arg1)]]
    elif function_name == "cos":
      token = [[T_NUM, math.cos(arg1)]]
    elif function_name == "tan":
      token = [[T_NUM, math.tan(arg1)]]
    elif function_name == "asin":
      token = [[T_NUM, math.asin(arg1)]]
    elif function_name == "acos":
      token = [[T_NUM, math.acos(arg1)]]
    elif function_name == "atan":
      token = [[T_NUM, math.atan(arg1)]]
    elif function_name == "sinh":
      token = [[T_NUM, math.sinh(arg1)]]
    elif function_name == "cosh":
      token = [[T_NUM, math.cosh(arg1)]]
    elif function_name == "tanh":
      token = [[T_NUM, math.tanh(arg1)]]
    elif function_name == "round":
      token = [[T_NUM, round(arg1)]]
    elif function_name == "ceil":
      token = [[T_NUM, math.ceil(arg1)]]
    elif function_name == "floor":
      token = [[T_NUM, math.floor(arg1)]]
    elif function_name == "log":
      token = [[T_NUM, math.log(arg1)]]
    elif function_name == "log2":
      token = [[T_NUM, math.log(arg1) / math.log(2)]]
    elif function_name == "log10":
      token = [[T_NUM, math.log10(arg1)]]
    elif function_name == "sqrt":
      token = [[T_NUM, math.sqrt(arg1)]]
    elif function_name == "cbrt":
      token = [[T_NUM, arg1 ** (1.0 / 3)]]
    elif function_name == "exp":
      token = [[T_NUM, math.exp(arg1)]]
    elif function_name == "expm1":
      token = [[T_NUM, math.exp(arg1) - 1]]
    elif function_name == "deg":
      token = [[T_NUM, arg1 * 180 / math.pi]]
    elif function_name == "rad":
      token = [[T_NUM, arg1 * math.pi / 180]]
  except ValueError as e:
    error("Error calculating `{0}'".format(serialize_expression(expr)))
  return token

def deref_tag(token):
  value = token[1]
  try:
    return CONSTS[value]
  except:
    return value

def calc_expression(operator, expr1, expr2=None, expr3=None):
  arg1 = None
  arg2 = None
  arg3 = None
  if expr2 == None:
    arg1 = deref_tag(expr1[0])
  else:
    arg1 = deref_tag(expr1[-1])
    arg2 = deref_tag(expr2[0])
    if expr3 != None:
      arg3 = deref_tag(expr3[0])
  if operator == "(-)":
    value = -arg1
  elif operator == "!":
    value = 1 - arg1
  elif operator == "^":
    value = arg1 ** arg2
  elif operator == "*" or operator == "&&" or operator == "?":
    value = arg1 * arg2
  elif operator == "/":
    try:
      value = arg1 / float(arg2)
    except ZeroDivisionError as e:
      error("Division by zero calculating `{0} / {1}'".format(arg1, arg2))
  elif operator == "%":
    try:
      value = arg1 % arg2
    except ZeroDivisionError as e:
      error("Division by zero calculating `{0} % {1}'".format(arg1, arg2))
  elif operator == "+":
    value = arg1 + arg2
  elif operator == "-":
    value = arg1 - arg2
  elif operator == "<=":
    value = int(arg1 <= arg2)
  elif operator == ">=":
    value = int(arg1 >= arg2)
  elif operator == "<:" or operator == "<":
    value = int(arg1 < arg2)
  elif operator == ">:" or operator == ">":
    value = int(arg1 > arg2)
  elif operator == "==":
    value = int(arg1 == arg2)
  elif operator == "!=":
    value = int(arg1 != arg2)
  elif operator == "||":
    value = 1 - (1 - arg1) * (1 - arg2)
  elif operator == "?:":
    value = arg1 * (arg2 - arg3) + arg3
  debug_print("calc: operator=[{0}], exprs=[{1} {2} {3}], args=[{4} {5} {6}]={7}".format(operator, expr1, expr2, expr3, arg1, arg2, arg3, value))
  token = [[T_NUM, value]]
  return token

"""
primary_expression =
    "(" expression ")"
    | ID [ "(" [ expression { [ "," ] expression } ] ")" ]
    | NUM
    | TAG
    ;
"""
def parse_primary_expression():
  debug_in()
  lvalue = []

  # parentheses
  if accepts("("):
    expr = parse_expression()
    if is_num(expr) or is_tag(expr):
      lvalue += expr
    else:
      lvalue += [(T_OPER, "(")] + expr + [(T_OPER, ")")]
    expect(")")

  # consts and functions
  elif accepts(T_ID, False):
    name = expect(T_ID)

    # function
    if accepts("("):
      function_name = name
      debug_print("==[start {0}]".format(function_name) + ("=" * (70 - len(function_name))))
      # get function declaration and generated expression
      function = getfunction(function_name)
      if function is None:
        error("Missing function declaration for `{0}'".format(function_name))
      fn_parms, fn_expr = function

      # compare args to parms
      args = []
      if not accepts(")"):
        debug_print("args function_name=[{0}], arg#={1}, expr=`{2}' ===> `{3}'".format(function_name, len(args), serialize_expression(tokens[:ti]), serialize_expression(tokens[ti:])))
        expr = parse_expression()
        args.append(expr)
        debug_print("expr function_name=[{0}], arg#={1}, expr=`{2}'".format(function_name, len(args), serialize_expression(expr)))

        while not accepts(")"):
          accepts(",")
          debug_print("args function_name=[{0}], arg#={1}, expr=`{2}' ===> `{3}'".format(function_name, len(args), serialize_expression(tokens[:ti]), serialize_expression(tokens[ti:])))
          expr = parse_expression()
          args.append(expr)
          debug_print("expr function_name=[{0}], arg#={1}, expr=`{2}'".format(function_name, len(args), serialize_expression(expr)))
        debug_print("args (end) function_name=[{0}], arg#={1}, expr=`{2}' ===> `{3}'".format(function_name, len(args), serialize_expression(tokens[:ti]), serialize_expression(tokens[ti:])))
      if len(args) != len(fn_parms):
        if len(fn_parms) > 0:
          parms = ": `{0}'".format(", ".join(fn_parms))
        else:
          parms = ""
        error("Function `{0}' expects {1} arguments{2}, got {3}".format(function_name, len(fn_parms), parms, len(args)))

      # extern functions have no associated expression except function call
      if fn_expr is None:
        fn_expr = [[T_FUNC, function_name], (T_OPER, "(")]
        first = True
        for arg in args:
          if first:
            first = False
          fn_expr += arg
        fn_expr += [(T_OPER, ")")]
        lvalue += calc_function(fn_expr)

      # user functions or interns: substitute args for locals
      else:
        expr = deref_function(function_name, args)
        debug_print("deref: {0}".format(serialize_expression(expr)))
        expr = simplify_expression(function_name, expr)
        debug_print("simplify: {0}".format(serialize_expression(expr)))
        lvalue += expr
      debug_print("==[end {0}]".format(function_name) + ("=" * (72 - len(function_name))))

    # const
    else:
      const_name = name
      const_expr = getconst(const_name)
      if const_expr is None:
        lvalue += [(T_CONST, (fn, const_name))]
      else:
        if is_num(const_expr):
          lvalue += const_expr
        else:
          lvalue += [(T_OPER, "(")] + const_expr + [(T_OPER, ")")]

  # numeric value
  elif accepts(T_NUM, False):
    num = expect(T_NUM)
    debug_print("num", num)
    lvalue += [[T_NUM, num]]

  # external tag
  elif accepts(T_TAG, False):
    tag = expect(T_TAG)
    debug_print("tag", tag)
    lvalue += [[T_TAG, tag]]

  # unexpected input
  else:
    error("Unexpected or incomplete input")

  debug_out()
  return lvalue

"""
unary_expression =
    "-" primary_expression
    | ( "!" | "not" ) primary_expression
    | primary_expression
    ;
"""
def parse_unary_expression():
  debug_in()
  if accepts("-"):
    rvalue = parse_primary_expression()
    if is_num(rvalue):
      lvalue = calc_expression("(-)", rvalue)
    else:
      lvalue = [(T_OPER, "-")] + rvalue
  elif accepts("!") or accepts("not"):
    rvalue = parse_primary_expression()
    if is_num(rvalue):
      lvalue = calc_expression("!", rvalue)
    else:
      lvalue = simplify_expression(fn, [(T_OPER, "("), (T_NUM, 1), (T_OPER, "-")] + rvalue + [(T_OPER, ")")])
  else:
    lvalue = parse_primary_expression()
  debug_out()
  return lvalue

"""
exp_expression =
    unary_expression { "^" unary_expression }
    ;
"""
def parse_exp_expression():
  debug_in()
  lvalue = parse_unary_expression()
  while True:
    if accepts("^"):
      rvalue = parse_unary_expression()
      if is_num(lvalue, rvalue):
        lvalue = lvalue[:-1] + calc_expression("^", lvalue, rvalue)
      else:
        lvalue = simplify_expression(fn, [(T_ID, "exp"), (T_OPER, "("), (T_ID, "log"), (T_OPER, "(")] + lvalue + [(T_OPER, ")"), (T_OPER, "*")] + rvalue + [(T_OPER, ")")])
    else:
      break
  debug_out()
  return lvalue

"""
mult_expression =
    exp_expression { ( "*" | "/" | "%" ) exp_expression }
    ;
"""
def parse_mult_expression():
  debug_in()
  lvalue = parse_exp_expression()
  while True:
    if accepts("*"):
      rvalue = parse_exp_expression()
      if is_num(lvalue, rvalue):
        lvalue = lvalue[:-1] + calc_expression("*", lvalue, rvalue)
      else:
        lvalue += [(T_OPER, "*")] + rvalue
    elif accepts("/"):
      rvalue = parse_exp_expression()
      if is_num(lvalue, rvalue):
        lvalue = lvalue[:-1] + calc_expression("/", lvalue, rvalue)
      else:
        lvalue += [(T_OPER, "/")] + rvalue
    elif accepts("%"):
      rvalue = parse_exp_expression()
      if is_num(lvalue, rvalue):
        lvalue = lvalue[:-1] + calc_expression("%", lvalue, rvalue)
      else:
        lvalue = simplify_expression(fn, lvalue + [(T_OPER, "-"), (T_OPER, "(")] + rvalue + [(T_OPER, "*"), [T_ID, "floor"], (T_OPER, "(")] + lvalue + [(T_OPER, "/")] + rvalue + [(T_OPER, ")"), (T_OPER, ")")])
    else:
      break
  debug_out()
  return lvalue

"""
add_expression =
    mult_expression { ( "+" | "-" ) mult_expression }
    ;
"""
def parse_add_expression():
  debug_in()
  lvalue = parse_mult_expression()
  while True:
    if accepts("+"):
      rvalue = parse_mult_expression()
      if is_num(lvalue, rvalue):
        lvalue = lvalue[:-1] + calc_expression("+", lvalue, rvalue)
      else:
        lvalue += [(T_OPER, "+")] + rvalue
    elif accepts("-"):
      rvalue = parse_mult_expression()
      if is_num(lvalue, rvalue):
        lvalue = lvalue[:-1] + calc_expression("-", lvalue, rvalue)
      else:
        lvalue += [(T_OPER, "-")] + rvalue
    else:
      break
  debug_out()
  return lvalue

"""
rel_expression =
    add_expression { ( "<=" | ">=" | "<:" | ">:" | "<" | ">" ) add_expression }
    ;
"""
def parse_rel_expression():
  debug_in()
  lvalue = parse_add_expression()
  while True:
    if accepts("<="):
      rvalue = parse_add_expression()
      if is_num(lvalue, rvalue):
        lvalue = lvalue[:-1] + calc_expression("<=", lvalue, rvalue)
      else:
        lvalue = simplify_expression(fn, deref_function("__<=", (lvalue, rvalue)))
    elif accepts(">="):
      rvalue = parse_add_expression()
      if is_num(lvalue, rvalue):
        lvalue = lvalue[:-1] + calc_expression(">=", lvalue, rvalue)
      else:
        lvalue = simplify_expression(fn, deref_function("__>=", (lvalue, rvalue)))
    elif accepts("<:"):
      rvalue = parse_add_expression()
      if is_num(lvalue, rvalue):
        lvalue = lvalue[:-1] + calc_expression("<:", lvalue, rvalue)
      else:
        lvalue = simplify_expression(fn, deref_function("__<:", (lvalue, rvalue)))
    elif accepts(">:"):
      rvalue = parse_add_expression()
      if is_num(lvalue, rvalue):
        lvalue = lvalue[:-1] + calc_expression(">:", lvalue, rvalue)
      else:
        lvalue = simplify_expression(fn, deref_function("__>:", (lvalue, rvalue)))
    elif accepts("<"):
      rvalue = parse_add_expression()
      if is_num(lvalue, rvalue):
        lvalue = lvalue[:-1] + calc_expression("<", lvalue, rvalue)
      else:
        lvalue = simplify_expression(fn, deref_function("__<", (lvalue, rvalue)))
    elif accepts(">"):
      rvalue = parse_add_expression()
      if is_num(lvalue, rvalue):
        lvalue = lvalue[:-1] + calc_expression(">", lvalue, rvalue)
      else:
        lvalue = simplify_expression(fn, deref_function("__>", (lvalue, rvalue)))
    else:
      break
  debug_out()
  return lvalue

"""
equ_expression =
    rel_expression { ( "==" | "=" | "!=" | "<>" ) rel_expression }
    ;
"""
def parse_equ_expression():
  debug_in()
  lvalue = parse_rel_expression()
  while True:
    if accepts("==") or accepts("="):
      rvalue = parse_rel_expression()
      if is_num(lvalue, rvalue):
        lvalue = lvalue[:-1] + calc_expression("==", lvalue, rvalue)
      else:
        lvalue = simplify_expression(fn, deref_function("__==", (lvalue, rvalue)))
    elif accepts("!=") or accepts("<>"):
      rvalue = parse_rel_expression()
      if is_num(lvalue, rvalue):
        lvalue = lvalue[:-1] + calc_expression("!=", lvalue, rvalue)
      else:
        lvalue = simplify_expression(fn, deref_function("__!=", (lvalue, rvalue)))
    else:
      break
  debug_out()
  return lvalue

"""
and_expression =
    equ_expression { ( "&&" | "and" ) equ_expression }
    ;
"""
def parse_and_expression():
  debug_in()
  lvalue = parse_equ_expression()
  while True:
    if accepts("&&") or accepts("and"):
      rvalue = parse_equ_expression()
      if is_num(lvalue, rvalue):
        lvalue = lvalue[:-1] + calc_expression("&&", lvalue, rvalue)
      else:
        lvalue = simplify_expression(fn, [(T_OPER, "(")] + lvalue + [(T_OPER, "*")] + rvalue + [(T_OPER, ")")])
    else:
      break
  debug_out()
  return lvalue

"""
or_expression =
    and_expression { ( "||" | "or" ) and_expression }
    ;
"""
def parse_or_expression():
  debug_in()
  lvalue = parse_and_expression()
  while True:
    if accepts("||") or accepts("or"):
      rvalue = parse_and_expression()
      if is_num(lvalue, rvalue):
        lvalue = lvalue[:-1] + calc_expression("||", lvalue, rvalue)
      else:
        lvalue = simplify_expression(fn, [(T_OPER, "("), (T_NUM, 1), (T_OPER, "-"), (T_OPER, "("), (T_NUM, 1), (T_OPER, "-")] + lvalue + [(T_OPER, ")"), (T_OPER, "*"), (T_OPER, "("), (T_NUM, 1), (T_OPER, "-")] + rvalue + [(T_OPER, ")"), (T_OPER, ")")])
    else:
      break
  debug_out()
  return lvalue

"""
expression =
    "if" "(" expression ( "?" | "," ) expression [ ( ":" | "," ) expression ] ")"
    | or_expression
    ;
"""
def parse_expression():
  debug_in()

  # ternary / binary operator
  #   b ? t : f -> (b * (t - f) + f)
  #   b ? t     -> (b * t)
  if accepts("if"):
    expect("(")
    bvalue = parse_expression()
    expect_list(["?", ","])
    tvalue = parse_expression()
    if accepts(":") or accepts(","):
      fvalue = parse_expression()
      if is_num(bvalue, tvalue, fvalue):
        lvalue = lvalue[:-1] + calc_expression("?:", bvalue, tvalue, fvalue)
      else:
        lvalue = simplify_expression(fn, [(T_OPER, "(")] + bvalue + [(T_OPER, "*"), (T_OPER, "(")] + tvalue + [(T_OPER, "-")] + fvalue + [(T_OPER, ")"), (T_OPER, "+")] + fvalue + [(T_OPER, ")")])
    else:
      if is_num(bvalue, tvalue):
        lvalue = lvalue[:-1] + calc_expression("?", bvalue, tvalue)
      else:
        lvalue = simplify_expression(fn, [(T_OPER, "(")] + bvalue + [(T_OPER, "*")] + tvalue + [(T_OPER, ")")])
    expect(")")
  else:
    lvalue = parse_or_expression()

  debug_out()
  return lvalue

"""
statement =
    ID "=" expression
    ;
"""
def parse_statement():
  debug_in()
  const_name = expect(T_ID)
  if getconst(const_name) is not None:
    error("Duplicate const declaration for `{0}'".format(const_name))
  expect("=")
  rvalue = parse_expression()
  consts[(fn, const_name)] = rvalue
  debug_print("{0}.{1}".format(fn, const_name), rvalue)
  debug_out()

"""
function =
    [ "function" | "def" | "double" ] ID "(" [ ID { [ "," ] ID } ] ")" [ ":" | "{" ] { statement [ ";" ] } "return" expression [ ";" ] [ "}" ]
    ;
"""
def parse_function():
  global fn

  debug_in()
  accepts("function") or accepts("def") or accepts("double")
  fn = expect(T_ID)
  debug_print("fn", fn)
  if getfunction(fn) is not None:
    error("Duplicate function declaration for `{0}'".format(fn))
  expect("(")
  parms = []
  if not accepts(")"):
    parms.append(expect(T_ID))
    while not accepts(")"):
      accepts(",")
      parms.append(expect(T_ID))
  debug_print("parms", parms)

  # verify that main has no parms
  if fn == "main" and len(parms) > 0:
    error("Function `main' must not take arguments")

  accepts(":") or accepts("{")
  while not accepts("return"):
    parse_statement()
    accepts(";")
  expr = parse_expression()
  accepts(";")
  accepts("}")
  functions[fn] = (parms, expr)
  debug_out()

"""
program =
    function { function }
    ;
"""
def parse_program():
  debug_in()
  while True:
    parse_function()
    if ti >= len(tokens):
      break
  debug_out()

def parse():
  parse_program()

def main():
  global src, cmdline, fn, tokens, ti

  # parse command line arguments
  parser = argparse.ArgumentParser(prog="cfs", description="Closed-Form Script Compiler.")
  parser.add_argument("-v", "--version", action="version", version="%(prog)s " + VERSION)
  parser.add_argument("-d", action="store_true", dest="debug", help="output verbose debugging information")
  parser.add_argument("-c", "--allow-const", action="store_true", dest="allow_const", help="don't generate an error on missing consts")
  parser.add_argument("-o", dest="dest", metavar="DEST", help="write output into file DEST instead of stdout")
  parser.add_argument("src", metavar="SOURCE", help="file containing program to compile")
  cmdline = parser.parse_args()

  # load external and library functions
  debug_orig = cmdline.debug
  cmdline.debug = False
  for name, parms in EXTERNS:
    functions[name] = (parms, None)
  for name, parms, expr in LIBRARY:
    expr = simplify_expression(name, expr)
    functions[name] = (parms, expr)
  cmdline.debug = debug_orig

  # read source code
  try:
    f = open(cmdline.src, "r")
    src = f.readlines()
    f.close()
  except IOError as e:
    sys.exit("Error reading source file: {0}".format(e))

  # parse into tokens
  lexer()
  debug_print("tokens", tokens)

  # parse grammar
  parse()
  debug_print("functions", functions)
  debug_print("consts", consts)

  # verify main function exists
  if not functions.has_key("main"):
    error("Missing required function declaration: `main'")

  # serialize expression
  expr = functions["main"][1]
  debug_print("expr", expr)
  expr_s = "(" + serialize_expression(expr, cmdline.allow_const) + ")"

  # output expression
  if cmdline.dest is None:
    print(expr_s)
  else:
    # open output file
    outfile = open(cmdline.dest, "w")
    outfile.write(expr_s + os.linesep)
    outfile.close()

if __name__ == "__main__":
  main()

