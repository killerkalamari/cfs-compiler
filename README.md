# cfs-compiler
Compiles Closed-Form Script (_cfs_) to a closed-form expression fully compatible with the Facer Android Wear watchface composer tool and app. My goals for _cfs_ are to facilitate the creation of watchface complications and secondarily to work around bugs and omissions in the Facer implementation. Using _cfs_, expressions can be generated that would be much too tedious to code by hand.

The _cfs_ language provides additional functions for trigonometric and integer operations, const-style expression assignments, custom function declarations, and binary, ternary, and logical operators that are not based on the Facer equivalents. 

The _cfs.py_ compiler is written in Python and is compatible with both Python 2 and 3.

### Table of Contents
[Language Description](#language-description)

[Operator Precedence](#operator-precedence)

[Internal Functions](#internal-functions-and-operators)

[Grammar](#formal-grammar)

## Language Description
### Overall Structure
A _cfs_ program is comprised of one or more lines of comments, function declarations, const assignment statements, and return expressions. No special statement terminator characters are necessary, although a semicolon may be used if desired. There must be at least one function defined, named `main`, that takes no arguments and returns an expression. The `main()` function is the starting point for program execution.

### Comments
Single line and multi-line comments are available, using the familiar C/C++ operators, `//` and `/* */`. Comments may start at the beginning or end of a line. Multi-line comments may span multiple lines and end in the middle of a line, if desired. 

**Single line comment examples:**
```
//return atan2d(0.559666, -0.762512)
lat = 37 // Latitude for North America 
```

**Multi-line comment example:**
```
/*
function jupiter()
	return planet(11.857911, 337.917132, 5.20278)
*/
```

### Identifiers
Identifiers in _cfs_ are used for function and const names, and are case sensitive. They are comprised of upper- and lowercase ASCII letters, numbers, and/or underscores, but cannot begin with a number.

### Facer Constants, Operators, Tags, and Functions
Facer constants, operators, tags, and functions may be used, with their standard syntax. However, the Facer ternary and logical operators have been replaced.

### Literals
Real numbers, `pi`, and `e` are supported as literals in _cfs_.

### Data Types
Although all _cfs_ values are represented by floating-point numbers, functions will only produce defined results when input values adhere to the following input type restrictions:

| Type  | Description                               |
| ----- | ----------------------------------------- |
| float | Floating-point (real) number              |
| int   | Integer (whole) number                    |
| bool  | Boolean values `0` (false) and `1` (true) |

### Operators
The following operators are available in addition to the standard arithmetic operators. Some operators have restrictions on input values. Refer to the _[Internal Functions](#internal-functions-and-operators)_ table for details.

| Operator | Syntax      | Input Types        | Output Type | Description                       |
| -------- | ----------- | ------------------ | ----------- | --------------------------------- |
| `!`      | `!x`        | bool               | bool        | Boolean not.                      |
| `not`    | `not x`     | bool               | bool        | Boolean not.                      |
| `^`      | `x^y`       | float, float       | float       | Exponentiation, left-associative. Tip: To square a number, use `x * x`. |
| `%`      | `x%y`       | float, float       | float       | Modulo (remainder) function.      |
| `<=`     | `x<=y`      | int, int           | bool        | Integer less than or equal to.    |
| `>=`     | `x>=y`      | int, int           | bool        | Integer greater than or equal to. |
| `<:`     | `x<:y`      | float, float       | bool        | Floating-point less than.         |
| `>:`     | `x>:y`      | float, float       | bool        | Floating-point greater than.      |
| `<`      | `x<y`       | int, int           | bool        | Integer less than.                |
| `>`      | `x>y`       | int, int           | bool        | Integer greater than.             |
| `==`     | `x==y`      | int, int           | bool        | Integer equality.                 |
| `=`      | `x=y`       | int, int           | bool        | Integer equality.                 |
| `!=`     | `x!=y`      | int, int           | bool        | Integer inequality.               |
| `<>`     | `x<>y`      | int, int           | bool        | Integer inequality.               |
| `&&`     | `x&&y`      | bool, bool         | bool        | Boolean and.                      |
| `and`    | `x and y`   | bool, bool         | bool        | Boolean and.                      |
| `||`     | `x||y`      | bool, bool         | bool        | Boolean or.                       |
| `or`     | `x or y`    | bool, bool         | bool        | Boolean or.                       |
| `if(,)`  | `if(b,t)`   | bool, float        | float       | Binary operator. Returns `t` on true, `0` on false. |
| `if(,,)` | `if(b,t,f)` | bool, float, float | float       | Ternary operator. Returns `t` on true, `f` on false. |

### Consts
A const defines a name for an expression, with scope restricted to the function in which it is defined. Consts may not be redefined within a function, however the same const name may be defined in multiple functions.

### Function Definitions
Functions in _cfs_ may have zero or more required parameters, surrounded by required parentheses. Parameters may be optionally comma-separated. Functions may include zero or more statements, and must conclude with one `return` statement.

### Statements
#### Assignment Statement
Assigns an expression to a const. The const name and expression must be separated by `=`.
#### Return Statement
Defines the return expression of a function.

## Operator Precedence
| Precedence | Operators                        | Description                                           |
| ---------- | -------------------------------- | ----------------------------------------------------- |
| 1          | `()`, _fn_`()`                   | parentheses, function calls                           |
| 2          | `-`, `!`, `not`                  | unary minus, bool not                                 |
| 3          | `^`                              | exponentiation                                        |
| 4          | `*`, `/`, `%`                    | multiplication, truncating division, division, modulo |
| 5          | `+`, `-`                         | addition, subtraction                                 |
| 6          | `<=`, `>=`, `<:`, `>:`, `<`, `>` | int and float comparisons                             |
| 7          | `==`, `=`, `!=`, `<>`            | int comparisons                                       |
| 8          | `&&`, `and`                      | bool and                                              |
| 9          | `||`, `or`                       | bool or                                               |
| 10         | `if(?)`, `if(?:)`                | binary and ternary conditionals                       |

## Internal Functions and Operators
| Function            | Input Types        | Output Type | Implementation                             | Domain         |
| ------------------- | ------------------ | ----------- | -------------------------------------------| -------------- |
| `acosd(x)`          | float              | float       | `deg(acos(x))`                             | −1 ≤ x ≤ 1     |
| `asind(x)`          | float              | float       | `deg(asin(x))`                             | −1 ≤ x ≤ 1     |
| `atan2(y, x)`       | float, float       | float       | `atan(y / x) + (x <: 0) * signf(y) * pi`   | x ≠ 0, y ≠ 0   |
| `atan2d(y, x)`      | float, float       | float       | `deg(atan2(y, x))`                         | x ≠ 0, y ≠ 0   |
| `atand(x)`          | float              | float       | `deg(atan(x))`                             | ℝ              |
| `cosd(θ)`           | float              | float       | `cos(rad(θ))`                              | ℝ              |
| `int(x)`            | float              | int         | `floor(x) + (1 - sign(floor(x))) / 2`      | ℝ              |
| `sind(θ)`           | float              | float       | `sin(rad(θ))`                              | ℝ              |
| `sign(i)`           | int                | int         | `signf(i + 0.5)`                           | x ≠ -0.5       |
| `signf(x)`          | float              | int         | `abs(x) / x`                               | x ≠ 0          |
| `signn(i)`          | int                | int         | `signf(i - 0.5)`                           | x ≠ 0.5        |
| `tand(θ)`           | float              | float       | `tan(rad(θ))`                              | x ≠ π/2 + *k*π |
| `!x`, `not x`       | bool               | bool        | `1 - x`                                    | x = [0, 1]     |
| `x ^ y`             | float, float       | float       | `exp(log(x) * y)`                          | x ≠ 0          |
| `x % y`             | float, float       | float       | `x - (y * floor(x / y))`                   | y ≠ 0          |
| `x < y`             | int, int           | bool        | `(1 - sign(x - y)) / 2`                    | x - y ≠ -0.5   |
| `x <= y`            | int, int           | bool        | `(1 - signn(x - y)) / 2`                   | x - y ≠ 0.5    |
| `x > y`             | int, int           | bool        | `(1 + signn(x - y)) / 2`                   | x - y ≠ 0.5    |
| `x >= y`            | int, int           | bool        | `(1 + sign(x - y)) / 2`                    | x - y ≠ -0.5   |
| `x <: y`            | float, float       | bool        | `(1 - signf(x - y)) / 2`                   | x - y ≠ 0      |
| `x >: y`            | float, float       | bool        | `(1 + signf(x - y)) / 2`                   | x - y ≠ 0      |
| `x == y`, `x = y`   | int, int           | bool        | `(x >= y) * (x <= y)`                      | x - y ≠ ±0.5   |
| `x != y`, `x <> y`  | int, int           | bool        | `(4 - (1+sign(x-y)) * (1-signn(x-y))) / 4` | x - y ≠ ±0.5   |
| `x && y`, `x and y` | bool, bool         | bool        | `x * y`                                    | x, y = [0, 1]  |
| `x || y`, `x or y`  | bool, bool         | bool        | `1 - (1 - x) * (1 - y)`                    | x, y = [0, 1]  |
| `if(b ? t : f)`     | bool, float, float | float       | `b * (t - f) + f`                          | ℝ              |
| `if(b ? t)`         | bool, float        | float       | `b * t`                                    | ℝ              |

## Formal Grammar
```ebnf
program =
    function { function }
    ;

function =
    [ "function" | "def" | "double" ] ID "(" [ ID { [ "," ] ID } ] ")" [ ":" | "{" ]
    { statement [ ";" ] }
    "return" expression [ ";" ]
    [ "}" ]
    ;

statement =
    ID "=" expression
    ;

expression =
    "if" "(" expression ( "?" | "," ) expression [ ( ":" | "," ) expression ] ")"
    | or_expression
    ;

or_expression =
    and_expression { ( "||" | "or" ) and_expression }
    ;

and_expression =
    equ_expression { ( "&&" | "and" ) equ_expression }
    ;

equ_expression =
    rel_expression { ( "==" | "=" | "!=" | "<>" ) rel_expression }
    ;

rel_expression =
    add_expression { ( "<=" | ">=" | "<:" | ">:" | "<" | ">" ) add_expression }
    ;

add_expression =
    mult_expression { ( "+" | "-" ) mult_expression }
    ;

mult_expression =
    exp_expression { ( "*" | "/" | "%" ) exp_expression }
    ;

exp_expression =
    unary_expression { "^" unary_expression }
    ;

unary_expression =
    "-" primary_expression
    | ( "!" | "not" ) primary_expression
    | primary_expression
    ;

primary_expression =
    "(" expression ")"
    | ID [ "(" [ expression { [ "," ] expression } ] ")" ]
    | NUM
    | TAG
    ;
```    

