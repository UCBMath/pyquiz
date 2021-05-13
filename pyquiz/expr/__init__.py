r"""This package implements a simple computer algebra system to aid in
the creation of dynamic quiz questions.  The two primary functions of
this in Pyquiz are (1) performing necessary calculations to construct
a question and its answer and (2) generating well-formed LaTeX for
inclusion in the text of the question.

The design is inspired by Mathematica, so those familiar might feel somewhat at home.

Every expression is either a native Python number type (like `int` or
`float`), a string, or an `Expr`.  An `Expr` consists of a "head",
which is an expression indicating the way in which the expression is
interpreted (it is almost always a string) along with with a list of
"arguments".  The `Expr` class implements most of Python's operators,
so the main way in which expressions are created is by algebraically
manipulating them.

*Note:* instead of dividing with a slash, use the `frac` function,
since it is careful to preserve exactness (i.e., it yields a
`Fraction` rather than a floating-point number).

Expressions can be indexed.  Like Mathematica (**warning:** but
*unlike* Python)
[they are 1-indexed](https://github.com/UCBMath/pyquiz/wiki/Explanation%3A-1-indexing-vs-0-indexing).
Since this module is meant to help with writing quiz questions for
math classes, which use 1-indexing, we break the Python convention and
follow suit.

To use expressions, you just need to import this module:
```python
from pyquiz.expr import *
```

# Modules

Overview of submodules:
* `pyquiz.expr.core` defines `Expr` and expression evaluation.
* `pyquiz.expr.arith` gives evaluation rules for arithmetic expressions.
* `pyquiz.expr.manipulate` gives functions such as `expand`.
* `pyquiz.expr.matrix` defines matrices and associated functions.
* `pyquiz.expr.tex_form` defines the `tex` function.
"""

from .core import *
from .arith import *
from .manipulate import *
from .tex_form import *
from .matrix import *
from .deriv import *
