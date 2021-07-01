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

For questions that have answers, `end_question(shuffle_answers=True)`
can be used to randomize their order.  When paired with question
groups, this can simulate the corresponding quiz option on a
per-question basis.

Feedback can be provided to a student using the following functions:

* `comment_general()` for general comments about a question.

* `comment_correct()` for feedback about correctly answered questions.

* `comment_incorrect()` for feedback about incorrectly answered questions.

* `answer_comment()` for feedback about specific answers given by a student.

*(Internal: not for quiz authors.)* `reset_quiz_builder()` clears all
the global state, and after evaluating quiz files the resulting
quizzes can be accessed using `get_loaded_quizzes()`.  Two places quiz files are used are
`pyquiz.html` for creating HTML previews and `pyquiz.canvas` to upload them to Canvas.

"""

from numbers import Number
from .rand import shuffle
import pyquiz.dynamic

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

    "reset_quiz_builder", "get_loaded_quizzes", "is_in_quiz"
]

class Quiz:
    def __init__(self, *, id, title, description, options):
        self.id = id
        self.title = title
        self.description = description
        self.options = options
        self.questions = [] # a list of QuestionGroup and Question

class QuestionGroup:
    def __init__(self, *, name, pick_count, points):
        self.name = name
        self.pick_count = pick_count
        self.points = points
        self.questions = [] # a list of Question
    def is_group(self):
        return True

class TextState:
    def __init__(self, *, avoid_para=False):
        self.in_para = False
        self.in_eqn = None
        self.text = ""
        self.avoid_para = avoid_para # for single-paragraph, avoid p tag
    def append(self, s):
        if not self.text and s == " ":
            pass
        else:
            self.text += s
    def ensure_para(self):
        if not self.in_para:
            if self.avoid_para:
                if self.text:
                    self.text = "<p>" + self.text + "</p>\n<p>"
                    self.avoid_para = False
            else:
                self.text += "<p>"
            self.in_para = True
    def end_para(self):
        if self.in_para:
            if self.avoid_para:
                pass
            else:
                self.text += "</p>"
            self.in_para = False
    def finish_text(self):
        if self.in_eqn == "display":
            raise Exception("Expecting $$ to end display equation.")
        elif self.in_eqn == "inline":
            raise Exception("Expecting $ to end inline equation.")
        self.end_para()
        return self.text

    def process(self, s):
        i = 0
        while i < len(s):
            if ord(s[i]) <= 32: # control character up to and including space
                newlines = 0
                while i < len(s) and ord(s[i]) <= 32:
                    if s[i] == "\n":
                        newlines += 1
                    i += 1
                if newlines < 2:
                    self.append(" ")
                else:
                    self.end_para()
            elif i + 1 < len(s) and s[i] == "\\":
                # this is for the unlikely case that $ is being escaped.
                self.ensure_para()
                self.append(s[i:i+2])
                i += 2
            elif s[i] == "$":
                self.ensure_para()
                i += 1
                if i < len(s) and s[i] == "$":
                    i += 1
                    if self.in_eqn == "display":
                        self.append(r"\]")
                        self.in_eqn = None
                    elif self.in_eqn == "inline":
                        raise Exception("Closing inline equation with $$, not $.")
                    else:
                        self.append(r"\[")
                        self.in_eqn = "display"
                else:
                    if self.in_eqn == "display":
                        raise Exception("Closing display equation with $, not $$.")
                    elif self.in_eqn == "inline":
                        self.append(r"\)")
                        self.in_eqn = None
                    else:
                        self.append(r"\(")
                        self.in_eqn = "inline"
            else:
                self.ensure_para()
                self.append(s[i])
                i += 1

def process_text(s, *, avoid_para=False):
    ts = TextState(avoid_para=avoid_para)
    ts.process(s)
    return ts.finish_text()

class Question:
    def __init__(self, *, question_type, name, points, options=None):
        self.question_type = question_type
        self.name = name
        self.points = points
        self.options = options or {}
        self.text = None
        self.answers = []
        self.comment_general = None
        self.comment_correct = None
        self.comment_incorrect = None

        # for text processing
        self.text_state = TextState()
    def is_group(self):
        return False
    def finalize(self):
        self.text = self.text_state.finish_text()
        self.text_state = None

class Answer:
    def __init__(self, *, text, correct, options=None):
        self.text = text
        self.correct = correct
        self.options = options or {}
        self.comment = None

LOADED_QUIZZES = []
QUIZ = None
QUESTION_GROUP = None
QUESTION = None

def reset_quiz_builder():
    """*(Internal: not for quiz authors.)" Reset the state of the quiz
    builder.  Used before loading a new quiz file."""
    global LOADED_QUIZZES, QUIZ, QUESTION_GROUP, QUESTION
    LOADED_QUIZZES = []
    QUIZ = None
    QUESTION_GROUP = None
    QUESTION = None

def get_loaded_quizzes():
    """*(Internal: not for quiz authors.)* Return a list of quizzes that have been loaded so far."""
    return LOADED_QUIZZES

def is_in_quiz():
    """*(Internal: not for quiz authors.)* Returns whether we are currently in a quiz (begun by
    `begin_quiz()`) without yet ending the quiz (by `end_quiz()`)."""
    return QUIZ != None

def assert_in_quiz():
    """(private internal)"""
    if not QUIZ:
        raise Exception("Not currently in a quiz.  Make sure to begin_quiz() first.")

def assert_in_question(question_type=True):
    """(private internal) Check that we are currently in a question with
    the given `question_type`.  The special value `question_type=True`
    indicates "any type."""
    assert_in_quiz()
    if not QUESTION:
        raise Exception("Not currently in a question.")
    elif question_type != True and QUESTION.question_type != question_type:
        raise Exception(f"Expecting a {question_type} question, not {QUESTION.question_type}.")

