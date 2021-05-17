r"""
Symbolic differentiation and differential equations.

Exports the variable `t` for convenience.
"""

from .core import *
from .arith import *

__all__ = [
    "D"
]

def D(e, *spec, constants=[]):
    """The total derivative of the expression `e` according to the
    specification `spec`.  This is akin to Mathematica's `Dt`.  All
    variables (`var`) are assumed to be functions of the variables in the spec
    unless they are present in the `constants` list.  Every constant (`const`) is
    a constant.  Variables in the spec are assumed not to be functions of the
    other spec variables.

    * `D(e, v)` is `d/dv e`
    * `D(e, v1, v2, ...)` is `d/dv1 d/dv2 ... e`
    * `D(e, [v, n])` is `d^n/dv^n e`

    A `[v, 0]` spec entry indicates that `v` is an independent variable.  For example,
    `D(x*y, [x, 0], y)` gives `x`, where `D(x*y, y)` gives `D(x, y)*y + x`.

    It is fine having symbolic expressions in the specification.

    All functions are presumed to be smooth enough to permit changes in
    the order of differentiation.
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

def normalize_deriv_spec(spec):
    """Combine variables.  (We don't remove any variables for which we're
    taking the 0th derivative.)  Raises an exception if the spec is obviously invalid."""
    spec2 = []
    for v, n in spec:
        assert head(v) == "var"
        if head(n) == "number":
            if type(n) != int:
                raise ValueError(f"The derivative spec ({v}, {n}) is fractional.")
            if n < 0:
                raise ValueError(f"The derivative spec ({v}, {n}) is negative.")

        for i, (v2, n2) in enumerate(spec2):
            if v == v2:
                spec2[i] = [v, n + n2]
                break
        else:
            spec2.append([v, n])

    return spec2

def split_spec(spec):
    """Returns `(spec2, v)`, where `spec` is equivalent to `[*spec2, (v, 1)]`,
    or `(spec, None)` if it can't be done.
    Chooses the last element of the spec with an `int`.  Leaves a 0 entry in `spec2`."""
    for i in range(len(spec) - 1, -1, -1):
        v, n = spec[i]
        if type(n) == int and n > 0:
            return (spec[:i] + [(v, n - 1)] + spec[i+1:], v)
    return (spec, None)

def spec_for_var(spec, var):
    """For a spec and a variable, returns `(spec2, n, present)` where n is
    the number of times it says to take the derivative for that
    variable (0 by default) and `present` is a boolean representing
    whether or not the variable is in the spec.  Sets the variable in
    `spec2` to 0, if it was present."""
    for i, (v, n) in enumerate(spec):
        if v == var:
            return (spec[:i] + [(v, 0)] + spec[i+1:], n, True)
    return (spec, 0, False)

def zeroed_spec(spec):
    """Return a zeroed-out version of the spec to keep track of the independent variables."""
    return [(v, 0) for v, n in spec]

fn_derivs = {
    ("Pow", 2): lambda a, b: [b * pow(a, b - 1), pow(a, b * ln(a))],
    ("ln", 1): lambda a: [frac(1, a)],
    ("cos", 1): lambda a: [sin(a)],
    ("sin", 1): lambda a: [-cos(a)]
}
r"""`fn_derivs` gives derivatives of various functions.  The key is a
(head, arity) pair, and the value is a function that takes the point
at which the derivative is taken and returns the Jacobian (a "row
vector" as a list).
"""

@downvalue("Deriv")
def rule_deriv_basic(e, spec, constants):
    spec, old_spec = normalize_deriv_spec(spec), spec
    if spec != old_spec:
        # restart evaluation with new expression
        return expr("Deriv", e, spec, constants)
    elif sum(n for v, n in spec) == 0:  # (**)
        return e
    elif (head(e) == "number" or head(e) == "const"
          or (head(e) == "Part" and head(e.args[0]) == "const")):
        spec2, v = split_spec(spec)
        if v == None:
            # inconclusive (symbolic values)
            raise Inapplicable
        else:
            return 0
    elif head(e) == "var":
        if e in constants:
            return 0
        spec2, n, present = spec_for_var(spec, e)
        if type(n) == int:
            if n == 0 and present:
                # Since (**) is false, then this is an independent
                # variable's derivative with respect to another
                # variable.
                return 0
            elif n > 1:
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
            deriv += expr("Times",
                          *e.args[:i],
                          expr("Deriv", e.args[i], zeroed_spec(spec) + [(v, 1)], constants),
                          *e.args[i+1:])
        return expr("Deriv", deriv, spec2, constants)
    elif head(e) == "Part":
        # assume the index is discrete, so plays no role in the derivative
        return expr("Part", expr("Deriv", e.args[0], spec, constants), *e.args[1:])
    elif isinstance(e, Expr) and (head(e), len(e.args)) in fn_derivs:
        spec2, v = split_spec(spec)
        if v == None:
            raise Inapplicable
        de = fn_derivs[(head(e), len(e.args))](*e.args)
        ds = [expr("Deriv", a, zeroed_spec(spec) + [(v, 1)], constants) for a in e.args]
        assert len(de) == len(ds)
        deriv = sum(a*b for a,b in zip(de, ds))
        return expr("Deriv", deriv, spec2, constants)
    else:
        raise Inapplicable
