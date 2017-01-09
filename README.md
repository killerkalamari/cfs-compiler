# cfs-compiler
Compiles Closed-Form Script to a closed-form expression compatible with Facer.

### Table of Contents
[Operator Precedence](#operator-precedence)

[Internal Functions](#internal-functions)

[Grammar](#grammar)

## Operator Precedence
| Precedence | Operators                        | Description                            |
| ---------- | -------------------------------- | -------------------------------------- |
| 1          | `()`, `f()`                      | parentheses, function calls            |
| 2          | `-`                              | unary minus                            |
| 3          | `^`                              | exponentiation                         |
| 4          | `*`, `/`, `%`                    | multiplication, division, modulo       |
| 5          | `+`, `-`                         | addition, subtraction                  |
| 6          | `<`, `<=`, `>`, `>=`, `<.`, `>.` | int comparisons, float comparisons     |
| 7          | `==`, `=`, `!=`, `<>`            | int comparisons                        |
| 8          | `if(?)`, `if(?:)`                | binary and ternary conditionals        |

## Internal Functions
| Function           | Input Types        | Output Type | Implementation                             | Domain         |
| ------------------ | ------------------ | ----------- | -------------------------------------------| -------------- |
| `acosd(x)`         | float              | float       | `deg(acos(x))`                             | −1 ≤ x ≤ 1     |
| `asind(x)`         | float              | float       | `deg(asin(x))`                             | −1 ≤ x ≤ 1     |
| `atan2(y, x)`      | float, float       | float       | `atan(y / x) + (x <. 0) * signf(y) * pi`   | x ≠ 0, y ≠ 0   |
| `atan2d(y, x)`     | float, float       | float       | `deg(atan2(y, x))`                         | x ≠ 0, y ≠ 0   |
| `atand(x)`         | float              | float       | `deg(atan(x))`                             | ℝ              |
| `cosd(θ)`          | float              | float       | `cos(rad(θ))`                              | ℝ              |
| `if(b ? t : f)`    | bool, float, float | float       | `b * (t - f) + f`                          | ℝ              |
| `if(b ? t)`        | bool, float        | float       | `b * t`                                    | ℝ              |
| `int(x)`           | float              | int         | `floor(x) + (1 - sign(floor(x))) / 2`      | ℝ              |
| `sind(θ)`          | float              | float       | `sin(rad(θ))`                              | ℝ              |
| `sign(i)`          | int                | int         | `signf(i + 0.5)`                           | x ≠ -0.5       |
| `signf(x)`         | float              | int         | `abs(x) / x`                               | x ≠ 0          |
| `signn(i)`         | int                | int         | `signf(i - 0.5)`                           | x ≠ 0.5        |
| `tand(θ)`          | float              | float       | `tan(rad(θ))`                              | x ≠ π/2 + *k*π |
| `x % y`            | float, float       | float       | `x - (y * floor(x / y))`                   | y ≠ 0          |
| `x < y`            | int, int           | bool        | `(1 - sign(x - y)) / 2`                    | x - y ≠ -0.5   |
| `x <= y`           | int, int           | bool        | `(1 - signn(x - y)) / 2`                   | x - y ≠ 0.5    |
| `x > y`            | int, int           | bool        | `(1 + signn(x - y)) / 2`                   | x - y ≠ 0.5    |
| `x >= y`           | int, int           | bool        | `(1 + sign(x - y)) / 2`                    | x - y ≠ -0.5   |
| `x <. y`           | float, float       | bool        | `(1 - signf(x - y)) / 2`                   | x - y ≠ 0      |
| `x >. y`           | float, float       | bool        | `(1 + signf(x - y)) / 2`                   | x - y ≠ 0      |
| `x == y`, `x = y`  | int, int           | bool        | `(x >= y) * (x <= y)`                      | x - y ≠ ±0.5   |
| `x != y`, `x <> y` | int, int           | bool        | `(4 - (1+sign(x-y)) * (1-signn(x-y))) / 4` | x - y ≠ ±0.5   |

## Grammar
```ebnf
program =
    function { function }
    ;

function =
    "function" ID "(" [ ID { "," ID } ] ")" ␤ { statement ␤ } "return" expression ␤
    ;

statement =
    ID "=" expression
    ;

expression =
    "if" "(" expression "?" expression [ ":" expression ] ")"
    | equ_expression
    ;

equ_expression =
    rel_expression { ( "==" | "=" | "!=" | "<>" ) rel_expression }
    ;

rel_expression =
    add_expression { ( "<" | "<=" | ">" | ">=" | "<." | ">." ) add_expression }
    ;

add_expression =
    mult_expression { ( "+" | "-" ) mult_expression }
    ;

mult_expression =
    exp_expression { ( "*" | "/" | "%" ) exp_expression }
    ;

exp_expression =
    unary_expression [ "^" unary_expression ]
    ;

unary_expression =
    "-" primary_expression
    | primary_expression
    ;

primary_expression =
    "(" expression ")"
    | ID [ "(" [ expression { "," expression } ] ")" ]
    | NUM
    | TAG
    ;
```    
