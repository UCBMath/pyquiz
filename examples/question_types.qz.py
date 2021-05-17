from pyquiz import *

begin_quiz(
    title="question_types.qz.py example quiz",
    description=rf"""
    This quiz file contains an example of every quiz question type.
    """
)

begin_essay_question()
text(rf"""
Give a historical account of the essay and its development during the Age of Enlightenment.
""")
end_question()

begin_file_upload_question()
text(rf"""
Upload a file.
""")
end_question()

begin_text_only_question()
text(rf"""
Think about something then imagine the thought.
""")
end_question()

begin_short_answer_question()
text(rf"""
Repeat "after me".
""")
short_answer("after me")
end_question()

begin_fill_in_multiple_blanks_question()
text(rf"""
Roses are [color1] and violets are [color2].
""")
fill_in_multiple_blanks_answer("color1", "red")
fill_in_multiple_blanks_answer("color2", "blue")
end_question()

begin_multiple_dropdowns_question()
text(rf"""
Roses are [color1] and violets are [color2].
""")
multiple_dropdowns_answer("color1", True, "red")
multiple_dropdowns_answer("color1", False, "gray")
multiple_dropdowns_answer("color2", True, "blue")
multiple_dropdowns_answer("color2", False, "taupe")
end_question()

begin_matching_question()
text(rf"""
Match the letter to its index in the alphabet.
""")
matching_answer("A", "1")
matching_answer("B", "2")
matching_answer("C", "3")
matching_distractor("300")
matching_distractor("5.4")
end_question()

begin_numeric_question()
text(rf"""
The answer is \(2.2\) plus or minus \(0.2\), or \(31415\) with two digits of precision in scientific notation, or exactly \(100\), or anything between \(16\) and \(17\) inclusive.
""")
numeric_answer(2.2, margin=0.2)
numeric_answer(31415, precision=2)
numeric_answer(100) # margin=0
numeric_answer_range(16, 17)
end_question()

begin_multiple_choice_question()
text(rf"""
The answer is A or B.
""")
multiple_choice_answer(True, "A")
multiple_choice_answer(True, "B")
multiple_choice_answer(False, "C")
multiple_choice_answer(False, "D")
end_question()

begin_multiple_choice_question(checkboxes=True)
text(rf"""
The answer is both A and B.
""")
multiple_choice_answer(True, "A")
multiple_choice_answer(True, "B")
multiple_choice_answer(False, "C")
multiple_choice_answer(False, "D")
end_question()


begin_true_false_question()
text(rf"""
The answer is true.
""")
true_false_answer(True)
end_question()

end_quiz()
