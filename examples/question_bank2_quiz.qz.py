from pyquiz.expr import *
from pyquiz.rand import *
from pyquiz import *
import question_bank2

# Set the seed for the pseudorandom number generator.  Without it,
# everytime you upload the quiz the questions will be different.
seed(22)

begin_quiz(
    title="question_bank2_quiz.qz.py",
    description=rf"""
    This is an example quiz using a question bank whose questions have random values.
    """
)

begin_group()
for i in range(10):
    question_bank2.q1()
end_group()

begin_group()
for i in range(10):
    question_bank2.q2()
end_group()

begin_group()
for i in range(10):
    question_bank2.q3()
end_group()

begin_group()
for i in range(10):
    question_bank2.q4()
end_group()

begin_group(pick_count=3)
question_bank2.true_false_bank()
end_group()

end_quiz()