def begin_quiz(*, id=None, title=None, description="", process_description=True,
               quiz_type=None, time_limit=None,
               scoring_policy="keep_highest",
               shuffle_answers=False,
               hide_results=None,
               show_correct_answers=True,
               allowed_attempts=1,
               show_correct_answers_last_attempt=False,
               one_question_at_a_time=False,
               cant_go_back=False,
               one_time_results=False):
    """Begin a new quiz.  The end of a quiz is marked with `end_quiz()`.

    * `title` is the title of the quiz, which shows up in the list of quizzes.
    * `description` is the description for the quiz, which is presented to students
      before they take the quiz.  If `process_description` is `True`, then the description
      is processed in a similar manner to question `text`.
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

    See [the Instructure documentation](https://canvas.instructure.com/doc/api/quizzes.html) for the meaning of the options.
    [This page](https://canvas.instructure.com/doc/api/live#!/quizzes.json/edit_quiz_put_3) might also be helpful.

    """
    global QUIZ
    if QUIZ:
        raise Exception("Currently in a quiz.  Make sure to end_quiz() first.")

    if not title:
        raise ValueError("Missing a title for the quiz.")

    quiz_type_opts = ("practice_quiz", "assignment", "graded_survey", "survey")
    if quiz_type != None and quiz_type not in quiz_type_opts:
        raise ValueError("quiz_type if set must be one of the following: " + ", ".join(quiz_type_opts))

    if time_limit != None and type(time_limit) != int:
        raise ValueError("time_limit if set must be an integer")

    scoring_policy_opts = ("keep_highest", "keep_latest")
    if scoring_policy not in scoring_policy_opts:
        raise ValueError("scoring_policy must be one of the following: " + ", ".join(scoring_policy_opts))

    hide_results_opts = ("always", "until_after_last_attempt")
    if hide_results != None and hide_results not in hide_results_opts:
        raise ValueError("hide_results must be None or one of the following: " + ", ".join(hide_results_opts))

    if type(allowed_attempts) != int or allowed_attempts < -1:
        raise ValueError("allowed_attempts must be an integer greater than or equal to -1")

    if process_description:
        description = process_text(description)

    options = {
        "quiz_type": quiz_type,
        "time_limit": time_limit,
        "scoring_policy": scoring_policy,
        "shuffle_answers": shuffle_answers,
        "hide_results": hide_results,
        "show_correct_answers": show_correct_answers,
        "allowed_attempts": allowed_attempts,
        "show_correct_answers_last_attempt": show_correct_answers_last_attempt,
        "one_question_at_a_time": one_question_at_a_time,
        "cant_go_back": cant_go_back,
        "one_time_results": one_time_results
    }

    QUIZ = Quiz(id=id, title=title, description=description, options=options)
    pyquiz.dynamic.enter()

def end_quiz():
    """Finish the quiz started with `begin_quiz()`.  Adds the quiz to the
    list of loaded quizzes and allows a new quiz to begin."""
    global QUIZ
    assert_in_quiz()
    if QUESTION:
        raise Exception("Currently in a question. Make sure to end_question() first.")
    if QUESTION_GROUP:
        raise Exception("Currently in a question group. Make sure to end_group() first.")
    LOADED_QUIZZES.append(QUIZ)
    QUIZ = None
    pyquiz.dynamic.leave()

