from pyquiz import *

begin_quiz(
    title="example (fails)",
    description=rf"""
    The question in this quiz has no text, which is likely a mistake, so pyquiz throws an exception.
    """
)

begin_multiple_choice_question()
end_question()

end_quiz()
