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

import sys, argparse, re, inspect, os

VERSION = "1.0-1"

# token types
T_NAMES = ("OPERATOR", "NUMBER", "IDENTIFIER", "TAG", "(end of line)", "FUNCTION", "CONST")
T_OPER = 0
T_NUM = 1
T_ID = 2
T_TAG = 3
T_EOL = 4
T_FUNC = 5
T_CONST = 6

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
  ("sign", ("i",), [(T_ID, "signf"), (T_OPER, "("), (T_ID, "i"), (T_OPER, "+"), (T_NUM, "0.5"), (T_OPER, ")")]),
  ("signn", ("i",), [(T_ID, "signf"), (T_OPER, "("), (T_ID, "i"), (T_OPER, "-"), (T_NUM, "0.5"), (T_OPER, ")")]),
  ("int", ("x",), [(T_ID, "floor"), (T_OPER, "("), (T_ID, "x"), (T_OPER, ")"), (T_OPER, "+"), (T_OPER, "("), (T_NUM, "1"), (T_OPER, "-"), (T_ID, "sign"), (T_OPER, "("), (T_ID, "floor"), (T_OPER, "("), (T_ID, "x"), (T_OPER, ")"), (T_OPER, ")"), (T_OPER, ")"), (T_OPER, "/"), (T_NUM, "2")]),
  ("__<=", ("l", "r"), [(T_OPER, "("), (T_NUM, "1"), (T_OPER, "-"), (T_ID, "signn"), (T_OPER, "("), (T_ID, "l"), (T_OPER, "-"), (T_ID, "r"), (T_OPER, ")"), (T_OPER, ")"), (T_OPER, "/"), (T_NUM, "2")]),
  ("__>=", ("l", "r"), [(T_OPER, "("), (T_NUM, "1"), (T_OPER, "+"), (T_ID, "sign"), (T_OPER, "("), (T_ID, "l"), (T_OPER, "-"), (T_ID, "r"), (T_OPER, ")"), (T_OPER, ")"), (T_OPER, "/"), (T_NUM, "2")]),
  ("__<:", ("l", "r"), [(T_OPER, "("), (T_NUM, "1"), (T_OPER, "-"), (T_ID, "signf"), (T_OPER, "("), (T_ID, "l"), (T_OPER, "-"), (T_ID, "r"), (T_OPER, ")"), (T_OPER, ")"), (T_OPER, "/"), (T_NUM, "2")]),
  ("__>:", ("l", "r"), [(T_OPER, "("), (T_NUM, "1"), (T_OPER, "+"), (T_ID, "signf"), (T_OPER, "("), (T_ID, "l"), (T_OPER, "-"), (T_ID, "r"), (T_OPER, ")"), (T_OPER, ")"), (T_OPER, "/"), (T_NUM, "2")]),
  ("__<", ("l", "r"), [(T_OPER, "("), (T_NUM, "1"), (T_OPER, "-"), (T_ID, "sign"), (T_OPER, "("), (T_ID, "l"), (T_OPER, "-"), (T_ID, "r"), (T_OPER, ")"), (T_OPER, ")"), (T_OPER, "/"), (T_NUM, "2")]),
  ("__>", ("l", "r"), [(T_OPER, "("), (T_NUM, "1"), (T_OPER, "+"), (T_ID, "signn"), (T_OPER, "("), (T_ID, "l"), (T_OPER, "-"), (T_ID, "r"), (T_OPER, ")"), (T_OPER, ")"), (T_OPER, "/"), (T_NUM, "2")]),
  ("__==", ("l", "r"), [(T_OPER, "("), (T_ID, "l"), (T_OPER, ">="), (T_ID, "r"), (T_OPER, ")"), (T_OPER, "*"), (T_OPER, "("), (T_ID, "l"), (T_OPER, "<="), (T_ID, "r"), (T_OPER, ")")]),
  ("__!=", ("l", "r"), [(T_OPER, "("), (T_NUM, "4"), (T_OPER, "-"), (T_OPER, "("), (T_NUM, "1"), (T_OPER, "+"), (T_ID, "sign"), (T_OPER, "("), (T_ID, "l"), (T_OPER, "-"), (T_ID, "r"), (T_OPER, ")"), (T_OPER, ")"), (T_OPER, "*"), (T_OPER, "("), (T_NUM, "1"), (T_OPER, "-"), (T_ID, "signn"), (T_OPER, "("), (T_ID, "l"), (T_OPER, "-"), (T_ID, "r"), (T_OPER, ")"), (T_OPER, ")"), (T_OPER, ")"), (T_OPER, "/"), (T_NUM, "4")]),
  ("atan2", ("y", "x"), [(T_ID, "atan"), (T_OPER, "("), (T_ID, "y"), (T_OPER, "/"), (T_ID, "x"), (T_OPER, ")"), (T_OPER, "+"), (T_ID, "__<:"), (T_OPER, "("), (T_ID, "x"), (T_OPER, ","), (T_NUM, "0"), (T_OPER, ")"), (T_OPER, "*"), (T_ID, "signf"), (T_OPER, "("), (T_ID, "y"), (T_OPER, ")"), (T_OPER, "*"), (T_TAG, "pi")]),
  ("atan2d", ("y", "x"), [(T_ID, "deg"), (T_OPER, "("), (T_ID, "atan2"), (T_OPER, "("), (T_ID, "y"), (T_OPER, ","), (T_ID, "x"), (T_OPER, ")"), (T_OPER, ")")])
]

