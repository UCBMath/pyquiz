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
f = y**2 + (2 + c)*y + E**(2*t)

text(rf"""True or false: With \(c\) a constant and \(y\) a function of \(t\), then
\[ \frac{{d}}{{dt}}\left({f}\right) = {D(f, t)}. \]
""")

true_false_answer(True)

end_question()

begin_true_false_question()

y = var("y")
c = const("c")
f = y**2 + (2 + c)*y + E**(2*t)

text(rf"""True or false: With \(c\) a constant and \(y\) a function of \(t\), then
\[ \frac{{d^2}}{{d t^2}}\left({f}\right) = {D(f, t, t)}. \]
""")

true_false_answer(True)

end_question()


begin_true_false_question()

x = var("x")
y = var("y")
u = var("u")
f = x**2 * y**2 * u

text(rf"""True or false: With \(u\) a function of \(x\) and \(y\), then
\[ \frac{{\partial^2}}{{\partial x\, \partial y}}\left({f}\right) = {D(f, x, y)}. \]
""")

true_false_answer(True)

end_question()

begin_true_false_question()

c = const("c")
f = c[1] * cos(t) + c[2] * sin(3*t)

text(rf"""True or false:
\[ \frac{{d}}{{dt}}\left({f}\right) = {D(f, t)}. \]
""")

true_false_answer(True)

end_question()


end_quiz()
