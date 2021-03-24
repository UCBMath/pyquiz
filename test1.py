from pyquiz.expr import *
from pyquiz.canvas import *

begin_quiz(
    title="Test Quiz 1",
    description=rf"""
    <p>This is an example quiz.  There is a single question with five different variations.</p>
    """
)

# Question 1

begin_numeric_question()

text("The answer is \(6\cdot 7\).")

numeric_answer(42)

end_question()

# Question 2

begin_group()

a = Var("a")
y = a**2 - 3*a + 1

# five different versions of the question
for i in range(5):

    begin_numeric_question()

    text(rf"""
    <p>Suppose \(a={i}\).  What is \(y={y}\)?</p>
    """)

    numeric_answer(replace(y, [(a, i)]),
                   precision=2)

    end_question()

end_group()

# Question 3

begin_multiple_choice_question()

text(rf"""
<p>What is another term for one-to-one?</p>
""")

multiple_choice_answer(True, "injective")
multiple_choice_answer(False, "surjective")
multiple_choice_answer(False, "bijective")
multiple_choice_answer(False, "trijective")
multiple_choice_answer(False, "postjective")
multiple_choice_answer(False, "prejective")
multiple_choice_answer(False, "epijective")

end_question()

# Question 4

begin_true_false_question()

text(r"""
<p>Suppose \(V\) is a vector space and \(\mathcal{B}_1\) and \(\mathcal{B}_2\) are two bases for \(V\).</p>

<p>The cardinalities of \(\mathcal{B}_1\) and \(\mathcal{B}_2\) are equal.</p>
""")

true_false_answer(True)

end_question()

end_quiz()
