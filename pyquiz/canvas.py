r"""
This is the quiz builder (see `pyquiz.builder`) for Canvas output.  Quiz writers should not need to refer to this module.
"""


from canvasapi import Canvas
from canvasapi.exceptions import ResourceDoesNotExist

# By adding this to a Canvas question, it enables MathJax for the page.
MATHJAX=r"""<p style="display: none;" aria-hidden="true"><math></math>Requires JavaScript enabled to see MathJax equations.</p>"""

class CanvasQuizBuilder:
    def __init__(self, api_url, api_key, course_id):
        self.canvas = Canvas(api_url, api_key)
        self.course = self.canvas.get_course(course_id)
        self.QUIZ = None
        self.GROUP_ID = None
        self.QUESTION_DATA = None

    def begin_quiz(self, id=None, title=None, description=""):
        """If the `id` is given, then edit the existing quiz (raising an error
        of no such quiz exists), otherwise look up a quiz by that
        title and if one with that title doesn't exist already, create
        one.  All existing questions are deleted.

        Warning: question groups will only be deleted if it has at
        least one question in it.  You may need to manually delete
        empty question groups in Canvas if they exist.
        """

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

        quiz = None

        if id != None:
            try:
                quiz = self.course.get_quiz(id)
            except ResourceDoesNotExist:
                raise Exception(f"There is no quiz yet with id {id}.")
            if quiz.title != title:
                # This is a safeguard against accidentally obliterating an existing quiz.
                raise Exception(f"The quiz with id {id} has the title {quiz.title!r}, not {title!r}.  Manually change the title in Canvas first.")
        else:
            # Is there a quiz with the same title? If so, edit it.
            for q in self.course.get_quizzes(search_term=title):
                if q.title == title:
                    quiz = q
                    break

        if quiz:
            if quiz.published:
                raise Exception(f"The quiz with title {title!r} has already been published.  Unpublish it in Canvas first.")
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
        else:
            # Create a new quiz
            print(f"Creating a new quiz")
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


    def begin_group(self, name="", pick_count=1, points=None):
        if self.GROUP_ID != None:
            raise Exception("Already in a group. Make sure to use end_group().")
        # Defer actually creating a question group -- the Canvas API
        # does not seem to give any way to let you find a list of all
        # existing question groups.
        self.GROUP_ID = "defer"
        self.GROUP_CONFIG = {
            'name': name,
            'pick_count': pick_count
        }
        if points != None:
            self.GROUP_CONFIG['question_points'] = points

    def end_group(self):
        if self.GROUP_ID == None:
            raise Exception("Not in a group.")
        if self.GROUP_ID == "defer":
            raise Exception("Empty question group.  All question groups must have at least one question.")
        self.GROUP_ID = None

    def text(self, s):
        if self.QUESTION_DATA == None:
            raise Exception("Not in a question.")
        self.QUESTION_DATA['question_text'] += s

    def begin_essay_question(self, name='', points=None):
        if self.QUESTION_DATA != None:
            raise Exception("In a question. Make sure to use end_question().")
        self.QUESTION_DATA = {
            'question_name': name,
            'question_text': MATHJAX,
            'question_type': "essay_question"
        }
        if points != None:
            self.QUESTION_DATA['points_possible'] = points

    def begin_file_upload_question(self, name='', points=None):
        if self.QUESTION_DATA != None:
            raise Exception("In a question. Make sure to use end_question().")
        self.QUESTION_DATA = {
            'question_name': name,
            'question_text': MATHJAX,
            'question_type': "file_upload_question"
        }
        if points != None:
            self.QUESTION_DATA['points_possible'] = points


    def begin_short_answer_question(self, name='', points=None):
        if self.QUESTION_DATA != None:
            raise Exception("In a question. Make sure to use end_question().")
        self.QUESTION_DATA = {
            'question_name': name,
            'question_text': MATHJAX,
            'question_type': "short_answer_question",
            'answers': []
        }
        if points != None:
            self.QUESTION_DATA['points_possible'] = points

    def short_answer(self, text):
        # TODO check if setting weight 0 is interesting
        self.QUESTION_DATA['answers'].append({
            'weight': 100,
            'text': text
        })

    def begin_fill_in_multiple_blanks_question(self, name='', points=None):
        if self.QUESTION_DATA != None:
            raise Exception("In a question. Make sure to use end_question().")
        self.QUESTION_DATA = {
            'question_name': name,
            'question_text': MATHJAX,
            'question_type': "fill_in_multiple_blanks_question",
            'answers': []
        }
        if points != None:
            self.QUESTION_DATA['points_possible'] = points

    def fill_in_multiple_blanks_answer(self, blank_id, text):
        self.QUESTION_DATA['answers'].append({
            'weight': 100,
            'blank_id': blank_id,
            'text': text
        })

    def begin_multiple_dropdowns_question(self, name='', points=None):
        if self.QUESTION_DATA != None:
            raise Exception("In a question. Make sure to use end_question().")
        self.QUESTION_DATA = {
            'question_name': name,
            'question_text': MATHJAX,
            'question_type': "multiple_dropdowns_question",
            'answers': []
        }
        if points != None:
            self.QUESTION_DATA['points_possible'] = points

    def multiple_dropdowns_answer(self, blank_id, correct, text):
        self.QUESTION_DATA['answers'].append({
            'weight': 100 if correct else 0,
            'blank_id': blank_id,
            'text': text
        })

    def begin_numeric_question(self, name='', points=None):
        if self.QUESTION_DATA != None:
            raise Exception("In a question. Make sure to use end_question().")
        self.QUESTION_DATA = {
            'question_name': name,
            'question_text': MATHJAX,
            'question_type': "numerical_question",
            'answers': []
        }
        if points != None:
            self.QUESTION_DATA['points_possible'] = points

    def numeric_answer(self, val, margin=None, precision=None):
        if margin != None and precision != None:
            raise ValueError("Not both margin and precision can be set")
        if margin == None and precision == None:
            margin = 0
        if margin != None:
            self.QUESTION_DATA['answers'].append({
                'weight': 100,
                'numerical_answer_type': 'exact_answer',
                'answer_exact': val,
                'answer_error_margin': margin
            })
        elif precision != None:
            self.QUESTION_DATA['answers'].append({
                'weight': 100,
                'numerical_answer_type': 'precision_answer',
                'answer_approximate': val,
                'answer_precision': precision
            })
        else:
            raise Exception

    def numeric_answer_range(self, lo, hi):
        self.QUESTION_DATA['answers'].append({
            'weight': 100,
            'numerical_answer_type': 'range_answer',
            'answer_range_start': lo,
            'answer_range_end': hi
        })

    def begin_multiple_choice_question(self, name='', points=None, checkboxes=False):
        if self.QUESTION_DATA != None:
            raise Exception("In a question. Make sure to use end_question().")
        self.QUESTION_DATA = {
            'question_name': name,
            'question_text': MATHJAX,
            'question_type': "multiple_answers_question" if checkboxes else "multiple_choice_question",
            'answers': []
        }
        if points != None:
            self.QUESTION_DATA['points_possible'] = points


    def multiple_choice_answer(self, correct, text):
        self.QUESTION_DATA['answers'].append({
            'weight': 100 if correct else 0,
            'text': text
        })

    def begin_true_false_question(self, name='', points=None):
        if self.QUESTION_DATA != None:
            raise Exception("In a question. Make sure to use end_question().")
        self.QUESTION_DATA = {
            'question_name': name,
            'question_text': MATHJAX,
            'question_type': "true_false_question",
            'answers': []
        }
        if points != None:
            self.QUESTION_DATA['points_possible'] = points


    def true_false_answer(self, correct_value):
        self.QUESTION_DATA['answers'].append({
            'weight': 100 if correct_value else 0,
            'text': "True",
        })
        self.QUESTION_DATA['answers'].append({
            'weight': 0 if correct_value else 100,
            'text': "False"
        })

    def end_question(self):
        if self.QUESTION_DATA == None:
            raise Exception("Not in a question")

        # Create the question group if deferred (why defer? Canvas
        # doesn't give you a way to get a list of question groups for
        # a quiz, so it's safest to guarantee there is at least one
        # question per question group)
        if self.GROUP_ID == "defer":
            group = self.QUIZ.create_question_group([self.GROUP_CONFIG])
            self.GROUP_ID = group.id
            self.GROUP_CONFIG = None
        self.QUESTION_DATA['quiz_group_id'] = self.GROUP_ID

        self.QUIZ.create_question(question=self.QUESTION_DATA)
        self.QUESTION_DATA = None
