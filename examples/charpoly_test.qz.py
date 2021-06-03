from pyquiz.expr import *
from pyquiz.rand import *
from pyquiz import *

seed(100)

begin_quiz(
    title="Charpoly test",
    description=rf"""Testing charpoly, det, and tr"""
)

begin_group()
for i in range(5):
    A = rand_matrix(4,4, -5,5)
    p = var("p")
    t = var("t")

    begin_text_only_question()
    text(rf"""
    Given
    $$A={A}$$
    then
    \begin{{align*}}
    \det A &= {det(A)} &
    \operatorname{{tr}} A &= {tr(A)}
    \end{{align*}}
    and the characteristic polynomial is
    $$p={charpoly(A)}$$
    Let's evaluate the characteristic polynomial at $0$ to get the determinant:
    $${charpoly(A, 0)}$$
    Let's take the third derivative, evaluate it at $0$, and divide by $-3!$ to get the trace:
    $${-frac(D(p,(t,3)), 6)} = {-frac(replace(D(charpoly(A),(t,3)), (t,0)), 6)}$$
    """)
    end_question()
end_group()

end_quiz()
