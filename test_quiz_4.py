from pyquiz.expr import *
from pyquiz.rand import *
from pyquiz import *

seed(100)

begin_quiz(
    title="Matrix test",
    description=rf""" <p>Testing matrix multiplication and such.</p> """
)

begin_group()
for i in range(5):
    begin_multiple_choice_question()

    A = rand_matrix(2,3, -5,5)
    B = rand_matrix(3,2, -5,5)

    text(rf"""
    Given the matrices
    \begin{{align*}}
    A &= {A} & B &= {B}
    \end{{align*}}
    compute the \((1,2)\) entry of \(AB\).
    """)

    ans = (A@B)[1,2]

    multiple_choice_answer(True, ans)

    fake_answers = list(range(-20, 21))
    if ans in fake_answers:
        fake_answers.remove(ans)

    for fake in sample(fake_answers, 3):
        multiple_choice_answer(False, fake)

    end_question()
end_group()

begin_group()
for i in range(5):
    begin_multiple_choice_question()

    A = rand_invertible_2x2(-10, 10)
    D = rand_diagonal_matrix(2, -4, 4)
    B = (A**-1) @ D @ A
    print(repr(A**-1))
    evals = set(D[i,i] for i in range(1, 2+1))

    fakes = []
    while len(fakes) < 3:
        fake_evals = set([randint(-4, 4), randint(-4, 4)])
        if fake_evals != evals and fake_evals not in fakes:
            fakes.append(fake_evals)

    text(rf"""
    What are the eigenvalues of the matrix
    \[{B}\]
    """)

    multiple_choice_answer(True, rf"""\({",".join(str(e) for e in evals)}\)""")

    for fake in fakes:
        multiple_choice_answer(False, rf"""\({",".join(str(e) for e in fake)}\)""")

    end_question()
end_group()

end_quiz()
