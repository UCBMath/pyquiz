r"""This module defines core functionality for expressions.  In
addition to some built-in Python types, there is the compound `Expr`
type for symbolic expressions.

Like Mathematica, subtraction and division don't exist.  Instead, `a - b` is
`a + (-1)*b` and `a / b` is `a * b**-1`.

"""

from collections import defaultdict
from numbers import Number

__all__ = [
    "Expr", "frac", "expr", "head",
    "Inapplicable", "downvalue", "evaluate",
    "irange",
    "var", "const"
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
    def __xor__(self, b):
        raise Exception("Use ** instead of ^ for exponentiation.")
    def __rxor__(self, a):
        raise Exception("Use ** instead of ^ for exponentiation.")
    def __getitem__(self, key):
        if type(key) == tuple:
            return evaluate(expr("Part", self, *key))
        else:
            return evaluate(expr("Part", self, key))
    def __setitem__(self, key, value):
        """Uses one-indexing (!)"""
        # TODO turn this into something more extensible

        if self.head != "matrix":
            raise ValueError("Can only set entries for matrices and vectors")

        # copy-on-write, sort of.
        self.args = list(self.args)

        def set1(idx):
            if type(idx) != int:
                raise ValueError("Expecting integer for index")
            elif not (1 <= idx <= len(self.args)):
                raise ValueError("Index out of range")
            else:
                if len(self.args[0]) != 1:
                    raise ValueError("Expecting vector, not matrix")
                self.args[idx - 1][0] = value
        def set2(idx1, idx2):
            if type(idx1) != int:
                raise ValueError("Expecting integer for first index")
            if type(idx2) != int:
                raise ValueError("Expecting integer for second index")
            elif not (1 <= idx1 <= len(self.args)):
                raise ValueError("First index out of range")
            elif not (1 <= idx2 <= len(self.args[0])):
                raise ValueError("Second index out of range")
            else:
                self.args[idx1 - 1][idx2 - 1] = value

        if type(key) == tuple:
            if len(key) == 1:
                set1(key[0])
            elif len(key) == 2:
                set2(key[0], key[1])
            else:
                raise ValueError("Expecting either 1 or 2 indices")
        else:
            set1(key)
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
        from pyquiz.expr.tex_form import tex
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

class Inapplicable(Exception):
    """An exception to signal that a rule (for example a downvalue) does
    not apply, so the next rule should be tried."""
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
    applying this downvalue, raising `Inapplicable` if there aren't the
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
        raise Inapplicable
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
                    raise Inapplicable
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
                return mk
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
        If a downvalue raises `Inapplicable` or it returns an expression that is equal to what it was given,
        then the next is tried in succession.  Otherwise, the resulting expression is (recursively) evaluated.
      * The evaluated expression is returned.

    """
    while True:
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
            except Inapplicable:
                continue
            except Exception as exc:
                print(f"evaluate: internal error while evaluating rule {rule.__name__} for {e!r}")
                raise exc from None
            if e2 != e:
                e = e2
                break # continue the while loop
        else:
            return e

def irange(a, b=None):
    """Inclusive range.

    * `irange(hi)` gives the list `[1, 2, ..., hi]`.
    * `irange(lo, hi)` gives the list `[lo, lo+1, ..., hi]`.

    This is intended for loops that index a matrix, for example if `A` is a square matrix, we could compute its trace
    and print it out by
    ```python
    t = 0
    for i in irange(ncols(A)):
      t = t + A[i, i]
    print(t)
    ```

    """
    if b == None:
        lo, hi = 1, a
    else:
        lo, hi = a, b
    return list(range(lo, hi+1))

def var(name):
    """`var("foo")` creates a variable of name "foo".

    A variable can contain LaTeX code, like for example
    `var(r"\lambda")`.  The `r` indicates "raw string", without which
    you need a doubled backslash like `var("\\lambda")`.

    Example:
    ```python
    a = var("a")
    ```

    See also `const`.  In contrast, a `var` can depend on other variables.
    """
    if not isinstance(name, str):
        raise ValueError("Expecting string")
    return expr("var", name)

def const(name):
    """`const("foo")` creates a constant of name "foo".

    A constant can contain LaTeX code, like for example
    `const(r"\lambda")`.  The `r` indicates "raw string", without which
    you need a doubled backslash like `const("\\lambda")`.

    Example:
    ```python
    a = const("a")
    ```

    See also `var`.  In constrast, a `const` is assumed to be a fixed constant scalar value.
    """
    if not isinstance(name, str):
        raise ValueError("Expecting string")
    return expr("const", name)
