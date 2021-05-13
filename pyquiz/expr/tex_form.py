r"""
The function `tex` gives the LaTeX form of an expression.


"""

from collections import defaultdict
from numbers import Number
from fractions import Fraction
from .core import *

__all__ = [
    "tex", "tex_vector_as_tuple"
]

TEX_VECTOR_AS_TUPLE = False
def tex_vector_as_tuple(state):
    r"""Change the way in which vectors are rendered to TeX.  By default, they are rendered as column vectors.

    For example,
    ```python
    tex_vector_as_tuple(True)
    print(vector(1, 2))
    ```
    prints out "`(1,2)`" rather than "`\begin{bmatrix}1\\2\end{bmatrix}`".
    """
    global TEX_VECTOR_AS_TUPLE
    TEX_VECTOR_AS_TUPLE = state

# precedences:
# 20 add
# 30 mul
# 40 frac
# 50 pow
# 60 subscripts

def parens(par_prec, prec, text):
    if par_prec > prec:
        return "\\left(" + text + "\\right)"
    else:
        return text

def tex_prec(prec, e):
    """Returns the LaTeX form of an expression. The prec argument is the
    precedence of the expression that contains this one, and it's up to
    this function to add parentheses as necessary."""
    if type(e) == int:
        return str(e)
    elif type(e) == float:
        # should make it format the number according to some specification
        return str(e)
    elif type(e) == Fraction:
        if e.denominator == 1:
            return str(e.numerator)
        else:
            return parens(prec, 40, rf"\tfrac{{{e.numerator}}}{{{e.denominator}}}")
    elif isinstance(e, Expr):
        if e.head == "Plus":
            text = ""
            for i, a in enumerate(e):
                if head(a) == "Times" and len(a.args) >= 1 and isinstance(a.args[0], Number):
                    coeff, b = a.args[0], evaluate(expr("Times", *a.args[1:]))
                elif isinstance(a, Number):
                    coeff, b = a, 1
                else:
                    coeff, b = 1, a
                op = " + "
                if coeff == -1:
                    if i == 0:
                        op = "-" # then this is unary minus
                    else:
                        op = " - "
                    coeff = 1
                elif i == 0:
                    op = ""
                elif i > 0 and coeff < 0:
                    op = " - "
                    coeff = -coeff
                if b == 1:
                    text += op + tex_prec(20, coeff)
                elif coeff == 1:
                    text += op + tex_prec(20, b)
                else:
                    text += op + tex_prec(30, coeff) + tex_prec(30, b)
            if text == "":
                text = "0"
            return parens(prec, 20, text)
        elif e.head == "Times":
            numer = []
            denom = []
            is_neg = False
            for a in e:
                if head(a) == "Pow":
                    b, exp = a
                else:
                    b, exp = a, 1
                if isinstance(exp, Number) and exp <= 0:
                    denom.append((b, -exp))
                elif exp == 1 and b == -1:
                    is_neg = True
                else:
                    numer.append((b, exp))
            snumer = ""
            for b, exp in numer:
                prec2 = 30 if len(numer) > 1 else (prec if len(denom) == 0 else 0)
                if exp == 1:
                    snumer += tex_prec(prec2, b)
                else:
                    snumer += tex_prec(prec2, expr("Pow", b, exp))
            sdenom = ""
            for b, exp in denom:
                prec2 = 30 if len(denom) > 1 else 0
                if exp == 1:
                    sdenom += tex_prec(prec2, b)
                else:
                    sdenom += tex_prec(prec2, expr("Pow", b, exp))
            if len(numer) == 0 and len(denom) > 0:
                if is_neg:
                    return parens(prec, 20, rf"-\frac{{1}}{{{sdenom}}}")
                else:
                    return parens(prec, 40, rf"\frac{{1}}{{{sdenom}}}")
            elif len(denom) == 0 and len(numer) > 0:
                if is_neg:
                    return parens(prec, 20, rf"-{snumer}")
                else:
                    return snumer
            else:
                if is_neg:
                    return parens(prec, 20, rf"-\frac{{{snumer}}}{{{sdenom}}}")
                else:
                    return parens(prec, 40, rf"\frac{{{snumer}}}{{{sdenom}}}")
        elif e.head == "MatTimes":
            return parens(prec, 30, "".join([tex_prec(30, a) for a in e.args]))
        elif e.head == "Pow":
            return parens(prec, 50, tex_prec(50, e.args[0]) + "^{" + tex_prec(0, e.args[1]) + "}")
        elif e.head == "Part":
            return parens(prec, 60,
                          tex_prec(60, e.args[0]) + "_{" + ",".join(tex_prec(0, x) for x in e.args[1:]) + "}")
        elif e.head == "var" or e.head == "const":
            return e.args[0]
        elif e.head == "matrix":
            if TEX_VECTOR_AS_TUPLE and is_vector(e):
                return "\\left(" + ",".join(tex_prec(0, row[0]) for row in e.args) + "\\right)"
            return (r"\begin{bmatrix}"
                    + r"\\".join("&".join(tex_prec(0, x) for x in row) for row in e.args)
                    + r"\end{bmatrix}")
        elif e.head == "Deriv":
            x, spec, constants = e.args
            bottom = []
            s = 0
            for v, n in spec:
                s += n
                if n == 1:
                    bottom.append(rf"\partial {tex_prec(30, v)}")
                else:
                    bottom.append(rf"\partial {tex_prec(30, v)}^{{{n}}}")
            if s == 1:
                p = ""
            else:
                p = "^" + str(s)
            top = rf"\partial{p} {tex_prec(30, x)}"
            return parens(prec, 40, rf"\frac{{{top}}}{{{' '.join(bottom)}}}")
        elif isinstance(e.head, str):
            return (r"\operatorname{" + e.head + "}(" +
                    ", ".join(tex_prec(0, x) for x in e.args)
                    + ")")
        else:
            raise ValueError(f"unknown expression type {e.head} to tex")
    elif type(e) == list or type(e) == tuple:
        return "\\left[" + ",".join(tex_prec(0, x) for x in e) + "\\right]"
    else:
        raise ValueError(f"unknown value to tex {e}")

def tex(e):
    """Return the TeX form of an expression."""
    return tex_prec(0, e)

if True:
    # A hack: monkey patch so that the string form of a Fraction is its TeX form
    Fraction.__str__ = lambda self: tex(self)
