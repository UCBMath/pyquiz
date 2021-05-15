r"""
Functions for manipulating expressions.
"""

from numbers import Number
from .core import *

__all__ = [
    "replace",
    "expand"
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
    if isinstance(e, Number) or isinstance(e, str):
        return e
    elif type(e) == list or type(e) == tuple:
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
