from pyquiz.expr import *
from pyquiz.rand import *
from pyquiz import *

seed(100)

begin_quiz(
    title="Matrix test 2",
    description=rf"""Testing random matrices."""
)

begin_group()
for i in range(10):
    n = randint(3,4)
    m = randint(3,5)
    rk = randint(2,min(n,m))
    A = rand_matrix_rank(n,m, rk, 3)
    begin_multiple_choice_question()
    text(rf"""
    What is the rank of the following matrix?
    $${A}$$
    """)
    for i in irange(0, 4):
        multiple_choice_answer(rk == i, rf"{i}")

    steps = []
    Ared = row_reduce(A, steps_out=steps)
    steps_str = r"\\".join(steps)
    comment_general(rf"""
    Row reducing, we get
    $${A} \leadsto {Ared}$$
    This calculation reveals ${rk}$ leading $1$'s, so $A$ has ${rk}$ pivots, and hence the rank of $A$ is ${rk}$.

    If you want to check the row reduction, here are the steps we followed:
    \begin{{align*}}
    {steps_str}
    \end{{align*}}
    """)
    end_question()
end_group()

# [Hausen] Jürgen Hausen, "Generating problems in linear algebra."  [MapleTech. Volume 1, Number 2. Fall 1994.](https://www.researchgate.net/publication/322520524_MapleTech_Volume_1_no_2_-_Fall_1994)

# [Hausen] Exercise 1
begin_group()
for i in range(5):
    L = rand_matrix_rank(3,3, bound=6)
    R = rand_matrix_rank(3,3, bound=6)
    A = L @ diagonal_matrix(1, 1, 0) @ R
    a = vector(1, 0, 1)
    b = A @ a
    X = vector_of(var("x"), 3)
    # original question is open-ended. just doing true/false as an example
    begin_true_false_question()
    text(rf"""
    The general solution to the following linear system of equations
    {vector_align(A @ X, b)}
    can be given by
    $$\mathbf{{x}} = {a} + {b}t.$$
    """)
    end_question()
end_group()

# [Hausen] Exercise 2
begin_group()
for i in range(5):
    L = rand_matrix_rank(4,4, bound=1)
    R = rand_matrix_rank(4,4, bound=1)
    x = var("x")
    a, b = sample(irange(-2,2), 2)
    A = collect(L @ diagonal_matrix(x-a, 1, x-b, 1) @ R, [x])
    v1, v2, v3, v4 = cols(A)
    begin_multiple_choice_question(checkboxes=True)
    text(rf"""
    Consider the vectors $\mathbf{{v}}_1,\dots,\mathbf{{v}}_4$ in $\mathbb{{R}}^4$ given by
    $$\mathbf{{v}}_1 = {v1},\quad \mathbf{{v}}_2 = {v2},\quad \mathbf{{v}}_3 = {v3},\quad \mathbf{{v}}_4 = {v4}$$
    Find all real numbers $x$ such that these four vectors are not linearly independent.
    """)
    multiple_choice_answer(a == -2 or b == -2, "$-2$")
    multiple_choice_answer(a == -1 or b == -1, "$-1$")
    multiple_choice_answer(a == 0 or b == 0, "$0$")
    multiple_choice_answer(a == 1 or b == 1, "$1$")
    multiple_choice_answer(a == 2 or b == 2, "$2$")

    comment_general(rf"""
    The determinant of the matrix
    $${A}$$
    is ${collect(det(A), x)}$, which has roots ${a}$ and ${b}$.  These are exactly the values for which the columns of
    the matrix are linearly dependent.
    """)
    end_question()
end_group()

# [Hausen] Exercise 3
begin_group()
for i in range(5):
    B1 = rand_matrix_rank(3,3, bound=4)
    B2 = rand_matrix_rank(3,3, bound=4)
    T = B2**-1 @ B1

    begin_true_false_question()
    text(rf"""
    Consider the following two bases for $\mathbb{{R}}^3$:
    \begin{{align*}}
    B_1 &= {tex_list(cols(B1))} &
    B_2 &= {tex_list(cols(B2))}
    \end{{align*}}
    Is the following the matrix $T$ that takes coordinates with respect to $B_1$
    into coordinates with respect to $B_2$?
    $$T = {T}$$
    """)
    true_false_answer(True)
    end_question()
end_group()

# [Hausen] Exercise 5
begin_group()
for i in range(5):
    L = rand_matrix_rank(3,3, bound=2)
    R = rand_matrix_rank(3,3, bound=2)
    t = var("t")
    A = collect(L @ diagonal_matrix(1, t, 1) @ R, t)
    begin_multiple_choice_question()
    text(rf"""
    For which values of $t$ does the following matrix has an inverse with only integer entries?
    $${A}$$
    (Hint: Cramer's rule.)
    """)
    multiple_choice_answer(False, "Only $t=-1$")
    multiple_choice_answer(False, "Only $t=0$")
    multiple_choice_answer(False, "Only $t=1$")
    multiple_choice_answer(True, "Only when $t=1$ or $t=-1$")
    multiple_choice_answer(False, "All values of $t$")

    comment_general(rf"""
    The determinant of the matrix is ${collect(det(A), t)}$.
    The matrix has an inverse with only integer entries when the determinant is invertible,
    that is, when the determinant is $\pm 1$.
    """)
    end_question()
end_group()

end_quiz()
