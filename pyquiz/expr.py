r"""This module implements a simple computer algebra system to aid in
generating well-formed LaTeX for dynamically generated questions.
It is inspired my Mathematica, so those familiar should feel somewhat at home.

Every expression is either a native Python number type (like `int` or
`float`), a string, or an `Expr`.  An `Expr` consists of a "head",
which is an expression indicating the way in which the expression is
interpreted (it is almost always a string) along with with a list of
"arguments".  `Expr` implements most of Python's operators, so the
main way in which expressions are created is by algebraically
manipulating them.

*Note:* instead of dividing with a slash, use the `frac` function,
since it is careful to preserve exactness (i.e., it yields a
`Fraction` rather than a floating-point number).

Expressions can be indexed.  Like Mathematica (**warning:** but
*unlike* Python) they are 1-indexed.  Since this module is meant to
help with writing quiz questions for math classes, which use
1-indexing, we break the Python convention and follow suit.

"""

from collections import defaultdict
from numbers import Number
from fractions import Fraction

__all__ = [
    "Expr", "frac", "expr", "head",
    "var",
    "vector", "matrix", "is_vector", "tex_vector_as_tuple",
    "rows", "cols",
    "row_reduce", "rank", "nullity",
    "irange", "identity_matrix", "det", "diagonal_matrix",
    "evaluate", "expand", "replace",
    "downvalue", "DeferEval",
    "tex"
]

class Expr:
    """This is supposed to be like a Mathematica expression.  Every
    expression has a `head` (an expression) and a list `args` (of
    expressions).  Expressions are either instances of `Expr` or are
    basic data types like strings or numbers.

    Given an expression `e`, the string version of `e` (for example,
    via `str(e)`) is its LaTeX form.  To get a somewhat
    Python-readable form, use `repr(e)`.

    In Python, matrix multiplication is indicated with `@`, for
    example `A @ B` (vs Mathematica's `A . B`).

    """

    def __init__(self, head, args):
        """Construct an `Expr` with the given head and list of arguments.  See also `expr()`."""
        self.head = head
        self.args = args
    def __add__(self, b):
        return evaluate(expr("Plus", self, b))
    def __radd__(self, a):
        return evaluate(expr("Plus", a, self))
    def __mul__(self, b):
        return evaluate(expr("Times", self, b))
    def __rmul__(self, a):
        return evaluate(expr("Times", a, self))
    def __sub__(self, b):
        return evaluate(expr("Plus", self, expr("Times", -1, b)))
    def __rsub__(self, a):
        return evaluate(expr("Plus", a, expr("Times", -1, self)))
    def __neg__(self):
        return evaluate(expr("Times", -1, self))
    def __pow__(self, b):
        return evaluate(expr("Pow", self, b))
    def __rpow__(self, a):
        return evaluate(expr("Pow", a, self))
    def __matmul__(self, b):
        return evaluate(expr("MatTimes", self, b))
    def __rmatmul__(self, a):
        return evaluate(expr("MatTimes", a, self))
    # These are commented out because the use of slash for division makes
    # it more likely to accidentally create floating-point numbers when exact
    # numbers were wanted.
    #def __truediv__(self, b):
    #    return evaluate(expr("Times", self, expr("Pow", b, -1)))
    #def __rtruediv__(self, a):
    #    return evaluate(expr("Times", a, expr("Pow", self, -1)))
    def __getitem__(self, key):
        if type(key) == tuple:
            return evaluate(expr("Part", self, *key))
        else:
            return evaluate(expr("Part", self, key))
    def __setitem__(self, key, value):
        """Uses one-indexing (!)"""
        # TODO turn this into something more extensible

        # copy-on-write, sort of.
        self.args = list(self.args)

        if type(key) == tuple:
            if len(key) == 1:
                self.args[key[0] - 1] = value
            elif len(key) == 2:
                self.args[key[0] - 1][key[1] - 1] = value
            else:
                raise TypeError("setitem for Expr only supports indexing up to two levels deep.")
        else:
            self.args[key - 1] = value
    def __iter__(self):
        """Iterate over the arguments of the expression."""
        return iter(self.args)
    def __len__(self):
        return len(self.args)
    def __eq__(self, other):
        """Check if structurally equal."""
        if self is other:
            return True
        return (isinstance(other, Expr)
                and self.head == other.head
                and len(self.args) == len(other.args)
                and all(a == b for a,b in zip(self.args, other.args)))
    def __str__(self):
        """Gives a LaTeX representation of the expression."""
        return tex(self)
    def __repr__(self):
        return "expr(%r%s)" % (self.head, "".join(", " + repr(a) for a in self.args))