def begin_group(name="", pick_count=1, points=1):
    """Begin a new question group, which is ended with `end_group()`.
    All questions created between `begin_group()` and `end_group()` will be added
    to this question group.

    * `pick_count` specifies the number of questions from this group that Canvas will randomly choose for the student.
    * `points` specifies how many points each question in this question group is worth.

    For example, if `pick_count=3` and `points=2`, then this group accounts for 6 points of the quiz.

    """
    global QUESTION_GROUP
    assert_in_quiz()
    if QUESTION_GROUP:
        raise Exception("Already in a question group. Make sure to end_group() first.")
    if QUESTION:
        raise Exception("Currently in a question. Make sure to end_question() first.")
    QUESTION_GROUP = QuestionGroup(name=name, pick_count=pick_count, points=points)
    QUIZ.questions.append(QUESTION_GROUP)
    pyquiz.dynamic.enter()

def end_group():
    """Ends the question group begun by a `begin_group()'."""
    global QUESTION_GROUP
    if not QUESTION_GROUP:
        raise Exception("Not currently in a question group.")
    if not QUESTION_GROUP.questions:
        raise Exception("Question groups must have at least one question.")
    QUESTION_GROUP = None
    pyquiz.dynamic.leave()

def text(s, process=True):
    """Attach the given text to the body of the current question.  This
    function can be used multiple times, concatenating the text.

    If `process` is `True`, then the text is processed in a couple
    useful ways.  First, double-newlines are turned into paragraph
    breaks as in LaTeX.  Second, `$` and `$$` are respectively turned
    into delimiters for inline and display equations (versus using
    `\(...\)` and `\[...\]`, which is what Canvas requires.)
    """
    assert_in_question(True)
    if not isinstance(s, str):
        raise ValueError("Expecting string")
    if process:
        QUESTION.text_state.process(s)
    else:
        QUESTION.text_state.ensure_para()
        QUESTION.text_state.append(s)

def para(s=None):
    """Like `text` but with a paragraph break before and after the text.
    If `s` is `None` then does a paragraph break."""
    assert_in_question(True)
    QUESTION.text_state.end_para()
    if s:
        QUESTION.text_state.process(s)
        QUESTION.text_state.end_para()

def comment_general(s, process=True):
    """Attach the given general comment to the current question.  This
    comment is always shown to the student after they take the quiz."""
    assert_in_question(True)
    if QUESTION.comment_general:
        raise Exception("Question already has a general comment")
    if process:
        s = process_text(s)
    QUESTION.comment_general = s

def comment_correct(s, process=True):
    """Attach the given comment for correct answers to the current
    question. This comment is shown to the student after they take the
    quiz if they got the question correct."""
    assert_in_question(True)
    if QUESTION.comment_correct:
        raise Exception("Question already has a comment for correct answers")
    if process:
        s = process_text(s)
    QUESTION.comment_correct = s

def comment_incorrect(s, process=True):
    """Attach the given comment for incorrect answers to the current
    question.  This comment is shown to the student after they take
    the quiz if they got the question incorrect.
    """
    assert_in_question(True)
    if QUESTION.comment_incorrect:
        raise Exception("Question already has a comment for incorrect answers")
    if process:
        s = process_text(s)
    QUESTION.comment_incorrect = s

