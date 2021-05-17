from pyquiz.expr import *
from pyquiz.rand import *
from pyquiz import *

seed(100)

x = var("x")

begin_quiz(title="Is the value zero?",
           description="Showing how to do a kind of true/false question.")

begin_group()
for i in range(10):
    begin_true_false_question()
    x = randint(0, 3)
    text(rf"""
    Suppose \(x = {x}\).  Is it true that \(x = 0\)?
    """)

    true_false_answer(x == 0)

    end_question()
end_group()

end_quiz()
