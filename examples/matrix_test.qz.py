from pyquiz.expr import *
from pyquiz.rand import *
from pyquiz import *

seed(100)

begin_quiz(
    title="Matrix test",
    description=rf"""Testing matrix multiplication and such."""
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

    P = rand_invertible_2x2(-10, 10)
    D = rand_diagonal_matrix(2, -4, 4)
    A = (P**-1) @ D @ P

    evals = set(D[i,i] for i in irange(1, 2))

    fakes = []
    while len(fakes) < 3:
        fake_evals = set([randint(-4, 4), randint(-4, 4)])
        if fake_evals != evals and fake_evals not in fakes:
            fakes.append(fake_evals)

    text(rf"""
    What are the eigenvalues of the matrix
    \[{A}\]
    """)

    multiple_choice_answer(True, rf"""\({",".join(str(e) for e in evals)}\)""")

    for fake in fakes:
        multiple_choice_answer(False, rf"""\({",".join(str(e) for e in fake)}\)""")

    end_question()
end_group()

begin_group()
for i in range(5):
    begin_numeric_question()

    P = rand_invertible_2x2(-10, 10)
    lam1 = randint(-4, 4)
    lam2 = randint(-4, 4)
    D = diagonal_matrix(lam1, lam2)
    A = (P**-1) @ D @ P

    text(rf"""
    Consider the matrix
    \[
    A={A}.
    \]
    What is the value of the largest eigenvalue of \(A\)?
    """)

    numeric_answer(max(lam1, lam2))

    end_question()
end_group()

begin_group()
for i in range(5):

    begin_numeric_question()

    a = randint_nonzero(-5,5)
    b = randint_nonzero(-5,5)
    A = matrix([a,-b],
               [b, a])

    text(rf"""
    What is the sum of the eigenvalues of the following matrix?
    \[
    A={A}
    \]
    """)

    numeric_answer(2*a)

    end_question()

end_group()

begin_group()
for i in range(5):

    begin_numeric_question()

    a = randint_nonzero(-5,5)
    b = randint_nonzero(-5,5)
    A = matrix([a,-b],
               [b, a])

    text(rf"""
    What is the absolute value of the difference of the the eigenvalues of the following matrix?
    \[
    A={A}
    \]
    """)

    numeric_answer(abs(2*b))

    end_question()

end_group()

begin_group()
for i in range(5):
    begin_numeric_question()

    P = rand_unimodular_2x2(-10, 10)
    lam1 = randint_nonzero(-4, 4)
    b = randint_nonzero(-4, 4)
    lam2 = var("a") - b
    D = diagonal_matrix(lam1, lam2)
    A = expand((P**-1) @ D @ P)

    text(rf"""
    Consider the matrix
    \[
    A={A}.
    \]
    What value of \(a\) makes \(A\) non-invertible?
    """)

    numeric_answer(b)

    end_question()
end_group()



end_quiz()