def expr(head, *args):
    """A convenience function for the `Expr` constructor.  `expr(a, b, c, ...)` is `Expr(a, [b, c, ...])`."""
    return Expr(head, args)

def head(e):
    """Gets the "head" of the expression.

    Gives the following values for built-in Python types:
    * numbers -> "number"
    * strings -> "string"
    * lists and tuples -> "list"
    * `Expr` -> the `head` attribute of the object
    """
    if isinstance(e, Number):
        return "number"
    elif isinstance(e, str):
        return "string"
    elif type(e) == list or type(e) == tuple:
        return "list"
    else:
        return e.head

def frac(a, b):
    """Divides `a` by `b` exactly.

    It's hard to fully overload division in Python, so this is a function that takes the
    quotient in a way that ensures the the quotient of two integers is a fraction."""
    return evaluate(expr("Times", a, expr("Pow", b, -1)))


attributes = defaultdict(set)
r"""Attributes control some additional evaluation rules that apply before
other evaluation rules.

* "Flat" takes nested expressions and flattens them.
  For example, `expr("Plus", expr("Plus", a, b), expr("Plus", c, d), e)`
  becomes `expr("Plus", a, b, c, d, e)`.
"""
attributes['Plus'].update(["Flat"])
attributes['Times'].update(["Flat"])

downvalues = defaultdict(list)
r"""Using the Mathematica terminology, a downvalue is an evaluation
rule attached to a particular head.  During the evaluation of an `Expr`,
if the head is a string then all the downvalues for that head are considered
one at a time in reverse order.
"""

class DeferEval(Exception):
    pass

def function_arity(f):
    """Returns the arity of `f`, which describes the number of positional
    arguments that `f` can accept.  Requires that `f` not be a builtin
    since it uses `inspect.signature` to calculate the arity.

    Returns: (lo, hi) where `lo` is the minimum number of positional
    arguments `f` accepts, and `hi` is the maximum (`float('inf')` if
    it can accept arbitrarily many).

    Examples:
    ```python
    def f1(a, b): pass       # arity = (2, 2)
    def f2(a, b=2): pass     # arity = (1, 2)
    def f3(a, b, *c): pass   # arity = (2, float('inf'))
    def f4(a, b=2, *c): pass # arity = (1, float('inf'))
    ```

    """
    import inspect
    lo = 0
    hi = 0
    for param in inspect.signature(f).parameters.values():
        if param.kind in (param.POSITIONAL_ONLY, param.POSITIONAL_OR_KEYWORD):
            if param.default is param.empty:
                lo += 1
            hi += 1
        elif param.kind == param.VAR_POSITIONAL:
            hi = float('inf')
    return (lo, hi)

def downvalue(head, with_expr=False, def_expr=False):
    """(internal) A decorator for adding new downvalues for a particular
    head.  The function receives the arguments of the expression as
    arguments if `with_expr=False`, and otherwise it receives the
    expression itself as its sole argument.  In the case
    `with_expr=False`, the arity of the function is considered when
    applying this downvalue, raising `DeferEval` if there aren't the
    correct number of arguments.

    If `def_expr` is `True`, then the decorator replaces the function
    with, essentially, `evaluate(expr(head, ...arguments))`.  This is
    to make it easy to define new types of expressions that really
    only have one downvalue.  If `with_expr` is `True`, then the arity
    is unbounded, and otherwise it uses the arity of the function.

    If `def_expr` is `False`, then the function that's defined is
    whatever gets added to the downvalues list.  This is so you can
    refer to it and remove it if you don't want a certain evaluation
    rule to apply.  (Note: if `def_expr` is `True` then the downvalue
    itself is *not* returned.)

    Example:
    ```python
    @downvalue("f", def_expr=True)
    def f(x):
      if not isinstance(x, int):
        raise DeferEval
      return x + 1
    ```
    Since `def_expr=True`, this creates a function `f` that takes one
    argument and returns `evaluate(expr("f", x))`.

    """
    assert isinstance(head, str)
    import functools
    def add_downvalue(f):
        if with_expr:
            # f itself is the downvalue
            downvalues[head].append(f)
            if def_expr:
                # return an expression constructor with no arity constraints
                @functools.wraps(f)
                def mk(*args):
                    return evaluate(Expr(head, args))
                return mk
            else:
                # otherwise return what was added to downvalues
                return f
        else:
            # need to wrap f in a function that extracts the arguments
            lo, hi = function_arity(f)
            @functools.wraps(f)
            def _f(e):
                if lo <= len(e.args) <= hi:
                    return f(*e.args)
                else:
                    raise DeferEval
            downvalues[head].append(_f)
            if def_expr:
                # return an expression constructor with arity constraints drawn from f
                @functools.wraps(f)
                def mk(*args):
                    if lo <= len(args) <= hi:
                        return evaluate(Expr(head, args))
                    else:
                        if hi == float('inf'):
                            raise ValueError(f"{head} expression expecting at least {lo} arguments")
                        else:
                            raise ValueError(f"{head} expression expecting between {lo} and {hi} arguments")
                return def_expr
            else:
                # otherwise return what was added to downvalues
                return _f
    return add_downvalue


