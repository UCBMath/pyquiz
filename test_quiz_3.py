from pyquiz.expr import *
from pyquiz.rand import *
from pyquiz import *
import lib.lay_1_1

seed(22)

begin_quiz(
    title="Diagnostic: Module 1.1",
    description=rf""" <p>This short quiz is designed to be a quick test of your
    understanding for the material presented in the Module 1.1
    lecture.</p> """
)

# Q1

begin_true_false_question()
para(r"""
True or false: the following is an example of a linear system of equations in the variables
\(x_1\) and \(x_2\).
""")
text(r"""
\begin{align*}
x_1+2x_2&=3 \\
x_2&=1
\end{align*}
""")
true_false_answer(True)
end_question()

# Q2

begin_true_false_question()
para(r"""
True or false: the following is an example of a linear system of equations in the variables
\(x_1\) and \(x_2\).
""")
text(r"""
\begin{align*}
x_1+2x_2&=3 \\
x_1x_2&=1
\end{align*}
""")
true_false_answer(False)
end_question()

# Q3

begin_multiple_choice_question()
para(r"""
Which of the following defines <em>equivalence</em> of a pair of linear systems?
""")
multiple_choice_answer(False, "They have identical sets of equations.")
multiple_choice_answer(True, "They have the same solution set.")
multiple_choice_answer(False, "They have the same variables.")
end_question()

end_quiz()
