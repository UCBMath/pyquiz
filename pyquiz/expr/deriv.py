r"""
Symbolic differentiation and differential equations.

Exports the variable `t` for convenience.
"""

from .core import *
from .arith import *

__all__ = [
    "Dt", "t"
]

t = var("t")

def normalize_deriv_spec(spec):
    """Combine variables, and remove any variables for which we're taking
    the 0th derivative."""
    spec2 = []
    for v, n in spec:
        assert head(v) == "var"
        for i, (v2, n2) in enumerate(spec2):
            if v == v2:
                spec2[i] = [v, n + n2]
                break
        else:
            spec2.append([v, n])
    # delete entries for 0th derivatives
    for i in range(len(spec2) - 1, -1, -1):
        if spec2[i][1] == 0:
            del spec2[i]
    return spec2

def Dt(e, *spec, constants=[]):
    """The total derivative of the expression `e` according to the
    specification `spec`.  This is akin to Mathematica's `Dt`.  All
    variables (`var`) are assumed to be functions of `v` unless they
    are present in the `constants` list.  Every constant (`const`) is
    a constant.

    * `Dt(e, v)` is `d/dv e`
    * `Dt(e, v1, v2, ...)` is `d/dv1 d/dv2 ... e`
    * `Dt(e, (v, n))` is `d^n/dv^n e`

    """
    assert all(head(x) == "var" for x in constants)

    spec = list(spec)

    for i, s in enumerate(spec):
        if head(s) == "var":
            v, n = s, 1
        elif type(s) in (tuple, list):
            if len(s) != 2:
                raise ValueError("tuple in spec should have length 2")
            v, n = s
        else:
            raise ValueError("unexpected item in spec")

        if head(v) != "var":
            raise ValueError("can only take derivatives with respect to variables")

        spec[i] = [v, n]

    return evaluate(expr("Deriv", e, spec, constants))

def split_spec(spec):
    """Returns `(spec2, v)`, where `spec` is equivalent to `[*spec2, (v, 1)]`,
    or `(spec, None)` if it can't be done.
    Chooses the last element of the spec with an `int`."""
    for i in range(len(spec) - 1, -1, -1):
        v, n = spec[i]
        if type(n) == int:
            if n < 0:
                raise ValueError(f"The derivative spec ({v}, {n}) is negative.")
            elif n == 1:
                return (spec[:i] + spec[i+1:], v)
            else:
                return (spec[:i] + [(v, n - 1)] + spec[i+1:], v)
    return (spec, None)

def spec_for_var(spec, var):
    """For a spec and a variable, returns (spec2, n) where n is the number
    of times it says to take the derivative for that variable (0 by
    default)."""
    for i, (v, n) in enumerate(spec):
        if v == var:
            return (spec[:i] + spec[i+1:], n)
    return (spec, 0)

@downvalue("Deriv")
def rule_deriv_basic(e, spec, constants):
    spec2 = normalize_deriv_spec(spec)
    if spec2 != spec:
        return expr("Deriv", e, spec2, constants)
    elif len(spec) == 0:
        return e
    elif head(e) == "number" or head(e) == "const":
        spec2, v = split_spec(spec)
        if v == None:
            raise Inapplicable
        else:
            return 0
    elif head(e) == "var":
        if e in constants:
            return 0
        spec2, n = spec_for_var(spec, e)
        if type(n) == int:
            if n > 1:
                return 0
            elif n == 1:
                return expr("Deriv", 1, spec2, constants)
        raise Inapplicable
    elif head(e) == "Deriv" and e.args[2] == constants:
        # join the derivatives
        return expr("Deriv", e.args[0], spec + e.args[1], constants)
    elif head(e) == "Plus":
        return Expr("Plus", [expr("Deriv", x, spec, constants) for x in e])
    elif head(e) == "Times":
        spec2, v = split_spec(spec)
        if v == None:
            raise Inapplicable
        deriv = 0
        for i in range(len(e.args)):
            deriv += expr("Times", *e.args[:i], expr("Deriv", e.args[i], [(v, 1)], constants), *e.args[i+1:])
        return expr("Deriv", deriv, spec2, constants)
    elif head(e) == "Pow":
        spec2, v = split_spec(spec)
        if v == None:
            raise Inapplicable
        a, b = e.args
        da = expr("Deriv", a, [(v, 1)], constants)
        db = expr("Deriv", b, [(v, 1)], constants)
        deriv = b * a**(b - 1) * da + a**b * ln(a) * db
        return expr("Deriv", deriv, spec2, constants)
    else:
        raise Inapplicable
