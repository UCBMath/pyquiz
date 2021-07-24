from pyquiz.expr import *
from pyquiz.rand import *
from pyquiz import *

begin_quiz(
    title="Bad precision",
    description=rf"""Testing an impossible-to-answer question.
    
    This shows a pitfall in using precision for numeric questions in Canvas."""
)

begin_numeric_question()
text("The answer should be -0.67.")

numeric_answer(-0.6666666666666666, precision=2)

end_question()

end_quiz()
