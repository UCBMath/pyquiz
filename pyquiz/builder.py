BUILDER = None

LOADED_QUIZZES = []

IN_QUIZ = False

def check_quiz_builder():
    if not BUILDER:
        raise Exception("No quiz builder is set.  Make sure to set_quiz_builder first.")

def set_quiz_builder(b):
    global BUILDER, LOADED_QUIZZES, IN_QUIZ
    BUILDER = b
    LOADED_QUIZZES = []
    IN_QUIZ = False

def get_loaded_quizzes():
    """Return a list of quiz titles that have been loaded so far."""
    return LOADED_QUIZZES

def is_in_quiz():
    return IN_QUIZ

def begin_quiz(title=None, description="", replace=True):
    global IN_QUIZ
    check_quiz_builder()
    LOADED_QUIZZES.append(title)
    IN_QUIZ = True
    BUILDER.begin_quiz(title=title, description=description, replace=replace)

def end_quiz():
    global IN_QUIZ
    check_quiz_builder()
    IN_QUIZ = False
    BUILDER.end_quiz()

def begin_group(name="", pick_count=1, points=1):
    check_quiz_builder()
    BUILDER.begin_group(name=name, pick_count=pick_count, points=points)

def end_group():
    check_quiz_builder()
    BUILDER.end_group()

def begin_numeric_question(name=''):
    check_quiz_builder()
    BUILDER.begin_numeric_question(name=name)

def begin_multiple_choice_question(name=''):
    check_quiz_builder()
    BUILDER.begin_multiple_choice_question(name=name)

def begin_true_false_question(name=''):
    check_quiz_builder()
    BUILDER.begin_true_false_question(name=name)

def text(s):
    check_quiz_builder()
    BUILDER.text(s)

def para(s):
    text("<p>" + s + "</p>")

def end_question():
    check_quiz_builder()
    BUILDER.end_question()

def numeric_answer(val, precision=2):
    check_quiz_builder()
    BUILDER.numeric_answer(val, precision=precision)

def multiple_choice_answer(correct, text):
    check_quiz_builder()
    assert isinstance(correct, bool)
    BUILDER.multiple_choice_answer(correct, text)

def true_false_answer(correct_value):
    check_quiz_builder()
    assert isinstance(correct_value, bool)
    BUILDER.true_false_answer(correct_value)