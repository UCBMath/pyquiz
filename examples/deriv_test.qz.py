from pyquiz.expr import *
from pyquiz.rand import *
from pyquiz import *

seed(100)

begin_quiz(
    title="Derivative test",
    description=rf""" <p>Testing derivatives and such.</p> """,

    quiz_type="practice_quiz",
    shuffle_answers=False,
    time_limit=None,
    allowed_attempts=-1,
    hide_results=None,
    show_correct_answers=True,
    one_question_at_a_time=True,
    cant_go_back=False # "lock questions after answering"
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

begin_group()
for i in range(10):
    begin_multiple_choice_question()

    y = var("y")
    lam = var("\\lambda")
    a, b, c = sample(irange(-10,-1) + irange(1,10), 3)

    text(rf"""Which is the auxiliary polynomial for the following differential equation?
    \[
    { a*D(y,t,t) + b*D(y,t) + c*y } = \cos t
    \]
    """)

    multiple_choice_answer(True, rf"""\({a*lam**2 + b*lam + c}\)""")
    multiple_choice_answer(False, rf"""\({c*lam**2 + b*lam + a}\)""")
    multiple_choice_answer(False, rf"""\({lam**2 + frac(b,a)*lam + frac(c,a)}\)""")
    multiple_choice_answer(False, rf"""\({(a*lam - 1) * (b*lam + c)}\)""")

    end_question()
end_group()

end_quiz()
