from pyquiz import *

begin_quiz(
    title="question_comments.qz.py example quiz",
    description=rf"""
    This quiz file contains some examples of feedback comments.
    """
)

begin_essay_question()
text(rf"""
Give a historical account of the essay and its development during the Age of Enlightenment.
""")
comment_general("We will grade your essay soon.")
end_question()

begin_short_answer_question()
text(rf"""
Repeat "after me".
""")
short_answer("after me")
answer_comment("Exactly.")
comment_general("This is quiz version of a common joke.")
comment_correct("You got it!")
comment_incorrect("The idea is to take the text between the quotes as the answer.")
end_question()

begin_short_answer_question()
text("The answer is A or B")
short_answer("A")
answer_comment("Awesome!")
short_answer("B")
answer_comment("Brilliant!")
end_question()

begin_matching_question()
text(rf"""
Match the letter to its index in the alphabet.
""")
matching_answer("A", "1")
answer_comment("Remember: 'A to Z' refers to A being the first and Z being the last letters of the alphabet.")
matching_answer("B", "2")
matching_answer("C", "3")
matching_distractor("300")
matching_distractor("5.4")
end_question()

end_quiz()
