from canvasapi import Canvas
from pyquiz.config import API_URL, API_KEY

canvas = Canvas(API_URL, API_KEY)
course = canvas.get_course(1504554)

QUIZ = None

mathjax=r"""<p style="display: none;" aria-hidden="true"><math></math>Requires JavaScript to see MathJax.</p>"""

def begin_quiz(title=None, description=""):
    global QUIZ

    if not title:
        raise ValueError("Missing title for quiz")

    for quiz in course.get_quizzes(search_term=title):
        if quiz.title == title:
            print("Deleting old version")
            quiz.delete()

    QUIZ = course.create_quiz({
        'title': title,
        'description': f"{mathjax} {description}",
        'quiz_type': 'assignment',
        # time limit in minutes
        'time_limit': 22,
        # reorder multiple choice questions per student
        'shuffle_answers': True,
        # null, "always", or "until_after_last_attempt"
        'hide_results': "until_after_last_attempt",
        # -1 for unlimited attempts
        'allowed_attempts': -1,
        'one_question_at_a_time': True,
        'cant_go_back': True
    })

GROUP_ID = None

def begin_group(name="", pick_count=1, points=1):
    global GROUP_ID
    if GROUP_ID != None:
        raise Exception("Already in a group. Make sure to use end_group().")
    group = QUIZ.create_question_group([{
        'name': name,
        'pick_count': pick_count,
        'question_points': 2
    }])
    GROUP_ID = group.id

def end_group():
    global GROUP_ID
    if GROUP_ID == None:
        raise Exception("Not in a group.")
    GROUP_ID = None

QUESTION_DATA = None

def begin_numeric_question(name=''):
    global QUESTION_DATA
    if QUESTION_DATA != None:
        raise Exception("In a question. Make sure to use end_question().")
    QUESTION_DATA = {
        'question_name': name,
        'question_text': mathjax,
        'points_possible': 1,
        'quiz_group_id': GROUP_ID,
        'question_type': "numerical_question",
        'answers': []
    }

def begin_multiple_choice_question(name=''):
    global QUESTION_DATA
    if QUESTION_DATA != None:
        raise Exception("In a question. Make sure to use end_question().")
    QUESTION_DATA = {
        'question_name': name,
        'question_text': mathjax,
        'points_possible': 1,
        'quiz_group_id': GROUP_ID,
        'question_type': "multiple_choice_question",
        'answers': []
    }

def begin_true_false_question(name=''):
    global QUESTION_DATA
    if QUESTION_DATA != None:
        raise Exception("In a question. Make sure to use end_question().")
    QUESTION_DATA = {
        'question_name': name,
        'question_text': mathjax,
        'points_possible': 1,
        'quiz_group_id': GROUP_ID,
        'question_type': "true_false_question",
        'answers': []
    }


def text(s):
    QUESTION_DATA['question_text'] += s

def end_question():
    global QUESTION_DATA
    if QUESTION_DATA == None:
        raise Exception("Not in a question")
    QUIZ.create_question(question=QUESTION_DATA)
    QUESTION_DATA = None

def numeric_answer(val, precision=2):
    QUESTION_DATA['answers'].append({
        'weight': 100,
        'numerical_answer_type': 'precision_answer',
        'answer_approximate': val,
        'answer_precision': precision
    })

def multiple_choice_answer(correct, text):
    QUESTION_DATA['answers'].append({
        'weight': 100 if correct else 0,
        'text': text
    })

def true_false_answer(correct_value):
    QUESTION_DATA['answers'].append({
        'weight': 100,
        'text': "True" if correct_value else "False"
    })
    QUESTION_DATA['answers'].append({
        'weight': 0,
        'text': "False" if correct_value else "True"
    })

def end_quiz():
    global QUIZ, GROUP_ID, QUESTION_DATA
    if QUESTION_DATA != None:
        raise Exception("need to end_question()")
    if GROUP_ID != None:
        raise Exception("need to end_group()")
    if QUIZ == None:
        raise Exception("not in a quiz")
    print(f"Quiz {repr(QUIZ.title)} uploaded")
    QUIZ = None
