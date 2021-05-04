from pyquiz import *

# This is a simple quiz with a multiple choice question and a
# true/false question.
#
# This is part of https://github.com/UCBMath/pyquiz/wiki/Tutorial%3A-Creating-a-simple-quiz

begin_quiz(
    title="Tutorial: simple quiz",
    description=r"""
    <p>This is a simple quiz.</p>

    <p>It has just two questions.</p>
    """
)

begin_multiple_choice_question()
text(r"""
What is \(6\cdot 9\)?
""")
multiple_choice_answer(False, "40")
multiple_choice_answer(False, "42")
multiple_choice_answer(False, "47")
multiple_choice_answer(True, "54")
end_question()

begin_true_false_question(points=2)
text(r"""
Every barber who shaves everyone shaves themself.
""")
true_false_answer(True)
end_question()

end_quiz()
