r"""Support for basic arithmetic in expressions.  For example,
simplification of linear combinations and monomials.
"""

from numbers import Number
from fractions import Fraction
from .core import *

__all__ = [
    "sqrt", "exp", "ln", "E", "Pi", "I", "sin", "cos",
    "pow", "py_pow",
    "abs", "py_abs",
    "N"
]

def split_summand(a):
    """Helper function for `rule_plus_collect`.  Gives a (coeff, expr)
    pair for a given expression.  Assumes the expression has been
    already evaluated."""
    if head(a) == "Times" and len(a.args) >= 2 and head(a.args[0]) == "number":
        if len(a.args) == 2:
            return (a.args[0], a.args[1])
        else:
            return (a.args[0], expr("Times", *a.args[1:]))
    elif head(a) == "number":
        return (a, 1)
    else:
        return (1, a)

@downvalue("Plus")
def rule_plus_collect(*args):
    """Collect monomials, adding numeric coefficients of repeated monomials."""
    terms = []
    for a in args:
        coeff, b = split_summand(a)
        for i, (c, t) in enumerate(terms):
            if b == t:
                terms[i] = (c + coeff, t)
                break
        else:
            terms.append((coeff, b))
    args2 = []
    for c, t in terms:
        t = c * t
        if t != 0:
            args2.append(t)
    if len(args2) == 0:
        return 0
    elif len(args2) == 1:
        return args2[0]
    else:
        return expr("Plus", *args2)

def split_multiplicand(a):
    """Helper function for `rule_times_collect`.  Returns (power, expr)."""
    if head(a) == "Pow":
        return (a.args[1], a.args[0])
    else:
        return (1, a)

@downvalue("Times")
def rule_times_collect(*args):
    """Collect multiplicands of the product, combining exponents."""
    # collect all powers
    # terms is a list of (value, exponent) pairs
    terms = []
    coeff = 1
    num_matrices = 0
    for a in args:
        exp, val = split_multiplicand(a)
        if head(val) == "matrix":
            num_matrices += 1
            if num_matrices > 1:
                raise ValueError("Use the @ operator to multiply matrices rather than *.")
        if exp == 1 and head(val) == "number":
            coeff *= val
        else:
            for i, (e, v) in enumerate(terms):
                if val == v:
                    terms[i] = (exp + e, v)
                    break
            else:
                terms.append((exp, val))
    if coeff == 0:
        return 0
    args2 = []
    if coeff != 1:
        args2.append(coeff)
    for e, v in terms:
        if e == 1: # special case for things like non-square matrices
            pass
        else:
            v = pow(v, e)
        if v != 1:
            args2.append(v)
    if len(args2) == 0:
        return 1
    elif len(args2) == 1:
        return args2[0]
    else:
        # sort args2 so that most functions occur last
        nums = []
        args = []
        fns = []
        for arg in args2:
            if head(arg) == "number":
                nums.append(arg)
            elif head(arg) == "pow" and head(arg.args[0]) == "number":
                nums.append(arg)
            elif head(arg) in ("var", "const", "Plus", "Times", "Pow"):
                args.append(arg)
            else:
                fns.append(arg)
        return expr("Times", *nums, *args, *fns)

def iroot(a, n):
    """Give the largest integer k such that k**n <= a."""
    assert a >= 0
    lo = 0
    hi = a
    while True:
        if lo == hi:
            return lo
        k = (lo + hi)//2
        kn = k**n
        kn1 = (k + 1)**n
        if kn <= a < kn1:
            return k
        elif kn1 <= a:
            hi = k - 1
        else:
            lo = k + 1

def factors(a):
    """Gives the prime factors of a.  Returns a list of `[(p, n), ...]` where `a = p**n * ...`.
    If `a` is negative, then one entry will be `(-1, 1)`."""

    assert type(a) == int

    factors = []
    if a < 0:
        a = -a
        factors.append((-1, 1))

    n2 = 0
    while a & 1 == 0:
        n2 += 1
        a = a >> 1
    if n2:
        factors.append((2, n2))

    p = 3
    while p <= a:
        n = 0
        while a % p == 0:
            n += 1
            a = a // p
        if n:
            factors.append((p, n))
        p += 2 # our numbers are small. should be ok.

    return factors