# globals
src = None
tokens = []
functions = {}
consts = {}
ti = 0
fn = None
debug = False

def error(message, line_no=None, col_no=None):
  if line_no is None and ti < len(tokens):
    if len(tokens[ti]) == 2:
      token_type, value = tokens[ti]
      line_no = None
    else:
      token_type, value, line_no, col_no = tokens[ti]
  if line_no is not None:
    line = src[line_no - 1].rstrip("\r\n")
    posinfo = "Line {0}, Col {1}, `{2}':\n".format(line_no, col_no, line)
  else:
    posinfo = ""
  sys.exit("{0}{1}.".format(posinfo, message))

def debug_print(var, value):
  if debug:
    if type(value).__name__ == "str":
      sys.stderr.write("{0} = `{1}'\n".format(var, value))
    else:
      sys.stderr.write("{0} = {1}\n".format(var, value))

def debug_parse(d):
  if not debug:
    return
  if ti < len(tokens):
    token = tokens[ti]
    if len(token) == 2:
      token_type, value = token
      line_no = 0
      col_no = 0
      line = ""
    else:
      token_type, value, line_no, col_no = token
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
  WHITESPACE = " \t\r\n;\f\v"
  OPERATORS = ["(", ")", "!=", "!", "^", "*", "/", "%", "+", "-", "<=", "<:", "<>", "<", ">=", ">:", ">", "&&", "||", "==", "=", "?", ":", ","]
  TAGS = ["pi", "e"]
  RE_NUM = re.compile(r"-?\d*\.?\d+")
  RE_ID = re.compile("[A-Za-z_][0-9A-Za-z_]*")
  RE_TAG = re.compile(r"#[0-9A-Za-z_]*#")

  mlc = False
  for line_no, line in enumerate(src):
    line_no += 1
    line = line.rstrip("\r\n")
    term = False
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

        # add a leading zero to bare decimal points
        if s[0] == ".":
          s = "0" + s
        elif s[0:2] == "-.":
          s = "-0" + s[1:]

        tokens.append((T_NUM, s, line_no, col_no))
        i += len(s)
        term = True
        continue

      # operator
      found_op = False
      for op in OPERATORS:
        if sub.startswith(op):
          tokens.append((T_OPER, op, line_no, col_no))
          i += len(op)
          term = True
          found_op = True
          break
      if found_op:
        continue

      # name
      match = RE_ID.match(sub)
      if match:
        s = match.group()
        if s in TAGS:
          tokens.append((T_TAG, s, line_no, col_no))
        else:
          tokens.append((T_ID, s, line_no, col_no))
        i += len(s)
        term = True
        continue

      # external tag
      match = RE_TAG.match(sub)
      if match:
        s = match.group()
        tokens.append((T_TAG, s, line_no, col_no))
        i += len(s)
        term = True
        continue

      error("Unrecognized input: `{0}'".format(sub), line_no, col_no)
    if term:
      tokens.append((T_EOL, "<EOL>", line_no, col_no))

def consume():
  global ti

  value = tokens[ti][1]
  ti += 1
  return value

def expect(expected):
  if len(tokens[ti]) == 2:
    token_type, value = tokens[ti]
    line_no = 0
    col_no = 0
  else:
    token_type, value, line_no, col_no = tokens[ti]
  istype = type(expected).__name__ == "int"
  if istype:
    if token_type != expected:
      error("Expected {0}, saw {1}".format(T_NAMES[expected], T_NAMES[token_type]))
  elif value != expected:
    error("Expected `{0}', saw `{1}'".format(expected, value))
  return consume()

def accepts(expected, discard=True):
  if ti >= len(tokens):
    return False
  if len(tokens[ti]) == 2:
    token_type, value = tokens[ti]
    line_no = 0
    col_no = 0
  else:
    token_type, value, line_no, col_no = tokens[ti]
  istype = type(expected).__name__ == "int"
  accepted = (istype and token_type == expected) or (not istype and value == expected)
  if accepted and discard:
    consume()
  return accepted

