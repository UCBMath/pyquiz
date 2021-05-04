r"""A quiz file is a plain Python file that executes quiz builder
functions, which are specified in this module.

Quizzes begin with `begin_quiz()` and end with `end_quiz()`.  Quiz
groups begin with `begin_group()` and end with `end_group()`.  Questions begin with one of the functions listed below and end with `end_question()`:

* `begin_text_only_question()` for an ungraded answer-free portion of
  a quiz.  Useful for giving directions partway through a quiz or
  prompting some other work.

* `begin_short_answer_question()` with `short_answer()` for a question
  with a specified short answer, for example a one-word answer.

* `begin_numeric_question()` with `numeric_answer()` and
  `numeric_answer_range()` for a short answer that is interpreted
  numerically.

* `begin_multiple_choice_question()` with `multiple_choice_answer()`
  for standard multiple-choice questions.

* `begin_true_false_question()` with `true_false_answer()` for
  standard true/false questions.

* `begin_fill_in_multiple_blanks_question()` with
  `fill_in_multiple_blanks_answer()` for a fill-in-the-blanks question
  with multiple clozes.

* `begin_multiple_dropdowns_question()` with
  `multiple_dropdowns_answer()` for a fill-in-the-blanks question
  where each cloze is given as a drop-down dialog.

* `begin_matching_question()` with `matching_answer()` and
  `matching_distractor()` for a question where each item in a list is
  matched to one of a given set of items.

* `begin_essay_question()` for a free-form textual answer (not automatically graded).

* `begin_file_upload_question()` for a free-form answer, uploaded as a file (not automatically graded).

The text of a question is given by one or more `text()` and `para()` calls.

Feedback can be provided to a student using the following functions:

* `comment_general()` for general comments about a question.

* `comment_correct()` for feedback about correctly answered questions.

* `comment_incorrect()` for feedback about incorrectly answered questions.

* `answer_comment()` for feedback about specific answers given by a student.

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

    "begin_text_only_question",
    "begin_short_answer_question", "short_answer",
    "begin_numeric_question", "numeric_answer", "numeric_answer_range",
    "begin_multiple_choice_question", "multiple_choice_answer",
    "begin_true_false_question", "true_false_answer",
    "begin_fill_in_multiple_blanks_question", "fill_in_multiple_blanks_answer",
    "begin_multiple_dropdowns_question", "multiple_dropdowns_answer",
    "begin_matching_question", "matching_answer", "matching_distractor",
    "begin_essay_question",
    "begin_file_upload_question",

    "comment_general", "comment_correct", "comment_incorrect",
    "answer_comment",

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
    global BUILDER, LOADED_QUIZZES, IN_QUIZ, IN_QUESTION_GROUP, IN_QUESTION
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

def begin_group(name="", pick_count=1, points=1):
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
    """Attach the given text to the body of the current question."""
    check_in_question(True)
    BUILDER.text(s)

def para(s):
    """Attach the given text as a paragraph to the body of the current
    question.  This simply wraps the text in an HTML paragraph tag."""
    check_in_question(True)
    text("<p>" + s + "</p>")

def comment_general(s):
    """Attach the given general comment to the current question.  This
    comment is always shown to the student after they take the quiz."""
    check_in_question(True)
    BUILDER.comment_general(s)

def comment_correct(s):
    """Attach the given comment for correct answers to the current
    question. This comment is shown to the student after they take the
    quiz if they got the question correct."""
    check_in_question(True)
    BUILDER.comment_correct(s)

def comment_incorrect(s):
    """Attach the given comment for incorrect answers to the current
    question.  This comment is shown to the student after they take
    the quiz if they got the question incorrect.
    """
    check_in_question(True)
    BUILDER.comment_incorrect(s)

def answer_comment(s):
    """Attach the given comment to the previous answer to the current
    question.  This comment is shown to the student at the end of the
    quiz if they selected this answer for most question types.  In a
    matching question, an answer comment is shown if a student missed
    the match.

    For example,
    ```python
    begin_short_answer_question()
    text("The answer is A or B")
    short_answer("A")
    answer_comment("Awesome!")
    short_answer("B")
    answer_comment("Brilliant!")
    end_question()
    ```

    """
    check_in_question(True)
    BUILDER.answer_comment(s)

def begin_text_only_question(name=''):
    """Begin a text-only question.  This is an answer-free question, useful
    for prompting reading, setting up the context for some following
    questions, or otherwise providing directions.  End with `end_question()`."""
    global IN_QUESTION
    check_in_quiz()
    IN_QUESTION = "text only"
    BUILDER.begin_text_only_question(name=name)

def begin_essay_question(name='', points=1):
    """Begin a free-form essay question. End with `end_question()`."""
    global IN_QUESTION
    check_in_quiz()
    IN_QUESTION = "essay"
    BUILDER.begin_essay_question(name=name, points=points)

def begin_file_upload_question(name='', points=1):
    """Begin a file upload question. End with `end_question()`."""
    global IN_QUESTION
    check_in_quiz()
    IN_QUESTION = "file upload"
    BUILDER.begin_file_upload_question(name=name, points=points)

def begin_short_answer_question(name='', points=1):
    """Begin a short-answer question.  Accepted answers are specified with
    calls to `short_answer()`. End with `end_question()`.
    """
    global IN_QUESTION
    check_in_quiz()
    IN_QUESTION = "short answer"
    BUILDER.begin_short_answer_question(name=name, points=points)

def short_answer(text):
    """The answer to a short answer question.  Can be called multiple
    times for multiple acceptible answers."""
    check_in_question("short answer")
    BUILDER.short_answer(text)

def begin_fill_in_multiple_blanks_question(name='', points=1):
    """Begin a fill-in-multiple-blanks question.  Each blank is given by
    text in square brackets (for example, "Roses are [color]"). End with
    `end_question()`."""
    global IN_QUESTION
    check_in_quiz()
    IN_QUESTION = "fill in multiple blanks"
    BUILDER.begin_fill_in_multiple_blanks_question(name=name, points=points)

def fill_in_multiple_blanks_answer(blank_id, text):
    """An answer to a fill-in-multiple-blanks question.  The `blank_id` is
    the text in square brackets in the body of the question."""
    check_in_question("fill in multiple blanks")
    BUILDER.fill_in_multiple_blanks_answer(blank_id, text)

def begin_multiple_dropdowns_question(name='', points=1):
    """Begin a fill-in-multiple-blanks question, just like
    `begin_fill_in_multiple_blanks_question()` but the blanks are
    drop-down dialogs showing possible answers. Each blank is given by
    text in square brackets (for example, "Roses are [color]").  End
    with `end_question()`.
    """
    global IN_QUESTION
    check_in_quiz()
    IN_QUESTION = "multiple dropdowns"
    BUILDER.begin_multiple_dropdowns_question(name=name, points=points)

def multiple_dropdowns_answer(blank_id, correct, text):
    """An answer to a multiple dropdowns question.  The `blank_id` refers
    to the text in square brackets in the body of the question, and
    `correct` is `True` or `False` whether it is one of the expected
    responses."""
    check_in_question("multiple dropdowns")
    BUILDER.multiple_dropdowns_answer(blank_id, correct, text)

def begin_matching_question(name='', points=1):
    """Begin a matching question.  A list of "left" items are matched
    against a set of "right" items, and the "right" items might have mixed
    amongst them a set of "distractors." End with `end_question()`."""
    global IN_QUESTION
    check_in_quiz()
    IN_QUESTION = "matching question"
    BUILDER.begin_matching_question(name=name, points=points)

def matching_answer(left, right):
    """An answer to a matching question.  The "left" item is shown in a
    list in the left, and the "right" item is added to a set of things
    matched."""
    check_in_question("matching question")
    BUILDER.matching_answer(left, right)

def matching_distractor(text):
    """A distractor to a matching question.  Shows up in the set of "right" items."""
    check_in_question("matching question")
    BUILDER.matching_distractor(text)

def begin_numeric_question(name='', points=1):
    """Begin a numeric question.  Like `begin_short_answer_question()` but
    the answer is interpreted numerically. End with `end_question()`."""
    global IN_QUESTION
    check_in_quiz()
    IN_QUESTION = "numeric question"
    BUILDER.begin_numeric_question(name=name, points=points)

def numeric_answer(val, margin=None, precision=None):
    """The answer to a numeric question.

    * If `margin` is set, then an acceptible answer is `val` plus or minus `margin`.

    * If `precision` is set, then an acceptible answer is that number
      of decimal places of `val` in scientific notation.

    If neither `margin` nor `precision` is set, then `margin=0`,
    meaning an exact answer.  At most one can be set.

    A numeric question may have multiple `numeric_answer()` and `numeric_answer_range()` calls.
    """
    check_in_question("numeric question")
    BUILDER.numeric_answer(val, margin=margin, precision=precision)

def numeric_answer_range(val_lo, val_hi):
    """The answer to a numeric question, where the answer lies in the
    closed interval `[val_lo, val_hi]`.

    A numeric question may have multiple `numeric_answer()` and `numeric_answer_range()` calls.

    """
    check_in_question("numeric question")
    BUILDER.numeric_answer_range(val_lo, val_hi)


def begin_multiple_choice_question(name='', points=1, checkboxes=False):
    """Begin a multiple choice question.  Ended with `end_question()`.

    * If `checkboxes` is `True`, then multiple answers can be
      selected, and the student is expected to select all the correct
      answers.

    End with `end_question()`.
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

def begin_true_false_question(name='', points=1):
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
