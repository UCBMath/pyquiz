from pyquiz.expr import *
from pyquiz.rand import *
from pyquiz import *

seed(100)

begin_quiz(
    title="Pivots test",
    description=rf"""Testing pivot positions and bases for colspace and nullspace"""
)

begin_group()
for i in range(20):
    r = randint(1,4)
    A = rand_matrix_rank(4,6, r=r, bound=5)

    begin_text_only_question()
    text(rf"""
    Given
    $$A={A}$$
    after row reducing we get
    $${row_reduce(A)}$$
    so we see it has pivot positions
    $${tex_list(pivots(A))}$$
    Hence, the column space has the basis
    $${tex_list(col_basis(A))}$$
    and the null space has the basis
    $${tex_list(null_basis(A))}$$
    """)
    end_question()
end_group()

end_quiz()
