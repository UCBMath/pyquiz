r"""Support for basic arithmetic in expressions.  For example,
simplification of linear combinations and monomials.
"""

from numbers import Number
from fractions import Fraction
from .core import *

__all__ = [
    "exp", "ln", "E"
]

def split_summand(a):
    """Helper function for `rule_plus_collect`.  Gives a (coeff, expr)
    pair for a given expression.  Assumes the expression has been
    already evaluated."""
    if head(a) == "Times" and len(a.args) >= 2 and isinstance(a.args[0], Number):
        if len(a.args) == 2:
            return (a.args[0], a.args[1])
        else:
            return (a.args[0], expr("Times", *a.args[1:]))
    elif isinstance(a, Number):
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
    for a in args:
        exp, val = split_multiplicand(a)
        if exp == 1 and isinstance(val, Number):
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
        v = v ** e
        if v != 1:
            args2.append(v)
    if len(args2) == 0:
        return 1
    elif len(args2) == 1:
        return args2[0]
    else:
        # sort args2 so that most functions occur last
        args3 = []
        fns = []
        for arg in args2:
            if head(arg) in ("number", "var", "const", "Plus", "Times", "Pow"):
                args3.append(arg)
            else:
                fns.append(arg)
        return expr("Times", *args3, *fns)

@downvalue("Pow")
def rule_pow_constants(a, b):
    """Compute powers when constants are present."""
    if a == 0:
        return 1
    elif b == 1:
        return a
    elif type(a) == int and isinstance(b, Number):
        # This ensures it will be exact if possible.
        return Fraction(a) ** b
    elif isinstance(a, Number) and isinstance(b, Number):
        return a ** b
    else:
        raise Inapplicable

@downvalue("Pow")
def rule_pow_pow(a, b):
    """`(a0 ** a1) ** b == a0 ** (a1 * b)`"""
    if head(a) == "Pow":
        return a.args[0] ** (a.args[1] * b)
    else:
        raise Inapplicable

E = const("e")

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

