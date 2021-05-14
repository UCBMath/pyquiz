r"""
The function `tex` gives the LaTeX form of an expression.


"""

from collections import defaultdict
from fractions import Fraction
from .core import *

__all__ = [
    "tex",
    "tex_vector_as_tuple",
    "tex_deriv_use_primes",
    "tex_deriv_indep_var",
    "tex_deriv_primes_limit"
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

TEX_DERIV_USE_PRIMES = True
TEX_DERIV_INDEP_VAR = var("t")
TEX_DERIV_PRIMES_LIMIT = 3

def tex_deriv_use_primes(state):
    r"""If `state` is `True` (the default), then derivatives with exactly
    one independent variable are rendered using prime notation, if
    that variable is the one set by `tex_deriv_indep_var`.
    """
    global TEX_DERIV_USE_PRIMES
    TEX_DERIV_USE_PRIMES = state

def tex_deriv_indep_var(var):
    r"""Set the independent variable used by the feature in `tex_deriv_use_primes`.
    By default, the variable is `var("t")`.
    """
    global TEX_DERIV_INDEP_VAR
    assert head(var) == "var"
    TEX_DERIV_INDEP_VAR = var

def tex_deriv_primes_limit(n):
    r"""When the `tex_deriv_use_primes` feature is active, gives point
    after which primes are instead rendered with parentheses.  By
    default, this is 3.  For example, the fourth derivative of `y`
    would be `y^{(4)}` rather than `y''''`.
    """
    global TEX_DERIV_PRIMES_LIMIT
    assert type(n) == int and n >= 0
    TEX_DERIV_PRIMES_LIMIT = n

# precedences:
# 20 add
# 30 mul
# 35 slash
# 40 frac
# 50 pow
# 60 subscripts

def parens(par_prec, prec, text):
    if par_prec > prec:
        return "\\left(" + text + "\\right)"
    else:
        return text

def tex_prec(prec, e, small):
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
        elif small:
            return parens(prec, 25, rf"{e.numerator}/{e.denominator}")
        else:
            return parens(prec, 40, rf"\tfrac{{{e.numerator}}}{{{e.denominator}}}")
    elif head(e) == "list":
        return "\\left[" + ",".join(tex_prec(0, x, small) for x in e) + "\\right]"
    elif isinstance(e, Expr):
        if e.head == "Plus":
            text = ""
            for i, a in enumerate(e):
                if head(a) == "Times" and len(a.args) >= 2 and head(a.args[0]) == "number":
                    if len(a.args) == 2:
                        coeff, b = a.args[0], a.args[1]
                    else:
                        coeff, b = a.args[0], expr("Times", *a.args[1:])
                elif head(a) == "number":
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
                    text += op + tex_prec(20, coeff, small)
                elif coeff == 1:
                    text += op + tex_prec(20, b, small)
                else:
                    text += op + tex_prec(30, coeff, small) + tex_prec(30, b, small)
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
                if head(exp) == "number" and exp <= 0:
                    denom.append((b, -exp))
                elif exp == 1 and head(b) == "number" and b < 0:
                    is_neg = True
                    if b != -1:
                        numer.append((-b, exp))
                else:
                    numer.append((b, exp))
            snumer = ""
            for i, (b, exp) in enumerate(numer):
                prec2 = 30 if len(numer) > 1 else (prec if len(denom) == 0 else 0)
                if i > 0 and head(b) == "number":
                    prec2 = 1000 # make sure it has parentheses
                if exp == 1:
                    snumer += tex_prec(prec2, b, small)
                else:
                    snumer += tex_prec(prec2, expr("Pow", b, exp), small)
            sdenom = ""
            for i, (b, exp) in enumerate(denom):
                prec2 = 30 if len(denom) > 1 else 0
                if i > 0 and head(b) == "number":
                    prec2 = 1000 # make sure it has parentheses
                if exp == 1:
                    sdenom += tex_prec(prec2, b, small)
                else:
                    sdenom += tex_prec(prec2, expr("Pow", b, exp), small)
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
            return parens(prec, 30, "".join([tex_prec(30, a, small) for a in e.args]))
        elif e.head == "Pow":
            return parens(prec, 49, tex_prec(50, e.args[0], small) + "^{" + tex_prec(0, e.args[1], True) + "}")
        elif e.head == "Part":
            return parens(prec, 60,
                          tex_prec(60, e.args[0], small) + "_{" + ",".join(tex_prec(0, x, True) for x in e.args[1:]) + "}")
        elif e.head == "var" or e.head == "const":
            return "{" + e.args[0] + "}"
        elif e.head == "matrix":
            if TEX_VECTOR_AS_TUPLE and is_vector(e):
                return "\\left(" + ",".join(tex_prec(0, row[0], small) for row in e.args) + "\\right)"
            return (r"\begin{bmatrix}"
                    + r"\\".join("&".join(tex_prec(0, x, True) for x in row) for row in e.args)
                    + r"\end{bmatrix}")
        elif e.head == "Deriv":
            x, spec, constants = e.args
            if TEX_DERIV_USE_PRIMES and len(spec) == 1 and spec[0][0] == TEX_DERIV_INDEP_VAR:
                n = spec[0][1]
                if type(n) == int and 1 <= n <= TEX_DERIV_PRIMES_LIMIT:
                    exp = "\\prime" * n
                else:
                    exp = "(" + tex_prec(0, n, True) + ")"
                return parens(prec, 49, tex_prec(50, e.args[0], small) + "^{" + exp + "}")
            if len(spec) == 1:
                d = "d"
            else:
                d = "\\partial"
            bottom = []
            s = 0
            for v, n in spec:
                if n == 0:
                    continue
                s += n
                if n == 1:
                    bottom.append(rf"{d} {tex_prec(30, v, small)}")
                else:
                    bottom.append(rf"{d} {tex_prec(30, v, small)}^{{{tex_prec(0, n, True)}}}")
            if s == 1:
                p = ""
            else:
                p = "^{" + tex_prec(0, s, True) + "}"
            top = rf"{d}{p} {tex_prec(30, x, small)}"
            bot = "\\,".join(bottom)
            return parens(prec, 40, rf"\frac{{{top}}}{{{bot}}}")
        elif isinstance(e.head, str):
            return (r"\operatorname{" + e.head + "}(" +
                    ", ".join(tex_prec(0, x, small) for x in e.args)
                    + ")")
        else:
            raise ValueError(f"unknown expression type {e.head} to tex")
    else:
        raise ValueError(f"unknown value to tex {e}")

def tex(e):
    """Return the TeX form of an expression."""
    return tex_prec(0, e, False)

if True:
    # A hack: monkey patch so that the string form of a Fraction is its TeX form
    Fraction.__str__ = lambda self: tex(self)
