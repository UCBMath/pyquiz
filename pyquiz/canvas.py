from canvasapi import Canvas
from canvasapi.exceptions import ResourceDoesNotExist

# By adding this to a Canvas question, it enables MathJax for the page.
MATHJAX=r"""<p style="display: none;" aria-hidden="true"><math></math>Requires JavaScript to see MathJax.</p>"""

class CanvasQuizBuilder:
    def __init__(self, api_url, api_key, course_id):
        self.canvas = Canvas(api_url, api_key)
        self.course = self.canvas.get_course(course_id)
        self.QUIZ = None
        self.GROUP_ID = None
        self.QUESTION_DATA = None

    def begin_quiz(self, title=None, description="", replace=True, id=None):
        """If the `id` is given, then edit the existing quiz.  Otherwise, look up the quiz by the title.  If one
        doesn't exist already, create one.  Otherwise, if `replace` is `True`, then edit the quiz in-place (and
        delete all existing questions), preserving the quiz ID.  Otherwise delete all quizzes with the same title
        and start from scratch."""

        if not title:
            raise ValueError("Missing title for quiz")

        quiz_config = {
            'title': title,
            'description': f"{MATHJAX} {description}",
            'quiz_type': 'assignment',
            # time limit in minutes
            'time_limit': 22,
            # reorder multiple choice questions per student
            'shuffle_answers': False, # note: reorders t/f too!
            # null, "always", or "until_after_last_attempt"
            'hide_results': "until_after_last_attempt",
            # -1 for unlimited attempts
            'allowed_attempts': -1,
            'one_question_at_a_time': True,
            'cant_go_back': True
        }

        if id != None:
            try:
                quiz = self.course.get_quiz(id)
            except ResourceDoesNotExist:
                raise Exception(f"There is no quiz yet with id {id}.")
            if quiz.title != title:
                # This is a safeguard against accidentally obliterating an existing quiz.
                raise Exception(f"The quiz with id {id} has the title {quiz.title!r}, not {title!r}.  Change it in Canvas first.")
            self.QUIZ = quiz
        else:
            # Is there a quiz with the same title? If so, edit it.
            for quiz in self.course.get_quizzes(search_term=title):
                if quiz.title == title:
                    if not replace:
                        print(f"Deleting quiz with id {quiz.id}")
                        quiz.delete()
                        continue
                    if quiz.published:
                        raise Exception(f"The quiz with title {title!r} has already been published")
                    print(f"Editing quiz with id {quiz.id} and deleting all existing questions")
                    quiz.edit(**quiz_config)
                    groups = set()
                    for question in quiz.get_questions():
                        if question.quiz_group_id:
                            groups.add(question.quiz_group_id)
                        question.delete()
                    # there is apparently no API call to get all the question groups for a quiz!
                    for gid in groups:
                        quiz.get_quiz_group(gid).delete(gid) # TODO fix bug in canvasapi itself?
                    self.QUIZ = quiz
                    break
            else:
                # Otherwise, create it
                self.QUIZ = self.course.create_quiz(quiz_config)


    def end_quiz(self):
        if self.QUESTION_DATA != None:
            raise Exception("need to end_question()")
        if self.GROUP_ID != None:
            raise Exception("need to end_group()")
        if self.QUIZ == None:
            raise Exception("not in a quiz")
        print(f"Uploaded quiz with id={self.QUIZ.id} and title={self.QUIZ.title!r}")
        self.QUIZ = None


    def begin_group(self, name="", pick_count=1, points=1):
        if self.GROUP_ID != None:
            raise Exception("Already in a group. Make sure to use end_group().")
        # Defer actually creating a question group -- the Canvas API
        # does not seem to give any way to let you find a list of all
        # existing question groups.
        self.GROUP_ID = "defer"
        self.GROUP_CONFIG = {
            'name': name,
            'pick_count': pick_count,
            'question_points': points
        }

    def end_group(self):
        if self.GROUP_ID == None:
            raise Exception("Not in a group.")
        if self.GROUP_ID == "defer":
            raise Exception("Empty question group.  All question groups must have at least one question.")
        self.GROUP_ID = None


    def begin_numeric_question(self, name=''):
        if self.QUESTION_DATA != None:
            raise Exception("In a question. Make sure to use end_question().")
        self.QUESTION_DATA = {
            'question_name': name,
            'question_text': MATHJAX,
            'points_possible': 1,
            'question_type': "numerical_question",
            'answers': []
        }

    def begin_multiple_choice_question(self, name=''):
        if self.QUESTION_DATA != None:
            raise Exception("In a question. Make sure to use end_question().")
        self.QUESTION_DATA = {
            'question_name': name,
            'question_text': MATHJAX,
            'points_possible': 1,
            'question_type': "multiple_choice_question",
            'answers': []
        }

    def begin_true_false_question(self, name=''):
        if self.QUESTION_DATA != None:
            raise Exception("In a question. Make sure to use end_question().")
        self.QUESTION_DATA = {
            'question_name': name,
            'question_text': MATHJAX,
            'points_possible': 1,
            'question_type': "true_false_question",
            'answers': []
        }


    def text(self, s):
        if self.QUESTION_DATA == None:
            raise Exception("Not in a question.")
        self.QUESTION_DATA['question_text'] += s

    def end_question(self):
        if self.QUESTION_DATA == None:
            raise Exception("Not in a question")

        # ensure GROUP_ID
        if self.GROUP_ID == "defer":
            group = self.QUIZ.create_question_group([self.GROUP_CONFIG])
            self.GROUP_ID = group.id
            self.GROUP_CONFIG = None
        self.QUESTION_DATA['quiz_group_id'] = self.GROUP_ID

        self.QUIZ.create_question(question=self.QUESTION_DATA)
        self.QUESTION_DATA = None

    def numeric_answer(self, val, precision=2):
        self.QUESTION_DATA['answers'].append({
            'weight': 100,
            'numerical_answer_type': 'precision_answer',
            'answer_approximate': val,
            'answer_precision': precision
        })

    def multiple_choice_answer(self, correct, text):
        self.QUESTION_DATA['answers'].append({
            'weight': 100 if correct else 0,
            'text': text
        })

    def true_false_answer(self, correct_value):
        self.QUESTION_DATA['answers'].append({
            'weight': 100 if correct_value else 0,
            'text': "True",
        })
        self.QUESTION_DATA['answers'].append({
            'weight': 0 if correct_value else 100,
            'text': "False"
        })
