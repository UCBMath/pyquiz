from pyquiz.expr import *
from pyquiz import *
import question_bank

begin_quiz(
    title="question_bank_quiz.qz.py",
    description=rf"""
    This is an example quiz.  It uses questions drawn from a question bank.
    """
)

question_bank.q1()

begin_group()
for i in range(5):
    question_bank.q2(i)
end_group()

question_bank.q3()

question_bank.q4()

question_bank.q5()

end_quiz()
