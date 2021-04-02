# expr.py
#
# A simple computer algebra system to aid in generating well-formed
# LaTeX for dynamically generated questions.
#
# Note: instead of dividing with a slash, use the `frac` function,
# since it is more careful to preserve exactness (i.e., it yields a
# Fraction rather than a floating-point number).

from collections import defaultdict
from numbers import Number
from fractions import Fraction

attributes = defaultdict(set)
attributes['Plus'].update(["Flat"])
attributes['Times'].update(["Flat"])

# A list of reduction rules
reductions = []

def reduction(f):
    """A decorator for defining new reductions.

    Usage:
    ```
    @reduction
    def my_reduction(e):
      return e
    ```
    """
    reductions.append(f)
    return f


class Expr:
    """This is supposed to be like a Mathematica expression.  Every
    expression has a `head` (an expression) and a list `args` (of
    expressions).  Expressions are either instances of `Expr` or are
    basic data types like strings or numbers."""

    def __init__(self, head, args):
        self.head = head
        self.args = list(args)
    def __add__(self, b):
        return normalize(expr("Plus", self, b))
    def __radd__(self, a):
        return normalize(expr("Plus", a, self))
    def __mul__(self, b):
        return normalize(expr("Times", self, b))
    def __rmul__(self, a):
        return normalize(expr("Times", a, self))
    def __sub__(self, b):
        return normalize(expr("Plus", self, expr("Times", -1, b)))
    def __rsub__(self, a):
        return normalize(expr("Plus", a, expr("Times", -1, self)))
    def __neg__(self):
        return normalize(expr("Times", -1, self))
    def __pow__(self, b):
        return normalize(expr("Pow", self, b))
    def __rpow__(self, a):
        return normalize(expr("Pow", a, self))
    # These are commented out because the use of slash for division makes
    # it more likely to accidentally create floating-point numbers when exact
    # numbers were wanted.
    #def __truediv__(self, b):
    #    return normalize(expr("Times", self, expr("Pow", b, -1)))
    #def __rtruediv__(self, a):
    #    return normalize(expr("Times", a, expr("Pow", self, -1)))
    def __getitem__(self, key):
        if type(key) == tuple:
            return normalize(expr("Part", self, *key))
        else:
            return normalize(expr("Part", self, key))
    def __setitem__(self, key, value):
        """Uses one-indexing (!)"""
        if type(key) == tuple:
            if len(key) == 1:
                self.args[key[0] - 1] = value
            elif len(key) == 2:
                self.args[key[0] - 1][key[1] - 1] = value
            else:
                raise TypeError("setitem for Expr only supports indexing up to two levels deep.")
        else:
            self.args[key - 1] = value
    def __eq__(self, other):
        """Check if structurally equal."""
        return (isinstance(other, Expr)
                and self.head == other.head
                and len(self.args) == len(other.args)
                and all(a == b for a,b in zip(self.args, other.args)))
    def __str__(self):
        """Gives a LaTeX representation of the expression."""
        return tex(self)
    def __repr__(self):
        return "expr(%r%s)" % (self.head, "".join(", " + repr(a) for a in self.args))

def frac(a, b):
    """It's hard to fully overload division in Python, so this is a function that takes the
    quotient in a way that ensures the the quotient of two integers is a fraction."""
    return normalize(expr("Times", a, expr("Pow", b, -1)))

def expr(head, *args):
    """A convenience for the Expr constructor.  `expr(a, b, c, ...)` is `Expr(a, [b, c, ...])`."""
    return Expr(head, args)

def head(e):
    """Gets the `head` of the expression.

    Gives the following values for built-in Python types:
    - numbers -> "number"
    - strings -> "string"
    - lists -> "list"
    """
    if isinstance(e, Number):
        return "number"
    elif isinstance(e, str):
        return "string"
    elif type(e) == list or type(e) == tuple:
        return "list"
    else:
        return e.head

def normalize(e):
    """Mathematica-like expression evaluation routine."""
    if isinstance(e, Number) or isinstance(e, str):
        return e
    elif type(e) == list or type(e) == tuple:
        # evaluate to list
        return [normalize(x) for x in e]
    elif type(e) != Expr:
        raise ValueError("Unknown type of value to normalize.")
    h = normalize(e.head)
    args = [normalize(a) for a in e.args]
    if "Flat" in attributes[h]:
        args2 = []
        for a in args:
            if head(a) == h:
                args2.extend(a.args)
            else:
                args2.append(a)
        args = args2
    e = Expr(h, args)
    for rule in reversed(reductions):
        e2 = rule(e)
        if e2 != e:
            return normalize(e2)
    return e

def plus_terms(e):
    """Helper function for rule_plus_collect."""
    assert head(e) == "Plus"
    def split(a):
        """Gives a (coeff, expr) pair for a given expression.  Assumes the
        expression has been already normalized."""
        if head(a) == "Times" and len(a.args) >= 1 and isinstance(a.args[0], Number):
            return (a.args[0], normalize(expr("Times", *a.args[1:])))
        elif isinstance(a, Number):
            return (a, 1)
        else:
            return (1, a)
    return [split(a) for a in e.args]

@reduction
def rule_plus_collect(e):
    """Collect monomials, adding numeric coefficients."""
    if head(e) != "Plus":
        return e
    terms = []
    for coeff, b in plus_terms(e):
        for i, (t, c) in enumerate(terms):
            if b == t:
                terms[i] = (t, c + coeff)
                break
        else:
            terms.append((b, coeff))
    args2 = []
    for t, c in terms:
        if c == 0:
            continue
        elif t == 1:
            args2.append(c)
        else:
            args2.append(normalize(expr("Times", c, t)))
    if len(args2) == 0:
        return 0
    elif len(args2) == 1:
        return args2[0]
    else:
        return expr("Plus", *args2)