def evaluate(e):
    """Mathematica-like expression evaluation routine.  Puts an expression
    into a sort of normal form by applying all the evaluation rules
    until the expression no longer changes.  This function is (or at
    least should be) idempotent in that `evaluate(evaluate(e)) == evaluate(e)`.

    It is not meant to be an expression simplifier, though we do let
    it collect coefficients and exponents in linear combinations and
    monomials.  We also allow applications of functions, for instance
    through the downvalues mechanism.

    * Simple expressions like literal numbers or strings are returned as-is.
    * Python lists/tuples are evaluated by evaluating their elements.  They are returned as lists.
    * Compound expressions (`Expr`) are evaluated according to the following steps:
      * The head and arguments are evaluated.
      * If the head is a string with the "Flat" attribute, then each
        argument with the same head is replaced with its arguments
        spliced in, effectively flattening the expression.  (This is
        meant to be used for associative operations where it is more
        convenient deal with the associated operad.)
      * If the head is a string with an associated list of `downvalues` (Mathematica terminology)
        then the downvalues are attempted to be applied in reverse order.
        If a downvalue raises `DeferEval` or it returns an expression that is equal to what it was given,
        then the next is tried in succession.  Otherwise, the resulting expression is (recursively) evaluated.
      * The evaluated expression is returned.

    """
    if isinstance(e, Number) or isinstance(e, str):
        return e
    elif type(e) == list or type(e) == tuple:
        # evaluate to list
        return [evaluate(x) for x in e]
    elif type(e) != Expr:
        raise ValueError(f"Unknown type of value ({type(e)!r}) to evaluate.")
    h = evaluate(e.head)
    args = [evaluate(a) for a in e.args]
    if "Flat" in attributes[h]:
        # assumes all arguments have been flattened by the recursive `evaluate`
        args2 = []
        for a in args:
            if head(a) == h:
                args2.extend(a.args)
            else:
                args2.append(a)
        args = args2
    e = Expr(h, args)
    if not isinstance(e.head, str):
        return e
    for rule in reversed(downvalues[e.head]):
        try:
            e2 = rule(e)
        except DeferEval:
            continue
        if e2 != e:
            return evaluate(e2)
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

def plus_terms(e):
    """Helper function for rule_plus_collect."""
    assert head(e) == "Plus"
    def split(a):
        """Gives a (coeff, expr) pair for a given expression.  Assumes the
        expression has been already evaluated."""
        if head(a) == "Times" and len(a.args) >= 1 and isinstance(a.args[0], Number):
            return (a.args[0], evaluate(expr("Times", *a.args[1:])))
        elif isinstance(a, Number):
            return (a, 1)
        else:
            return (1, a)
    return [split(a) for a in e.args]

@downvalue("Plus", with_expr=True)
def rule_plus_collect(e):
    """Collect monomials, adding numeric coefficients."""
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
            args2.append(evaluate(expr("Times", c, t)))
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

@downvalue("Times", with_expr=True)
def rule_times_collect(e):
    """Collect multiplicands of the product, combining exponents."""
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
        v = evaluate(expr("Pow", v, e))
        if v != 1:
            args2.append(v)
    if len(args2) == 0:
        return 1
    elif len(args2) == 1:
        return args2[0]
    else:
        return expr("Times", *args2)

@downvalue("Pow")
def rule_pow_constants(a, b):
    """Compute powers when constants are present."""
    if a == 0:
        return 1
    elif b == 1:
        return a
    elif type(a) == int and isinstance(b, Number):
        return Fraction(a) ** b
    elif isinstance(a, Number) and isinstance(b, Number):
        return a ** b
    else:
        raise DeferEval

@downvalue("Part")
def rule_part_matrix(e, *idxs):
    """Extract a Part of a matrix or vector.  Uses 1-indexing(!)"""
    if head(e) != "matrix" or not (1 <= len(idxs) <= 2):
        raise DeferEval
    if not all(type(x) == int for x in idxs):
        raise DeferEval
    if len(idxs) == 1:
        row = e.args[idxs[0] - 1]
        if len(row) != 1:
            raise ValueError("Need two indices to index a matrix.")
        return row[0]
    elif len(idxs) == 2:
        return e.args[idxs[0] - 1][idxs[1] - 1]
    else:
        raise Exception("Internal error")

