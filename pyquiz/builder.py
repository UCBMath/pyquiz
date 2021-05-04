r"""A quiz file is a plain Python file that executes quiz builder
functions, which are specified in this module.

Quizzes begin with `begin_quiz()` and end with `end_quiz()`.  Quiz
groups begin with `begin_group()` and end with `end_group()`.  Questions begin with one of the functions listed below and end with `end_question()`:

* `begin_numeric_question()` with `numeric_answer()`.

* `begin_multiple_choice_question()` with `multiple_choice_answer()`.

* `begin_true_false_question()` with `true_false_answer()`.

The text of a question is given by one or more `text()` and `para()` calls.

*(Internal: not for quiz authors.)* By setting the quiz builder with
`set_quiz_builder` before executing a quiz file (done by the uploader
UI for example), the resulting quiz can have different effects.  For
example, `pyquiz.html` creates an HTML output file, and
`pyquiz.canvas` uploads the quiz to Canvas.

"""

__all__ = [
    "begin_quiz", "end_quiz",
    "begin_group", "end_group",
    "text", "para",

    "begin_essay_question",
    "begin_file_upload_question",
    "begin_short_answer_question", "short_answer",
    "begin_fill_in_multiple_blanks_question", "fill_in_multiple_blanks_answer",
    "begin_multiple_dropdowns_question", "multiple_dropdowns_answer",
    "begin_numeric_question", "numeric_answer", "numeric_answer_range",
    "begin_multiple_choice_question", "multiple_choice_answer",
    "begin_true_false_question", "true_false_answer",
    "end_question",

    "set_quiz_builder", "get_loaded_quizzes", "is_in_quiz"
]

BUILDER = None

LOADED_QUIZZES = []

IN_QUIZ = False
IN_QUESTION_GROUP = False
IN_QUESTION = False

def set_quiz_builder(b):
    """*(Internal: not for quiz authors.)* Sets the current quiz builder."""
    global BUILDER, LOADED_QUIZZES, IN_QUIZ
    BUILDER = b
    LOADED_QUIZZES = []
    IN_QUIZ = False
    IN_QUESTION_GROUP = False
    IN_QUESTION = False

def get_loaded_quizzes():
    """*(Internal: not for quiz authors.)* Return a list of quiz titles that have been loaded so far.  This is
    used by the uploader UI to show the titles of quizzes that a file contained."""
    return LOADED_QUIZZES

def is_in_quiz():
    """*(Internal: not for quiz authors.)* Returns whether we are currently in a quiz (begun by
    `begin_quiz()`) without yet ending the quiz (by `end_quiz()`)."""
    return IN_QUIZ

def check_quiz_builder():
    """(Internal) Checks that there is currently a quiz builder set."""
    if not BUILDER:
        raise Exception("No quiz builder is set.  Make sure to set_quiz_builder first.")

def check_in_quiz():
    check_quiz_builder()
    if not IN_QUIZ:
        raise Exception("Not currently in a quiz.")

def check_in_question(question_type=True):
    check_in_quiz()
    if question_type == True:
        if not IN_QUESTION:
            raise Exception("Not currently in a question.")
    elif IN_QUESTION != question_type:
        raise Exception(f"Not currently in a {question_type} question.")

def begin_quiz(id=None, title=None, description=""):
    """Begin a new quiz.  The end of a quiz is marked with `end_quiz()`.

    * `title` is the title of the quiz, which shows up in the list of quizzes.
    * `description` is the description for the quiz, which is presented to students
      before they take the quiz.
    * `id` can be optionally supplied to replace a quiz with a specific id.

    If `id` is supplied, then that quiz will be replaced, thereby
    preserving any links to this specific quiz from elsewhere in the
    course website.  As a safeguard, the `title` *must* match the
    title of the quiz with that id.  To change the title of a quiz,
    edit the title manually in Canvas.

    Otherwise, if there is no id then a quiz with the given title, if
    one exists, will be replaced.

    In all cases, as a safeguard it is an error to try to replace a
    published quiz.  Unpublish the quiz first from Canvas.

    """
    global IN_QUIZ
    check_quiz_builder()
    if IN_QUIZ:
        raise Exception("Currently in a quiz.  Make sure to end_quiz() first.")
    if not title:
        raise ValueError("Missing a title for the quiz.")
    LOADED_QUIZZES.append(title)
    IN_QUIZ = True
    BUILDER.begin_quiz(id=id, title=title, description=description)

def end_quiz():
    """Finish the quiz started with `begin_quiz()`."""
    global IN_QUIZ
    check_in_quiz()
    if IN_QUESTION:
        raise Exception("Currently in a question. Make sure to end_question() first.")
    if IN_QUESTION_GROUP:
        raise Exception("Currently in a question group. Make sure to end_group() first.")
    IN_QUIZ = False
    BUILDER.end_quiz()