@downvalue("Pow")
def rule_pow_constants(a, b):
    """Compute powers when numeric constants are present."""

    if a == 0:
        return 1

    if b == 1:
        return a

    if head(a) == "number" and a < 0:
        return pow(-a, b) * pow(I, 2*b)

    if type(a) in (int, Fraction) and type(b) == int:
        return Fraction(a) ** b

    if type(a) in (int, Fraction) and type(b) == Fraction:
        ap, aq = Fraction(a).as_integer_ratio()
        bp, bq = b.as_integer_ratio()

        if bp < 0:
            bp = -bp
            ap, aq = aq, ap

        out = Fraction(1)
        stay = Fraction(1)

        for p, n in factors(ap):
            out = out * p**(n * bp // bq)
            stay = stay * p**(n * bp % bq)
        for p, n in factors(aq):
            out = out / p**(n * bp // bq)
            stay = stay / p**(n * bp % bq)

        if stay == 1:
            return out
        elif out == 1:
            # no change
            raise Inapplicable
        else:
            return out * pow(stay, Fraction(1, bq))

    if type(a) == float or type(b) == float:
        return a ** b

    raise Inapplicable

@downvalue("Pow")
def rule_pow_pow(a, b):
    """`(a0 ** a1) ** b == a0 ** (a1 * b)`"""
    if head(a) == "Pow":
        return expr("Pow", a.args[0], a.args[1] * b)
    else:
        raise Inapplicable

@downvalue("Pow")
def rule_mul_pow(a, b):
    """`(a0 * a1) ** b == a0**b * a1**b` if `b` is a number"""
    if head(a) == "Times" and head(b) == "number":
        return pow(a.args[0], b) * pow(a.args[1], b)
    else:
        raise Inapplicable


E = const("e")
Pi = const(r"\pi")
I = const("i")

@downvalue("Pow")
def rule_I_pow(a, b):
    if a == I and type(b) == int:
        b = b % 4
        if b == 0:
            return 1
        elif b == 1:
            return I
        elif b == 2:
            return -1
        else:
            return -I
    else:
        raise Inapplicable

# TODO: add rationalization of complex divisors
#@downvalue("Pow")
#def rule_I_div(a, b):
#    if not (type(b) == int and b < 0):
#        raise Inapplicable
#    if 

def sqrt(x):
    """The square root function.  Essentially returns `x ** frac(1, 2)`, but is a
    little careful to ensure things remain exact."""
    return evaluate(expr("Pow", x, Fraction(1, 2)))

def exp(x):
    """The exponential function with base *e*, referred to using `E`.  Just returns `E ** x`."""
    return E ** x

@downvalue("ln", def_expr=True)
def ln(x):
    """The natural logarithm.  The base of the logarithm is referred to by `E`."""
    if x == 0:
        raise ValueError("ln(0) is undefined")
    elif x == 1:
        return 0
    elif x == E:
        return 1
    elif head(x) == "Pow" and x.args[0] == E: # simplification: ln(E ** t) == t
        return x.args[1]
    else:
        raise Inapplicable

@downvalue("Pow")
def rule_exp_ln(a, b):
    """Assumes x is in the correct domain, simplifying `E ** ln(x) == x`."""
    if a == E and head(b) == "ln":
        return b.args[0]
    else:
        raise Inapplicable

@downvalue("sin", def_expr=True)
def sin(x):
    """The sine function."""
    if x == 0:
        return 0
    else:
        raise Inapplicable

@downvalue("cos", def_expr=True)
def cos(x):
    """The cosine function."""
    if x == 0:
        return 1
    else:
        raise Inapplicable

py_abs = abs
r"""This is the built-in Python abs function.  We replace it with our own to avoid confusion."""

@downvalue("abs", def_expr=True)
def abs(x):
    """The absolute value of the argument."""
    if head(x) == "number":
        return py_abs(x)
    else:
        raise Inapplicable

def N(x):
    """Convert all numbers in the expression to floating-point numbers.

    Example:
    ```python
    print(sqrt(2)) # gives "2^{1/2}"
    print(N(sqrt(2))) # gives "1.4142135623730951"
    ```

    If there are partially evaluated symbolic expressions, this can potentially cause issues.
    For example, some of the arguments in a "Deriv" expression must be integers.
    """
    if head(x) == "number":
        return float(x)
    elif head(x) == "list":
        return [N(a) for a in x]
    elif isinstance(x, Expr):
        return evaluate(Expr(x.head, [N(a) for a in x.args]))
    else:
        return x
