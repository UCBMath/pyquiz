from pyquiz.expr import *
from pyquiz import *

def q1():
    begin_numeric_question()

    text("The answer is \(6\cdot 7\).")

    numeric_answer(42)

    end_question()

def q2(i):
    """Each value of i in [0,5) gives a variant of the question."""

    a = var("a")
    y = a**2 - 3*a + 1

    begin_numeric_question()

    text(rf"""
    <p>Suppose \(a={i}\).  What is \(y={y}\)?</p>
    """)

    numeric_answer(replace(y, [(a, i)]),
                   precision=2)

    end_question()

def q3():
    begin_multiple_choice_question()

    text(rf"""
    <p>What is another term for one-to-one?</p>
    """)

    multiple_choice_answer(True, "injective")
    multiple_choice_answer(False, "surjective")
    multiple_choice_answer(False, "bijective")
    multiple_choice_answer(False, "trijective")
    multiple_choice_answer(False, "postjective")
    multiple_choice_answer(False, "prejective")
    multiple_choice_answer(False, "epijective")

    end_question()

def q4():
    begin_true_false_question()

    text(r"""
    <p>Suppose \(V\) is a vector space and \(\mathcal{B}_1\) and \(\mathcal{B}_2\) are two bases for \(V\).</p>

    <p>The cardinalities of \(\mathcal{B}_1\) and \(\mathcal{B}_2\) are equal.</p>
    """)

    true_false_answer(True)

    end_question()

def q5():
    begin_multiple_choice_question()

    a = var("a")
    A = matrix([a[1,1], a[1,2], a[1,3]],
               [a[2,1], a[2,2], a[2,3]],
               [a[3,1], a[3,2], a[3,3]])

    text(rf"""
    <p>Suppose</p>
    \[A = {A}.\]
    <p>Which of the following is equal to \({det(var("A"))}\)?</p>
    """)

    multiple_choice_answer(True, rf"\({det(A)}\)")
    multiple_choice_answer(False, r"\(a_{1,1}a_{2,2}a_{3,3}\)")

    end_question()