def getfunction(name):
  try:
    return functions[name]
  except:
    return None

def getconst(name):
  try:
    return consts[(fn, name)]
  except:
    return None

def deref_function(name, args):
  value = [(T_OPER, "(")]
  fn_parms, fn_value = functions[name]
  for fvalue in fn_value:
    if fvalue[0] == T_CONST and fvalue[1][0] == name:
      cname = fvalue[1][1]
      try:
        fvalue = args[fn_parms.index(cname)]
      except:
        error("Missing definition for const `{0}' in function `{1}'".format(cname, name))
    else:
      fvalue = [fvalue]
    value += fvalue
  value += [(T_OPER, ")")]
  return value

"""
primary_expression =
    "(" expression ")"
    | "if" "(" expression "?" expression [ ":" expression ] ")"
    | ID [ "(" [ expression { "," expression } ] ")" ]
    | NUM
    | TAG
    ;
"""
def parse_primary_expression():
  debug_in()
  value = []

  # (x)
  if accepts("("):
    value += [(T_OPER, "(")] + parse_expression() + [(T_OPER, ")")]
    expect(")")

  # consts and functions
  elif accepts(T_ID, False):
    name = expect(T_ID)

    # function
    if accepts("("):
      # get function declaration and generated expression
      function = getfunction(name)
      if function is None:
        error("Missing function declaration for `{0}'".format(name))
      fn_parms, fn_value = function

      # compare args to parms
      args = []
      if not accepts(")"):
        args.append(parse_expression())
        while not accepts(")"):
          expect(",")
          args.append(parse_expression())
      if len(args) != len(fn_parms):
        if len(fn_parms) > 0:
          parms = ": `{0}'".format(", ".join(fn_parms))
        else:
          parms = ""
        error("Function `{0}' expects {1} arguments{2}, got {3}".format(name, len(fn_parms), parms, len(args)))

      # extern functions have no associated expression except function call
      if fn_value is None:
        value += [(T_FUNC, name), (T_OPER, "(")]
        first = True
        for arg in args:
          if first:
            first = False
          else:
            value += [(T_OPER, ",")]
          value += arg
        value += [(T_OPER, ")")]

      # user functions or interns: substitute args for locals
      else:
        value += deref_function(name, args)

    # const
    else:
      cvalue = getconst(name)
      if cvalue is None:
        value += [(T_CONST, (fn, name))]
      else:
        value += [(T_OPER, "(")] + cvalue + [(T_OPER, ")")]

  # numeric value
  elif accepts(T_NUM, False):
    num = expect(T_NUM)
    debug_print("num", num)
    value += [(T_NUM, num)]

  # external tag
  else:
    tag = expect(T_TAG)
    debug_print("tag", tag)
    value += [(T_TAG, tag)]

  debug_out()
  return value

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
    lvalue = [(T_OPER, "-")] + parse_primary_expression()
  elif accepts("!") or accepts("not"):
    lvalue = [(T_OPER, "("), (T_NUM, "1"), (T_OPER, "-")] + parse_primary_expression() + [(T_OPER, ")")]
  else:
    lvalue = parse_primary_expression()
  debug_out()
  return lvalue

