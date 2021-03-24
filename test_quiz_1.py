from pyquiz.expr import *
from pyquiz.canvas import *
import lib.bank1

begin_quiz(
    title="Test Quiz 1",
    description=rf"""
    <p>This is an example quiz.  It uses questions drawn from a question bank.</p>
    """
)

lib.bank1.q1()

begin_group()
for i in range(5):
    lib.bank1.q2(i)
end_group()

lib.bank1.q3()

lib.bank1.q4()

lib.bank1.q5()

end_quiz()
