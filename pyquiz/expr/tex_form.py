r"""
The function `tex` gives the LaTeX form of an expression.

Note: this module changes `__str__` of `Fraction` to use `tex` instead.
"""

from collections import defaultdict
from fractions import Fraction
from .core import *
from pyquiz.expr.matrix import is_vector, nrows, ncols, vector_entries
import pyquiz.dynamic

__all__ = [
    "tex",
    "tex_vector_as_tuple",
    "tex_deriv_use_primes",
    "tex_deriv_indep_var",
    "tex_deriv_primes_limit",
    "vector_align",
    "tex_list"
]

DEFAULT_TEX_VECTOR_AS_TUPLE = False
def tex_vector_as_tuple(state):
    r"""Change the way in which vectors are rendered to TeX.  By default, they are rendered as column vectors.

    For example,
    ```python
    tex_vector_as_tuple(True)
    print(vector(1, 2))
    ```
    prints out "`(1,2)`" rather than "`\begin{bmatrix}1\\2\end{bmatrix}`".

    This is a dynamic variable.
    """
    pyquiz.dynamic.set("TEX_VECTOR_AS_TUPLE", state)
def TEX_VECTOR_AS_TUPLE():
    return pyquiz.dynamic.get("TEX_VECTOR_AS_TUPLE", DEFAULT_TEX_VECTOR_AS_TUPLE)

DEFAULT_TEX_DERIV_USE_PRIMES = True
DEFAULT_TEX_DERIV_INDEP_VAR = var("t")
DEFAULT_TEX_DERIV_PRIMES_LIMIT = 3

def tex_deriv_use_primes(state):
    r"""If `state` is `True` (the default), then derivatives with exactly
    one independent variable are rendered using prime notation, if
    that variable is the one set by `tex_deriv_indep_var`.

    This is a dynamic variable.
    """
    pyquiz.dynamic.set("TEX_DERIV_USE_PRIMES", state)
def TEX_DERIV_USE_PRIMES():
    return pyquiz.dynamic.get("TEX_DERIV_USE_PRIMES", DEFAULT_TEX_DERIV_USE_PRIMES)

def tex_deriv_indep_var(var):
    r"""Set the independent variable used by the feature in `tex_deriv_use_primes`.
    By default, the variable is `var("t")`.

    This is a dynamic variable.
    """
    if head(var) != "var":
        raise ValueError("Expecting var")
    pyquiz.dynamic.set("TEX_DERIV_INDEP_VAR", var)
def TEX_DERIV_INDEP_VAR():
    return pyquiz.dynamic.get("TEX_DERIV_INDEP_VAR", DEFAULT_TEX_DERIV_INDEP_VAR)

def tex_deriv_primes_limit(n):
    r"""When the `tex_deriv_use_primes` feature is active, gives point
    after which primes are instead rendered with parentheses.  By
    default, this is 3.  For example, the fourth derivative of `y`
    would be `y^{(4)}` rather than `y''''`.

    This is a dynamic variable.
    """
    if not (type(n) == int and n >= 0):
        raise ValueError("Expecting non-negative integer")
    pyquiz.dynamic.set("TEX_DERIV_PRIMES_LIMIT", n)
def TEX_DERIV_PRIMES_LIMIT():
    return pyquiz.dynamic.get("TEX_DERIV_PRIMES_LIMIT", DEFAULT_TEX_DERIV_PRIMES_LIMIT)