def times_terms(e):
    """Helper function for rule_times_collect."""
    assert head(e) == "Times"
    def split(a):
        if head(a) == "Pow":
            return a.args
        else:
            return (a, 1)
    return [split(a) for a in e.args]

@reduction
def rule_times_collect(e):
    """Collect multiplicands of the product, combining exponents."""
    if head(e) != "Times":
        return e
    # collect all powers
    # terms is a list of (value, exponent) pairs
    terms = []
    coeff = 1
    for val, exp in times_terms(e):
        if exp == 1 and isinstance(val, Number):
            coeff *= val
        else:
            for i, (v, e) in enumerate(terms):
                if val == v:
                    terms[i] = (v, exp + e)
                    break
            else:
                terms.append((val, exp))
    args2 = []
    if coeff != 1:
        args2.append(coeff)
    for v, e in terms:
        v = normalize(expr("Pow", v, e))
        if v != 1:
            args2.append(v)
    if len(args2) == 0:
        return 1
    elif len(args2) == 1:
        return args2[0]
    else:
        return expr("Times", *args2)

@reduction
def rule_pow_constants(e):
    """Compute powers when constants are present."""
    if head(e) != "Pow":
        return e
    elif e.args[1] == 0:
        return 1
    elif e.args[1] == 1:
        return e.args[0]
    elif type(e.args[0]) == int and isinstance(e.args[1], Number):
        return Fraction(e.args[0]) ** e.args[1]
    elif isinstance(e.args[0], Number) and isinstance(e.args[1], Number):
        return e.args[0] ** e.args[1]
    else:
        return e

@reduction
def rule_part_matrix(e):
    """Extract a Part of a matrix or vector.  Uses 1-indexing(!)"""
    if head(e) != "Part" or head(e.args[0]) != "matrix" or len(e.args) not in (2, 3):
        return e
    if not all(type(x) == int for x in e.args[1:]):
        return e
    if len(e.args) == 2:
        row = e.args[0].args[e.args[1] - 1]
        if len(row) != 1:
            raise ValueError("Need two indices to index a matrix.")
        return row[0]
    elif len(e.args) == 3:
        return e.args[0].args[e.args[1] - 1][e.args[2] - 1]
    else:
        raise Exception("Internal error")

def replace(e, substs):
    """substs is a list of variable/value pairs to replace in the expression.  Similar to Replace in Mathematica."""
    for p,v in substs:
        if e == p:
            return v
    if isinstance(e, Expr):
        return normalize(expr(replace(e.head, substs), *(replace(a, substs) for a in e.args)))
    else:
        return e

###
### LaTeX generation
###

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
            for i, (coeff, b) in enumerate(plus_terms(e)):
                op = " + "
                if coeff == -1:
                    op = "-" # if i==0, then this is unary minus
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
            for b, exp in times_terms(e):
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
        elif e.head == "Pow":
            return parens(prec, 50, tex_prec(50, e.args[0]) + "^{" + tex_prec(0, e.args[1]) + "}")
        elif e.head == "Part":
            return parens(prec, 60,
                          tex_prec(60, e.args[0]) + "_{" + ",".join(tex_prec(0, x) for x in e.args[1:]) + "}")
        elif e.head == "var":
            return e.args[0]
        elif e.head == "matrix":
            return (r"\begin{bmatrix}"
                    + r"\\".join("&".join(tex_prec(0, x) for x in row) for row in e.args)
                    + r"\end{bmatrix}")
        elif isinstance(e.head, str):
            return (r"\operatorname{" + e.head + "}(" +
                    ", ".join(tex_prec(0, x) for x in e.args)
                    + ")")
        else:
            raise ValueError("unknown expression type to tex")
    else:
        raise ValueError("unknown value to tex " + repr(e))

def tex(e):
    return tex_prec(0, e)

###
### Useful constructors
###

def var(name):
    return expr("var", name)


###
### Matrices and vectors
###

def vector(*elts):
    """example: vector(1,2,3) returns matrix([1], [2], [3])"""
    #return Expr("Vector", elts)
    return Expr("matrix", [[elt] for elt in elts])
def matrix(*rows):
    """example: matrix([1,2],[3,4]) for rows [1,2] and [3,4]."""
    return Expr("matrix", rows)

def identity_matrix(n):
    """Returns the n by n identity matrix."""
    assert isinstance(n, int)
    return matrix(*[[1 if i == j else 0 for j in range(n)] for i in range(n)])

def det(e):
    return normalize(expr("det", e))
@reduction
def reduce_det(e):
    if head(e) != "det" or head(e.args[0]) != "matrix":
        return e
    def expand(rows):
        if len(rows) == 1:
            assert len(rows[0]) == 1
            return rows[0][0]
        # Expand along the first column
        acc = 0
        for i in range(len(rows)):
            submatrix = [row[1:] for row in rows[:i] + rows[i+1:]]
            acc += (-1) ** i * rows[i][0] * expand(submatrix)
        return acc

    r = expand(e.args[0].args)
    return r

# M = identity_matrix(3)
# N = matrix([1,1,1],[1,-1,0],[1,1,-2])
# A = matrix(*[[var("a")[i+1,j+1] for j in range(3)] for i in range(3)])
# v = var("v")
# M[1,1] = v
# print(det(A))
