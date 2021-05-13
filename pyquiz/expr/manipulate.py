r"""
Functions for manipulating expressions.
"""

from numbers import Number
from .core import *

__all__ = [
    "replace",
    "expand"
]

def replace(e, p, v):
    """Every occurrence of `p` in the expression `e` is replaced by `v`. Similar to Replace in Mathematica."""
    if e == p:
        return v
    if isinstance(e, Expr):
        return evaluate(Expr(replace(e.head, p, v), [replace(a, p, v) for a in e.args]))
    elif head(e) == "list":
        return [replace(a, p, v) for a in e]
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