# precedences:
# 20 add
# 30 mul
# 33 dot
# 35 slash
# 40 frac
# 50 pow and transpose
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
            return parens(prec, 19, text) # make sure -(x+1)+2 doesn't appear as -x+1+2
        elif e.head == "Times":
            numer = []
            denom = []
            is_neg = False
            for a in e:
                if head(a) == "Pow":
                    b, exp = a
                else:
                    b, exp = a, 1
                if type(b) == Fraction and exp == 1:
                    p, q = b.as_integer_ratio()
                    if p < 0:
                        is_neg = not is_neg
                        p = -p
                    if p != 1:
                        numer.append((p, 1))
                    if q != 1:
                        denom.append((q, 1))
                elif head(exp) == "number" and exp <= 0:
                    denom.append((b, -exp))
                elif exp == 1 and head(b) == "number" and b < 0:
                    is_neg = not is_neg
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
        elif e.head == "transpose":
            return parens(prec, 49, tex_prec(50, e.args[0], small) + "^T")
        elif e.head == "dot":
            a, b = e.args
            return parens(prec, 33, tex_prec(33, a, small) + " \\cdot " + tex_prec(33, b, small))
        elif e.head == "Part":
            return parens(prec, 60,
                          tex_prec(60, e.args[0], small) + "_{" + ",".join(tex_prec(0, x, True) for x in e.args[1:]) + "}")
        elif e.head == "var" or e.head == "const":
            return "{" + e.args[0] + "}"
        elif e.head == "matrix":
            if TEX_VECTOR_AS_TUPLE() and is_vector(e):
                return "\\left(" + ",".join(tex_prec(0, row[0], small) for row in e.args) + "\\right)"
            return (r"\begin{bmatrix}"
                    + r"\\".join("&".join(tex_prec(0, x, True) for x in row) for row in e.args)
                    + r"\end{bmatrix}")
        elif e.head == "blockmatrix":
            # TODO make nicer results for cases we are able.  MathJax doesn't have multicolumn or multirow.
            # For now, symbolic entries are placed in the row/col that's centered (rounded down) in the block...

            # get number of columns and rows per block.  None if unknown.
            bncols = [None for _ in e.args[0]]
            bnrows = [None for _ in e.args]
            for i, row in enumerate(e.args):
                for j, b in enumerate(row):
                    if head(b) == "matrix":
                        c = ncols(b)
                        r = nrows(b)
                        if bncols[j] == None:
                            bncols[j] = c
                        elif bncols[j] != c:
                            raise ValueError(f"Block matrix has inconsistent numbers of columns in block column {j+1}")
                        if bnrows[i] == None:
                            bnrows[i] = r
                        elif bnrows[i] != r:
                            raise ValueError(f"Block matrix has inconsistent numbers of rows in block row {i+1}")
            # set unknown dimensions to 1
            for i, r in enumerate(bnrows):
                if r == None:
                    bnrows[i] = 1
            for j, c in enumerate(bncols):
                if c == None:
                    bncols[j] = 1
            # assemble the entries
            cols = sum(bncols)
            rows = sum(bnrows)
            entries = [["" for j0 in range(cols)] for i0 in range(rows)]
            hlinerows = set()
            i0 = 0
            for i, row in enumerate(e.args):
                j0 = 0
                for j, b in enumerate(row):
                    if head(b) == "matrix":
                        for i1, brow in enumerate(b.args):
                            for j1, e in enumerate(brow):
                                entries[i0 + i1][j0 + j1] = tex_prec(0, e, True)
                    else:
                        # try to center it vertically...
                        i1 = bnrows[i]//2
                        j1 = bncols[j]//2
                        entries[i1][j1] = tex_prec(0, b, True)
                    j0 += bncols[j]
                if i0 > 0:
                    hlinerows.add(i0)
                i0 += bnrows[i]
            return (r"\left[\begin{array}{" + "|".join("c"*nc for nc in bncols) + r"} "
                    + r" \\ ".join((r"\hline " if i in hlinerows else "") + " & ".join(row)
                                   for i, row in enumerate(entries))
                    + r"\end{array}\right]")
        elif e.head == "Deriv":
            x, spec, constants = e.args
            if TEX_DERIV_USE_PRIMES() and len(spec) == 1 and spec[0][0] == TEX_DERIV_INDEP_VAR():
                n = spec[0][1]
                if type(n) == int and 1 <= n <= TEX_DERIV_PRIMES_LIMIT():
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

def vector_align(v, w):
    """Given vectors `v` and `w` with the same dimensions, return an
    `align*` environment representing equalities between the entries
    of the vectors."""
    if not is_vector(v):
        raise ValueError("First argument must be a vector")
    if not is_vector(w):
        raise ValueError("Second argument must be a vector")
    if nrows(v) != nrows(w):
        raise ValueError("The vectors must have the same number of rows")
    s = r"\begin{align*} "
    for a, b in zip(vector_entries(v), vector_entries(w)):
        s += rf"{tex(a)} &= {tex(b)}\\ "
    s += r"\end{align*}"
    return s

def tex_list(x):
    """Gives the tex form of a list as an ordered set (i.e., using curly braces)."""
    if head(x) != "list":
        raise ValueError("Expecting list")
    return "\\left\{" + ",".join(tex(a) for a in x) + "\\right\}"
