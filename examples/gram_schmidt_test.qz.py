from pyquiz.expr import *
from pyquiz.rand import *
from pyquiz import *

seed(100)

begin_quiz(
    title="Gram-Schmidt test",
    description=rf"""Testing Gram-Schmidt."""
)

# Example 6.4.4 of Lay
begin_text_only_question()
A = matrix([1, 0, 0],
           [1, 1, 0],
           [1, 1, 1],
           [1, 1, 1])
Q, R = gram_schmidt(A, normalize=True)
text(rf"""
Given
$$A = {A}$$
then $QR$ factorization gives
\begin{{align*}}
Q &= {Q} \\
R &= {R}
\end{{align*}}
And as expected,
$$QR = {Q@R}$$
""")
end_question()

begin_text_only_question()
A = matrix_of(var("a"), 2, 2)
Q,R = gram_schmidt(A, normalize=False)
text(rf"""
Given
$$A = {A}$$
then $QR$ factorization gives
\begin{{align*}}
Q &= {collect(Q, [var("a")[1,1], var("a")[1,2], var("a")[2,1], var("a")[2,2]])} \\
R &= {R}
\end{{align*}}
""")
end_question()

end_quiz()