def replace(e, substs):
    """substs is a list of expression/value pairs to replace in the expression.  Similar to Replace in Mathematica."""
    for p,v in substs:
        if e == p:
            return v
    if isinstance(e, Expr):
        return evaluate(expr(replace(e.head, substs), *(replace(a, substs) for a in e.args)))
    elif head(e) == "list":
        return [replace(a, substs) for a in e]
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
        elif e.head == "MatTimes":
            return parens(prec, 30, "".join([tex_prec(30, a) for a in e.args]))
        elif e.head == "Pow":
            return parens(prec, 50, tex_prec(50, e.args[0]) + "^{" + tex_prec(0, e.args[1]) + "}")
        elif e.head == "Part":
            return parens(prec, 60,
                          tex_prec(60, e.args[0]) + "_{" + ",".join(tex_prec(0, x) for x in e.args[1:]) + "}")
        elif e.head == "var":
            return e.args[0]
        elif e.head == "matrix":
            if TEX_VECTOR_AS_TUPLE and is_vector(e):
                return "(" + ",".join(tex_prec(0, row[0]) for row in e.args) + ")"
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
    """Return the TeX form of an expression."""
    return tex_prec(0, e)

if True:
    # A hack: monkey patch so that the string form of a Fraction is its TeX form
    Fraction.__str__ = lambda self: tex(self)

###
### Useful constructors
###

def var(name):
    """`var("foo")` creates a variable of name "foo".

    A variable can contain LaTeX code, like for example
    `var(r"\lambda")`.  The `r` indicates "raw string", without which
    you need a doubled backslash like `var("\\lambda")`.

    Example:
    ```python
    a = var("a")
    ```

    """
    return expr("var", name)


###
### Matrices and vectors
###

def vector(*elts):
    """example: vector(1,2,3) returns matrix([1], [2], [3])"""
    if len(elts) == 0:
        raise ValueError("We don't allow vectors to have no elements.")
    return Expr("matrix", [[elt] for elt in elts])
def matrix(*rows):
    """example: matrix([1,2],[3,4]) for rows [1,2] and [3,4]."""
    if len(rows) == 0:
        raise ValueError("We don't allow matrices to have no rows.")
    if any(len(row) != len(rows[0]) for row in rows):
        raise ValueError("Not all rows in matrix have the same length.")
    return Expr("matrix", rows)

def is_vector(e):
    """A vector is a matrix whose rows each have one entry."""
    return head(e) == "matrix" and len(e.args[0]) == 1

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

def identity_matrix(n):
    """Returns the n by n identity matrix."""
    assert isinstance(n, int)
    return matrix(*[[1 if i == j else 0 for j in range(n)] for i in range(n)])

@downvalue("det", def_expr=True)
def det(e):
    """Computes the determinant of the given matrix"""
    if head(e) != "matrix":
        raise DeferEval
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

    r = expand(e.args)
    return r

# TODO make this an "expansion" that doesn't apply during evaluation?
@downvalue("MatTimes")
def reduce_matmul(A, B):
    if head(A) != "matrix" or head(B) != "matrix":
        raise DeferEval
    if cols(A) != rows(B):
        raise ValueError("Number of columns of first argument does not equal number of rows of second argument")
    C = []
    for i in irange(rows(A)):
        row = []
        C.append(row)
        for j in irange(cols(B)):
            x = 0
            for k in irange(cols(A)):
                x += A[i,k] * B[k,j]
            row.append(x)
    return matrix(*C)

@downvalue("adj", def_expr=True)
def adj(e):
    """Computes the adjugate matrix"""
    if head(e) != "matrix":
        raise DeferEval
    rows = e.args
    if len(rows) != len(rows[0]):
        raise ValueError("expecting square matrix")
    n = len(rows)
    def C(i0, j0):
        """(i,j) cofactor"""
        rows2 = [[v for j,v in enumerate(row) if j != j0] for i,row in enumerate(rows) if i != i0]
        return det(matrix(*rows2))
    return matrix(*[[(-1)**(i + j) * C(j, i) for j in range(n)] for i in range(n)])

@downvalue("Pow")
def reduce_matrix_inverse(A, n):
    if head(A) != "matrix" or n != -1:
        raise DeferEval

    if len(A) != len(A[0]):
        raise ValueError("Taking the inverse of a non-square matrix")

    d = det(A)
    a = adj(A)
    return matrix(*[[frac(v, d) for v in row] for row in a.args])

