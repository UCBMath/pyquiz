from pyquiz import *
from pyquiz.expr import *
from pyquiz.rand import *

seed(22)

begin_quiz(
    title="Row reduce test",
    description="Questions involving steps of row reduction"
)

begin_group()
for i in range(10):

    begin_true_false_question()

    A = rand_matrix(3, 3, -5, 5)
    steps = []
    A_reduced = row_reduce(A, rref=False, steps_out=steps)

    text(rf"""
    Consider the matrix
    \begin{{align}}
    A &= {A}
    \end{{align}}
    We applied the row reduction steps
    \begin{{align}}
    """)
    for step in steps:
        text(rf""" {step} \\""")
    text(rf"""
    \end{{align}}
    to get
    \begin{{equation}}
    {A_reduced}.
    \end{{equation}}
    Did we put \(A\) into echelon form correctly?
    """)

    true_false_answer(True)

    end_question()

end_group()

end_quiz()