"""
exp_expression =
    unary_expression [ "^" unary_expression ]
    ;
"""
def parse_exp_expression():
  debug_in()
  lvalue = parse_unary_expression()
  if accepts("^"):
    rvalue = parse_unary_expression()
    lvalue = [(T_FUNC, "exp"), (T_OPER, "("), (T_FUNC, "log"), (T_OPER, "(")] + lvalue + [(T_OPER, ")"), (T_OPER, "*")] + rvalue + [(T_FUNC, ")")]
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
      lvalue += [(T_OPER, "*")] + rvalue
    elif accepts("/"):
      rvalue = parse_exp_expression()
      lvalue += [(T_OPER, "/")] + rvalue
    elif accepts("%"):
      rvalue = parse_exp_expression()
      lvalue += [(T_OPER, "-"), (T_OPER, "(")] + rvalue + [(T_OPER, "*"), (T_FUNC, "floor"), (T_OPER, "(")] + lvalue + [(T_OPER, "/")] + rvalue + [(T_OPER, ")"), (T_OPER, ")")]
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
      lvalue += [(T_OPER, "+")] + rvalue
    elif accepts("-"):
      rvalue = parse_mult_expression()
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
      lvalue = deref_function("__<=", (lvalue, rvalue))
    elif accepts(">="):
      rvalue = parse_add_expression()
      lvalue = deref_function("__>=", (lvalue, rvalue))
    elif accepts("<:"):
      rvalue = parse_add_expression()
      lvalue = deref_function("__<:", (lvalue, rvalue))
    elif accepts(">:"):
      rvalue = parse_add_expression()
      lvalue = deref_function("__>:", (lvalue, rvalue))
    elif accepts("<"):
      rvalue = parse_add_expression()
      lvalue = deref_function("__<", (lvalue, rvalue))
    elif accepts(">"):
      rvalue = parse_add_expression()
      lvalue = deref_function("__>", (lvalue, rvalue))
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
      lvalue = deref_function("__==", (lvalue, rvalue))
    elif accepts("!=") or accepts("<>"):
      rvalue = parse_rel_expression()
      lvalue = deref_function("__!=", (lvalue, rvalue))
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
      lvalue = [(T_OPER, "(")] + lvalue + [(T_OPER, "*")] + rvalue + [(T_OPER, ")")]
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
      lvalue = [(T_OPER, "("), (T_NUM, "1"), (T_OPER, "-"), (T_OPER, "("), (T_NUM, "1"), (T_OPER, "-")] + lvalue + [(T_OPER, ")"), (T_OPER, "*"), (T_OPER, "("), (T_NUM, "1"), (T_OPER, "-")] + rvalue + [(T_OPER, ")"), (T_OPER, ")")]
    else:
      break
  debug_out()
  return lvalue

"""
expression =
    "if" "(" expression "?" expression [ ":" expression ] ")"
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
    expect("?")
    tvalue = parse_expression()
    if accepts(":"):
      fvalue = parse_expression()
      lvalue = [(T_OPER, "(")] + bvalue + [(T_OPER, "*"), (T_OPER, "(")] + tvalue + [(T_OPER, "-")] + fvalue + [(T_OPER, ")"), (T_OPER, "+")] + fvalue + [(T_OPER, ")")]
    else:
      lvalue = [(T_OPER, "(")] + bvalue + [(T_OPER, "*")] + tvalue + [(T_OPER, ")")]
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
  name = expect(T_ID)
  expect("=")
  rvalue = parse_expression()
  consts[(fn, name)] = rvalue
  debug_print("{0}.{1}".format(fn, name), rvalue)
  debug_out()

"""
function =
    "function" ID "(" [ ID { "," ID } ] ")" <EOL> { statement <EOL> } "return" expression <EOL>
    ;
"""
def parse_function():
  global fn

  debug_in()
  expect("function")
  fn = expect(T_ID)
  debug_print("fn", fn)
  if getfunction(fn) is not None:
    error("Duplicate function declaration for `{0}'".format(fn))
  expect("(")
  parms = []
  if not accepts(")"):
    parms.append(expect(T_ID))
    while not accepts(")"):
      expect(",")
      parms.append(expect(T_ID))
  debug_print("parms", parms)

  # verify that main has no parms
  if fn == "main" and len(parms) > 0:
    error("Function `main' must not require arguments")

  expect("<EOL>")
  while not accepts("return"):
    parse_statement()
    expect("<EOL>")
  value = parse_expression()
  expect("<EOL>")
  functions[fn] = (parms, value)
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
  global src, debug, fn, tokens, ti

  # parse command line arguments
  parser = argparse.ArgumentParser(prog="cfs", description="Closed-Form Script Compiler.")
  parser.add_argument("-v", "--version", action="version", version="%(prog)s " + VERSION)
  parser.add_argument("-d", action="store_true", dest="debug", help="output verbose debugging information")
  parser.add_argument("-o", dest="dest", metavar="DEST", help="write output into file DEST instead of stdout")
  parser.add_argument("src", metavar="SOURCE", help="file containing program to compile")
  args = parser.parse_args()
  debug = args.debug

  # load external and library functions
  for name, parms in EXTERNS:
    functions[name] = (parms, None)
  for name, parms, value in LIBRARY:
    fn = name
    tokens = value
    ti = 0
    value = parse_expression()
    functions[name] = (parms, value)
  tokens = []
  ti = 0
  fn = None

  # read source code
  try:
    f = open(args.src, "r")
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
  expr = functions["main"]
  debug_print("expr", expr)
  expr_s = "("
  for value in expr[1]:
    if value[0] == T_CONST:
      fname, cname = value[1]
      error("Missing definition for const `{0}' in function `{1}'".format(cname, fname))
    else:
      value = value[1]
    expr_s += value
  expr_s += ")"

  # output expression
  if args.dest is None:
    print(expr_s)
  else:
    # open output file
    outfile = open(args.dest, "w")
    outfile.write(expr_s + os.linesep)
    outfile.close()

if __name__ == "__main__":
  main()

