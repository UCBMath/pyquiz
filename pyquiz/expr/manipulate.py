r"""
Functions for manipulating expressions.
"""

import itertools
from .core import *

__all__ = [
    "replace",
    "expand",
    "collect"
]

def replace(e, *repls):
    """Each argument after the first is a pair `(p, v)`, and every occurrence of `p` in `e` is replaced by `v`.
    Similar to Replace in Mathematica.

    Example:
    ```python
    a = var("a")
    b = var("b")
    f = a**2 + a*b + a
    print(replace(f, (a, 2), (b, 3)))
    ```
    """
    for pair in repls:
        if type(pair) != tuple or len(pair) != 2:
            raise ValueError("Each replacement must be a tuple of two elements.")
        if e == pair[0]:
            return pair[1]
    if isinstance(e, Expr):
        return evaluate(Expr(replace(e.head, *repls), [replace(a, *repls) for a in e.args]))
    elif head(e) == "list":
        return [replace(a, *repls) for a in e]
    else:
        return e

def expand(e):
    """Mathematica-like `ExpandAll`.  Distributes multiplications over additions everywhere in the expression."""
    if head(e) in ("number", "string"):
        return e
    elif head(e) == "list":
        return [expand(x) for x in e]
    elif type(e) != Expr:
        raise ValueError(f"Unknown type of value ({type(e)!r}) to expand.")

    args = [expand(a) for a in e.args]

    if e.head == "Times":
        for i, a in enumerate(args):
            if head(a) == "Plus":
                rest = expand(evaluate(expr("Times", *args[:i], *args[i+1:])))
                val = 0
                for b in a.args:
                    val += expand(b * rest)
                return val

    if e.head == "Pow" and type(e.args[1]) == int and e.args[1] != -1 and head(e.args[0]) == "Plus":
        new_exp = e.args[1] + (-1 if e.args[1] > 0 else 1)
        rest = expand(evaluate(expr("Pow", e.args[0], new_exp)))
        val = 0
        for b in e.args[0].args:
            val += expand(b * rest)
        return val

    return evaluate(Expr(e.head, args))

def collect_coeffs_rebuild(pr, vars):
    """(internal) Given the polynomial representation from
    `collect_coeffs`, turn it back into an expression."""

    res = 0
    for c, mon in pr:
        if c != 0:
            res += expr("Times", c, *(pow(v, e) for v,e in zip(vars, mon)))
    return res

def collect_coeffs(x, vars):
    """(internal) Helper for `collect`."""

    # extract a polynomial representation of x
    # type: [(coeff, (exps...))]
    # where (exps...) represents exponents for the list of `vars`.

    def add_to(cs1, cs2):
        # add polynomial representation `cs2` to `cs1`, mutating `cs1`.
        for c2, mon2 in cs2:
            for i, (c1, mon1) in enumerate(cs1):
                if mon1 == mon2:
                    cs1[i] = (c1 + c2, mon1)
                    break
            else:
                cs1.append((c2, mon2))
        return cs1

    def del_zeroes(cs):
        # remove terms with zero coefficient from `cs`, mutating it.
        for i in range(len(cs)-1, -1, -1):
            if cs[i][0] == 0:
                del cs[i]
        return cs

    def sort_cs(cs):
        # put all the all-number exponents first, and lexicographically sort them in decreasing order
        num_cs = []
        rest_cs = []
        for c, mon in cs:
            if all(head(e) == "number" for e in mon):
                num_cs.append((c, mon))
            else:
                rest_cs.append((c, mon))
        num_cs.sort(key=lambda p: p[1], reverse=True)
        num_cs.extend(rest_cs)
        return num_cs

    def collect_core(x):
        if x in vars:
            i = vars.index(x)
            mon = tuple(int(i == j) for j in range(len(vars)))
            return [(1, mon)]
        elif head(x) == "Plus":
            cs = []
            for a in x.args:
                add_to(cs, collect_core(a))
            return del_zeroes(cs)
        elif head(x) == "Times":
            cs = []
            for distr in itertools.product(*(collect_core(a) for a in x.args)):
                mon2 = tuple(0 for v in vars)
                c2 = 1
                for c, mon in distr:
                    mon2 = tuple(a + b for a,b in zip(mon2, mon))
                    c2 *= c
                #print("times c2 = " + repr(c2))
                add_to(cs, [(c2, mon2)])
            return del_zeroes(cs)
        elif head(x) == "Pow":
            a, b = x.args
            if b == 0:
                return collect_core(1)

            if type(b) == int:
                if b < 0:
                    neg = True
                    b = -b
                else:
                    neg = False
                assert b > 0
                ac = collect_core(expr("Times", *(a for i in range(b))))
                if neg:
                    if len(ac) == 0:
                        return []
                    elif len(ac) == 1:
                        [(c, mon)] = ac
                        return [(pow(c, -1), tuple(-e for e in mon))]
                    else:
                        return [(pow(collect_coeffs_rebuild(ac, vars), -1), tuple(0 for v in vars))]
                else:
                    return ac
            else:
                ac = collect_core(a)
                return [(pow(collect_coeffs_rebuild(ac, vars), b), tuple(0 for v in vars))]

        else:
            return [(x, tuple(0 for v in vars))]

    return sort_cs(collect_core(x))

def collect(x, vars=None, *, f=None):
    """Collect terms of the polynomial `x`.  The `vars` argument is an
    array of expressions used as the variables, and if it is `None` it
    is the collection of all `var` terms in the expression.  The `f`
    function is applied to each coefficient; `collect` will not
    re-collect after `f` is applied.

    If `x` is a list or matrix, `collect` will apply to each element.

    If there are symbolic exponents, `collect` might give unexpected
    results since it does not try hard at all to tell when symbolic
    expressions are equivalent.

    Example:
    ```python
    x = var("x")
    y = var("y")
    collect((x + y)*(x - y), [x, y])
    ```
    If you leave off `[x, y]`, then `collect((x + y)*(x - y))` will automatically choose the variable list.

    Example:
    ```python
    x = var("x")
    collect((x - (4+3*I)) * (x - (4-3*I)), f=expand)
    ```
    This uses `expand` to simplify the coefficients.

    See also: `expand`
    """

    if vars != None and not isinstance(vars, list):
        raise ValueError("vars argument should be None or a list")

    if vars == None:
        # get all variables in the expression
        def find_vars(x):
            if head(x) == "var":
                yield x.args[0]
            elif isinstance(x, Expr):
                for a in x.args:
                    yield from find_vars(a)
            else:
                pass
        var_names = list(set(find_vars(x)))
        var_names.sort()
        vars = [var(name) for name in var_names]

    if head(x) == "list":
        return [collect(e, vars=vars, f=f) for e in x]
    elif head(x) == "matrix":
        return matrix(*([collect(e, vars=vars, f=f) for e in row] for row in x))

    cs = []
    for c, mon in collect_coeffs(x, vars):
        if f:
            cs.append((f(c), mon))
        else:
            cs.append((c, mon))
    return collect_coeffs_rebuild(cs, vars)
