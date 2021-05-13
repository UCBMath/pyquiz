from pyquiz.expr import *
from pyquiz.rand import *
from pyquiz import *

seed(100)

begin_quiz(
    title="Derivative test",
    description=rf""" <p>Testing derivatives and such.</p> """
)

begin_true_false_question()

y = var("y")
c = const("c")
f = y**2 + (2 + c)*y + E**t

text(rf"""True or false: With \(c\) a constant and \(y\) a function of \(t\), then
\[ \frac{{\partial}}{{\partial t}}\left({f}\right) = {Dt(f, t)}. \]
""")

true_false_answer(True)

end_question()

end_quiz()
