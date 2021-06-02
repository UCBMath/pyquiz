from pyquiz.expr import *
from pyquiz.rand import *
from pyquiz import *

seed(100)

begin_quiz(
    title="Block matrix test",
    description=rf"""Testing block matrices."""
)

begin_text_only_question()
A = var("A")
v = vector(1,2,3)
w = transpose(vector(4,5,6))
B = block_matrix([A, v], [w, vector(22)])
A0 = rand_matrix_rank(3,3)
B0 = replace(B, (A, A0))
text(rf"""
This is the internal representation of $B$: {repr(B)}

In TeX form, it is:
$$B = {B}$$

With
$$A = {A0}$$
then
$$B = {B0}$$
""")
end_question()

begin_text_only_question()
A = var("A")
v = vector(1,2,3)
B = matrix_with_cols(A, v)
A0 = rand_matrix_rank(3,3)
B0 = replace(B, (A, A0))
text(rf"""
This is the internal representation of $B$: {repr(B)}

In TeX form, it is:
$$B = {B}$$

With
$$A = {A0}$$
then
$$B = {B0}$$
""")
end_question()

begin_text_only_question()
A = var("A")
v = transpose(vector(1,2,3))
B = matrix_with_rows(A, v)
A0 = rand_matrix_rank(3,3)
B0 = replace(B, (A, A0))
text(rf"""
This is the internal representation of $B$: {repr(B)}

In TeX form, it is:
$$B = {B}$$

With
$$A = {A0}$$
then
$$B = {B0}$$
""")
end_question()


end_quiz()
