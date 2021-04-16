from pyquiz.expr import *
from pyquiz.rand import *
from pyquiz import *

def q1():
    """Two equations, two unknowns."""

    A = rand_invertible_2x2(-8,8)
    d = det(A)
    b = vector(randint(-5, 5) * d,
               randint(-5, 5) * d)

    x1 = var("x")[1]
    x2 = var("x")[2]

    ans = frac(A[2,2]*b[1] - A[1,2]*b[2], d)

    begin_numeric_question()

    text(rf"""
    <p>Solve the following system of equations, and give the value for \(x_1\).</p>
    \[\begin{{align*}}
      {A[1,1]*x1 + A[1,2]*x2} &= {b[1]} \\
      {A[2,1]*x1 + A[2,2]*x2} &= {b[2]}
    \end{{align*}}\]
    """)

    numeric_answer(ans)

    end_question()

def q2():
    """Two equations, two unknowns, but said in terms of lines."""

    A = rand_invertible_2x2(-8,8)
    d = det(A)
    b = vector(randint(-5, 5) * d,
               randint(-5, 5) * d)

    x1 = var("x")[1]
    x2 = var("x")[2]

    ans = frac(A[2,2]*b[1] - A[1,2]*b[2], d)

    begin_numeric_question()

    text(rf"""
    <p>Give the value of \(x_1\) for the point \((x_1,x_2)\) that simultaneously lies on the line
    \({A[1,1]*x1 + A[1,2]*x2} = {b[1]}\) and on the line \({A[2,1]*x1 + A[2,2]*x2} = {b[2]}\).</p>
    """)

    numeric_answer(ans)

    end_question()

def q3():
    a = randint_nonzero(-5, 5)
    b = randint_nonzero(-5, 5)
    scale1 = randint_nonzero(-5, 5)
    scale2 = randint_nonzero(-5, 5)

    begin_numeric_question()

    text(rf"""
    <p>For how many different values of \(h\) is the following an augmented matrix of
    a consistent linear system?</p>
    \[
    \begin{{bmatrix}}
    {a} & {a * scale1} & h \\
    {b} & {b * scale1} & {b * scale2}
    \end{{bmatrix}}
    \]
    """)

    numeric_answer(1)

    end_question()

def q4():
    a = randint_nonzero(-5, 5)
    b = randint_nonzero(-5, 5)
    scale1 = randint_nonzero(-5, 5)
    scale2 = randint_nonzero(-5, 5)

    begin_multiple_choice_question()

    text(rf"""
    <p>For how many different values of \(h\) is the following an augmented matrix of
    a consistent linear system?</p>
    \[
    \begin{{bmatrix}}
    {a} & h & {a * scale2} \\
    {b} & {b * scale1} & {b * scale2}
    \end{{bmatrix}}
    \]
    """)

    multiple_choice_answer(False, "\(0\)")
    multiple_choice_answer(False, "\(1\)")
    multiple_choice_answer(False, "\(2\)")
    multiple_choice_answer(True, "\(\infty\)")

    end_question()

def true_false_bank():
    """Add all these true/false questions.  Use a question group to pick a certain number."""

    begin_true_false_question()
    text(r"""Every elementary row operation is reversible.""")
    true_false_answer(True)
    end_question()

    begin_true_false_question()
    text(r"""A \(5\times 6\) matrix has six rows.""")
    true_false_answer(False)
    end_question()

    begin_true_false_question()
    text(r"""The solution set of a linear system involving variables
    \(x_1,\dots,x_n\) is a list of numbers \((s_1,\dots,s_n)\) that makes each
    equation in the system a true statement when the values \(s_1,\dots,s_n\)
    are respectively substituted for \(x_1,\dots,x_n\).""")
    true_false_answer(True)
    end_question()

    begin_true_false_question()
    text(r"""Two fundamental questions about a linear system involve existence and uniqueness.""")
    true_false_answer(True)
    end_question()

    begin_true_false_question()
    text(r"""Elementary row operations on an augmented matrix never change the solution set of the
    associated linear system.""")
    true_false_answer(True)
    end_question()

    begin_true_false_question()
    text(r"""Two matrices are row equivalent if they have the same number of rows.""")
    true_false_answer(False)
    end_question()

    begin_true_false_question()
    text(r"""An inconsistent system has more than one solution.""")
    true_false_answer(False)
    end_question()

    begin_true_false_question()
    text(r"""Two linear systems are equivalent if they have the same solution set.""")
    true_false_answer(True)
    end_question()
