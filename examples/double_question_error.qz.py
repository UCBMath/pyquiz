from pyquiz import *

begin_quiz(
    title="example (fails)",
    description=rf"""
    Two questions are created, but there's a missing end_question
    """
)

begin_multiple_choice_question()
begin_multiple_choice_question()
text("hi")
end_question()

end_quiz()