def begin_group(name="", pick_count=1, points=None):
    """Begin a new question group, which is ended with `end_group()`.
    All questions created between `begin_group()` and `end_group()` will be added
    to this question group.

    * `pick_count` specifies the number of questions from this group that Canvas will randomly choose for the student.
    * `points` specifies how many points each question in this question group is worth.

    For example, if `pick_count=3` and `points=2`, then this group accounts for 6 points of the quiz.

    """
    global IN_QUESTION_GROUP
    check_in_quiz()
    if IN_QUESTION_GROUP:
        raise Exception("Already in a question group. Make sure to end_group() first.")
    if IN_QUESTION:
        raise Exception("Currently in a question. Make sure to end_question() first.")
    IN_QUESTION_GROUP = True
    BUILDER.begin_group(name=name, pick_count=pick_count, points=points)

def end_group():
    """Ends the question group begun by a `begin_group()'."""
    global IN_QUESTION_GROUP
    if not IN_QUESTION_GROUP:
        raise Exception("Not currently in a question group.")
    IN_QUESTION_GROUP = False
    BUILDER.end_group()

def text(s):
    """Attach the given text to the current question."""
    check_in_question(True)
    BUILDER.text(s)

def para(s):
    """Attach the given text as a paragraph to the current question.  This simply wraps the text in an HTML paragraph tag."""
    check_in_question(True)
    text("<p>" + s + "</p>")

def begin_essay_question(name='', points=None):
    """Begin an essay question."""
    global IN_QUESTION
    check_in_quiz()
    IN_QUESTION = "essay"
    BUILDER.begin_essay_question(name=name, points=points)

def begin_file_upload_question(name='', points=None):
    """Begin a file upload question."""
    global IN_QUESTION
    check_in_quiz()
    IN_QUESTION = "file upload"
    BUILDER.begin_file_upload_question(name=name, points=points)

def begin_short_answer_question(name='', points=None):
    """Begin a short answer question."""
    global IN_QUESTION
    check_in_quiz()
    IN_QUESTION = "short answer"
    BUILDER.begin_short_answer_question(name=name, points=points)

def short_answer(text):
    """The answer to a short answer question"""
    check_in_question("short answer")
    BUILDER.short_answer(text)

def begin_fill_in_multiple_blanks_question(name='', points=None):
    """Begin a fill-in-multiple-blanks question."""
    global IN_QUESTION
    check_in_quiz()
    IN_QUESTION = "fill in multiple blanks"
    BUILDER.begin_fill_in_multiple_blanks_question(name=name, points=points)

def fill_in_multiple_blanks_answer(blank_id, text):
    """An answer to a fill-in-multiple-blanks question"""
    check_in_question("fill in multiple blanks")
    BUILDER.fill_in_multiple_blanks_answer(blank_id, text)

def begin_multiple_dropdowns_question(name='', points=None):
    """Begin a fill-in-multiple-blanks question."""
    global IN_QUESTION
    check_in_quiz()
    IN_QUESTION = "multiple dropdowns"
    BUILDER.begin_multiple_dropdowns_question(name=name, points=points)

def multiple_dropdowns_answer(blank_id, correct, text):
    """An answer to a multilpe dropdowns question"""
    check_in_question("multiple dropdowns")
    BUILDER.multiple_dropdowns_answer(blank_id, correct, text)

def begin_numeric_question(name='', points=None):
    """Begin a numeric question."""
    global IN_QUESTION
    check_in_quiz()
    IN_QUESTION = "numeric question"
    BUILDER.begin_numeric_question(name=name, points=points)

def numeric_answer(val, margin=None, precision=None):
    """The answer to a numeric question"""
    check_in_question("numeric question")
    BUILDER.numeric_answer(val, margin=margin, precision=precision)

def numeric_answer_range(val_lo, val_hi):
    """The answer to a numeric question"""
    check_in_question("numeric question")
    BUILDER.numeric_answer_range(val_lo, val_hi)


def begin_multiple_choice_question(name='', points=None, checkboxes=False):
    """Begin a multiple choice question.  Ended with `end_question()`.

    * If `checkboxes` is `True`, then multiple answers can be
      selected, and the student is expected to select all the correct
      answers.

    """
    global IN_QUESTION
    check_in_quiz()
    IN_QUESTION = "multiple choice"
    BUILDER.begin_multiple_choice_question(name=name, points=points, checkboxes=checkboxes)

def multiple_choice_answer(correct, text):
    """The answer to a multiple choice question.

    * `correct` is `True` or `False`, representing whether or not this
      is a correct answer.  There may be multiple correct answers.
    * `text` is how this response is shown to the student.

    """
    check_in_question("multiple choice")
    if not isinstance(correct, bool):
        raise ValueError("The first argument must be True or False")
    BUILDER.multiple_choice_answer(correct, text)

def begin_true_false_question(name='', points=None):
    """Begin a true/false question.  Ended with `end_question()`."""
    global IN_QUESTION
    check_in_quiz()
    IN_QUESTION = "true/false"
    BUILDER.begin_true_false_question(name=name, points=points)

def true_false_answer(correct_value):
    """The answer to a true/false question.
    * `correct_value` is `True` or `False` depending on whether the answer is "true" or "false."
    """
    check_in_question("true/false")
    if not isinstance(correct_value, bool):
        raise ValueError("The first argument must be True or False")
    BUILDER.true_false_answer(correct_value)

def end_question():
    """End the current question."""
    global IN_QUESTION
    if not IN_QUESTION:
        raise Exception("Not currently in a question")
    IN_QUESTION = False
    BUILDER.end_question()