def answer_comment(s, process=True):
    """Attach the given comment to the previous answer for the current
    question.  For most question types, this comment is shown to the
    student at the end of the quiz if they selected this answer.  In a
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
    assert_in_question(True)
    if QUESTION.question_type == "true_false_question":
        raise Exception("For true/false questions, use the keyword arguments for true_false_answer instead")
    if not QUESTION.answers:
        raise Exception("Question has no answers")
    if QUESTION.answers[-1].comment:
        raise Exception("Answer already has a comment")
    if process:
        s = process_text(s)
    QUESTION.answers[-1].comment = s

def add_question(question):
    """(private internal) Add the question to the current thing that accepts
    questions: the question group or the quiz itself."""
    global QUESTION
    if QUESTION_GROUP:
        QUESTION_GROUP.questions.append(question)
    else:
        QUIZ.questions.append(question)
    QUESTION = question
    pyquiz.dynamic.enter()

def add_answer(answer):
    """(private internal) Checks that there are no duplicate answers."""
    global QUESTION
    if QUESTION.answers == None:
        raise Exception("Question does not accept answers (internal error!)")
    if answer in QUESTION.answers:
        raise Exception("Question already has this answer (duplicate answer).")
    QUESTION.answers.append(answer)

def begin_text_only_question(name=''):
    """Begin a text-only question.  This is an answer-free question, useful
    for prompting reading, setting up the context for some following
    questions, or otherwise providing directions.  End with `end_question()`."""
    assert_in_quiz()
    q = Question(question_type="text_only_question",
                 name=name,
                 points=None)
    q.answers = None
    add_question(q)

def begin_essay_question(name='', points=1):
    """Begin a free-form essay question. End with `end_question()`."""
    assert_in_quiz()
    q = Question(question_type="essay_question",
                 name=name,
                 points=points)
    q.answers = None
    add_question(q)

def begin_file_upload_question(name='', points=1):
    """Begin a file upload question. End with `end_question()`."""
    assert_in_quiz()
    q = Question(question_type="file_upload_question",
                 name=name,
                 points=points)
    q.answers = None
    add_question(q)

def begin_short_answer_question(name='', points=1):
    """Begin a short-answer question.  Accepted answers are specified with
    calls to `short_answer()`. End with `end_question()`.
    """
    assert_in_quiz()
    add_question(Question(question_type="short_answer_question",
                          name=name,
                          points=points))

def short_answer(text):
    """The answer to a short answer question.  Can be called multiple
    times for multiple acceptible answers."""
    assert_in_question("short_answer_question")
    add_answer(Answer(text=text,
                      correct=True))

def begin_fill_in_multiple_blanks_question(name='', points=1):
    """Begin a fill-in-multiple-blanks question.  Each blank is given by
    text in square brackets (for example, "Roses are [color]"). End with
    `end_question()`."""
    assert_in_quiz()
    add_question(Question(question_type="fill_in_multiple_blanks_question",
                          name=name,
                          points=points))

def fill_in_multiple_blanks_answer(blank_id, text):
    """An answer to a fill-in-multiple-blanks question.  The `blank_id` is
    the text in square brackets in the body of the question."""
    assert_in_question("fill_in_multiple_blanks_question")
    add_answer(Answer(text=text,
                      correct=True,
                      options={"blank_id": blank_id}))

def begin_multiple_dropdowns_question(name='', points=1):
    """Begin a fill-in-multiple-blanks question, just like
    `begin_fill_in_multiple_blanks_question()` but the blanks are
    drop-down dialogs showing possible answers. Each blank is given by
    text in square brackets (for example, "Roses are [color]").  End
    with `end_question()`.
    """
    assert_in_quiz()
    add_question(Question(question_type="multiple_dropdowns_question",
                          name=name,
                          points=points))

def multiple_dropdowns_answer(blank_id, correct, text):
    """An answer to a multiple dropdowns question.  The `blank_id` refers
    to the text in square brackets in the body of the question, and
    `correct` is `True` or `False` whether it is one of the expected
    responses."""
    assert_in_question("multiple_dropdowns_question")
    if not isinstance(correct, bool):
        raise ValueError("The second argument must be True or False")
    add_answer(Answer(text=text,
                      correct=correct,
                      options={"blank_id": blank_id}))

def begin_matching_question(name='', points=1):
    """Begin a matching question.  A list of "left" items are matched
    against a set of "right" items, and the "right" items might have mixed
    amongst them a set of "distractors." End with `end_question()`."""
    assert_in_quiz()
    add_question(Question(question_type="matching_question",
                          name=name,
                          points=points,
                          options={"incorrect_matches": []}))

def matching_answer(left, right):
    """An answer to a matching question.  The "left" item is shown in a
    list in the left, and the "right" item is added to a set of things
    matched."""
    assert_in_question("matching_question")
    add_answer(Answer(text=None,
                      correct=None,
                      options={"match_left": left,
                               "match_right": right}))

def matching_distractor(text):
    """A distractor to a matching question.  Shows up in the set of "right" items."""
    assert_in_question("matching_question")
    QUESTION.options['incorrect_matches'].append(text)

def begin_numeric_question(name='', points=1):
    """Begin a numeric question.  Like `begin_short_answer_question()` but
    the answer is interpreted numerically. End with `end_question()`."""
    assert_in_quiz()
    add_question(Question(question_type="numerical_question",
                          name=name,
                          points=points))

def numeric_answer(val, margin=None, precision=None):
    """The answer to a numeric question.

    * If `margin` is set, then an acceptible answer is `val` plus or minus `margin`.

    * If `precision` is set, then an acceptible answer is that number
      of decimal places of `val` in scientific notation.

    If neither `margin` nor `precision` is set, then `margin=0`,
    meaning an exact answer.  At most one can be set.

    A numeric question may have multiple `numeric_answer()` and `numeric_answer_range()` calls.
    """
    if not isinstance(val, Number):
        raise ValueError("Expecting number")
    assert_in_question("numerical_question")
    if margin != None and precision != None:
        raise ValueError("Not both margin and precision can be set")
    if margin == None and precision == None:
        margin = 0
    if margin != None:
        if not isinstance(margin, Number):
            raise ValueError("The margin must be a number.")
        add_answer(Answer(text=None,
                          correct=True,
                          options={"numerical_answer_type": "exact_answer",
                                   "answer_exact": float(val),
                                   "answer_error_margin": margin}))
    else:
        if not isinstance(precision, Number):
            raise ValueError("The precision must be a number.")
        add_answer(Answer(text=None,
                          correct=True,
                          options={"numerical_answer_type": "precision_answer",
                                   "answer_approximate": float(val),
                                   "answer_precision": precision}))

def numeric_answer_range(val_lo, val_hi):
    """The answer to a numeric question, where the answer lies in the
    closed interval `[val_lo, val_hi]`.

    A numeric question may have multiple `numeric_answer()` and `numeric_answer_range()` calls.

    """
    if not isinstance(val_lo, Number):
        raise ValueError("Expecting lower bound to be number")
    if not isinstance(val_hi, Number):
        raise ValueError("Expecting upper bound to be number")
    if val_lo > val_hi:
        raise ValueError("Lower bound must be less than or equal to upper bound")
    assert_in_question("numerical_question")
    add_answer(Answer(text=None,
                      correct=True,
                      options={"numerical_answer_type": "range_answer",
                               "answer_range_start": float(val_lo),
                               "answer_range_end": float(val_hi)}))

def begin_multiple_choice_question(name='', points=1, checkboxes=False):
    """Begin a multiple choice question.  Ended with `end_question()`.

    * If `checkboxes` is `True`, then multiple answers can be
      selected, and the student is expected to select all the correct
      answers.

    End with `end_question()`.
    """
    assert_in_quiz()
    add_question(Question(question_type="multiple_choice_question",
                          name=name,
                          points=points,
                          options={"checkboxes": checkboxes}))

def multiple_choice_answer(correct, text, process=True):
    """The answer to a multiple choice question.

    * `correct` is `True` or `False`, representing whether or not this
      is a correct answer.  There may be multiple correct answers.
    * `text` is how this response is shown to the student.

    """
    assert_in_question("multiple_choice_question")
    if not isinstance(correct, bool):
        raise ValueError("The first argument must be True or False")
    if not isinstance(text, str):
        raise ValueError("The second argument must be a string")
    if process:
        text = process_text(text, avoid_para=True)
    add_answer(Answer(text=text,
                      correct=correct))

def begin_true_false_question(name='', points=1):
    """Begin a true/false question.  Ended with `end_question()`.

    This is essentially a multiple choice question with two answers: "True" and "False"."""
    assert_in_quiz()
    add_question(Question(question_type="true_false_question",
                          name=name,
                          points=points))

def true_false_answer(correct_value, true_comment=None, false_comment=None):
    """The answer to a true/false question.
    * `correct_value` is `True` or `False` depending on whether the answer is "true" or "false."

    This function adds two answers, so it's not possible to use `answer_comment()`.  Instead:
    * If `true_comment` is set, then it will be the answer comment for "true".
    * If `false_comment` is set, then it will be the answer comment for "false".
    """
    assert_in_question("true_false_question")
    if not isinstance(correct_value, bool):
        raise ValueError("The first argument must be True or False")
    if QUESTION.answers:
        raise Exception("True/false question already has an answer")

    add_answer(Answer(text="True",
                      correct=correct_value))
    if true_comment:
        answer_comment(true_comment)

    add_answer(Answer(text="False",
                      correct=not correct_value))
    if false_comment:
        answer_comment(false_comment)

def end_question(*, shuffle_answers=False):
    """End the current question.

    * `shuffle_answers=True` indicates that the answers to the
      question should be randomly permuted.  If you create multiple
      copies of a question in a question group, this lets you mimick
      the "shuffle_answers" option for quizzes, but for a single
      question.
    """
    global QUESTION
    assert_in_question(True)
    if shuffle_answers:
        if not QUESTION.answers:
            raise Exception("No answers to shuffle.")
        shuffle(QUESTION.answers)
    QUESTION.finalize()
    if not QUESTION.text:
        raise Exception("Question has no text!")
    QUESTION = None
    pyquiz.dynamic.leave()