def row_reduce(e, rref=True, steps_out=None):
    """Puts the matrix into row echelon form.

    * If `rref=True` then gives the reduced row echelon form.

    * If `rref=False` then gives row echelon form.

    Follows the algorithm in Lay.

    If `steps_out` if set to a list of your choosing, then it will be
    populated with TeX for each rule that was applied.
    ```python
    steps = []
    row_reduce(A, steps_out=steps)
    print(",".join(steps))
    ```
    """
    if head(e) != "matrix":
        raise ValueError("expecting matrix")

    # copy the matrix
    mat = [[v for v in row] for row in e.args]

    rows = len(mat)
    cols = len(mat[0])
    def swap(i, j):
        # R_i <-> R_j
        mat[i], mat[j] = mat[j], mat[i]
        if steps_out != None:
            steps_out.append(rf"R_{i} \leftrightarrow R_{j}")
    def scale(i, c):
        # c * R_i -> R_i
        for k in range(cols):
            mat[i][k] *= c
        if steps_out != None:
            Ri = var(f"R_{i}")
            steps_out.append(rf"{c * Ri} \rightarrow {Ri}")
    def replace(i, j, c):
        # R_i + c * R_j -> R_i
        for k in range(cols):
            mat[i][k] += c * mat[j][k]
        if steps_out != None:
            Ri = var(f"R_{i}")
            Rj = var(f"R_{j}")
            steps_out.append(rf"{Ri + c * Rj} \rightarrow {Ri}")
    def is_zero(i):
        # whether row i is a zero row
        return all(mat[i][k] == 0 for k in range(cols))

    i = 0
    j = 0
    last_nz = rows - 1
    while last_nz >= 0 and is_zero(last_nz):
        last_nz -= 1
    while i < rows and j < cols:
        if is_zero(i):
            if i >= last_nz:
                break
            swap(i, last_nz)
            last_nz -= 1
        if mat[i][j] == 0:
            for k in range(i + 1, last_nz + 1):
                if mat[k][j] != 0:
                    swap(i, k)
                    break
        if mat[i][j] == 0:
            j += 1
            continue
        if mat[i][j] != 1:
            scale(i, frac(1, mat[i][j]))
        for k in range(i + 1, last_nz + 1):
            if mat[k][j] != 0:
                replace(k, i, -mat[k][j])
        i += 1
        j += 1
    if rref:
        for i in range(last_nz, -1, -1):
            for j in range(cols):
                if mat[i][j] != 0:
                    # in fact, the entry is 1
                    for k in range(i - 1, -1, -1):
                        if mat[k][j] != 0:
                            replace(k, i, -mat[k][j])
                    break
    return matrix(*mat)

def rows(e):
    """Gives the number of rows in the matrix."""
    if head(e) != "matrix":
        raise ValueError("expecting a matrix")
    return len(e.args)

def cols(e):
    """Gives the number of columns in the matrix."""
    if head(e) != "matrix":
        raise ValueError("expecting a matrix")
    return len(e.args[0])

@downvalue("rank", def_expr=True)
def rank(e):
    """Gives the rank of the matrix"""
    if head(e) != "matrix":
        raise DeferEval
    e = row_reduce(e, rref=False)
    assert head(e) == "matrix"
    return sum(1 for row in e.args if not all(v == 0 for v in row))

@downvalue("nullity", def_expr=True)
def nullity(e):
    """Gives the nullity of the matrix"""
    if head(e) != "matrix":
        raise DeferEval
    return cols(e) - rank(e)

def irange(a, b=None):
    """Inclusive range.

    * `irange(hi)` gives the list `[1, 2, ..., hi]`.
    * `irange(lo, hi)` gives the list `[lo, lo+1, ..., hi]`.

    This is intended for loops that index a matrix, for example if `A` is a square matrix, we could compute its trace
    and print it out by
    ```python
    t = 0
    for i in irange(cols(A)):
      t = t + A[i, i]
    print(t)
    ```

    """
    if b == None:
        lo, hi = 1, a
    else:
        lo, hi = a, b
    return list(range(lo, hi+1))

def diagonal_matrix(*entries):
    """`diagonal_matrix(a11, a22, ..., ann)` gives an nxn matrix whose diagonal is given by these n expressions."""
    return matrix(*([entries[i] if i == j else 0 for j in range(len(entries))] for i in range(len(entries))))

# M = identity_matrix(3)
# N = matrix([1,1,1],[1,-1,0],[1,1,-2])
# A = matrix(*[[var("a")[i+1,j+1] for j in range(3)] for i in range(3)])
# v = var("v")
# M[1,1] = v
# print(det(A))
