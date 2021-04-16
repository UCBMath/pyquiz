from canvasapi import Canvas
from canvasapi.exceptions import ResourceDoesNotExist

# By adding this to a Canvas question, it enables MathJax for the page.
mathjax=r"""<p style="display: none;" aria-hidden="true"><math></math>Requires JavaScript to see MathJax.</p>"""

class CanvasQuizBuilder:
    def __init__(self, api_url, api_key, course_id):
        self.canvas = Canvas(api_url, api_key)
        self.course = self.canvas.get_course(course_id)
        self.QUIZ = None
        self.GROUP_ID = None
        self.QUESTION_DATA = None

    def begin_quiz(self, title=None, description="", replace=True):
        """If `replace` is `True`, then edit the quiz in-place (and delete all existing questions), preserving
        the quiz ID.  Otherwise delete all quizzes with the same title and start from scratch."""

        if not title:
            raise ValueError("Missing title for quiz")

        quiz_config = {
            'title': title,
            'description': f"{mathjax} {description}",
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
        self.QUIZ = None


    # TODO add warning if a question group is empty, since we won't be
    # able to delete it automatically when editing a quiz
    # (possibly: auto-delete the group if no questions were added, along with a warning that this is being done.)

    def begin_group(self, name="", pick_count=1, points=1):
        if self.GROUP_ID != None:
            raise Exception("Already in a group. Make sure to use end_group().")
        group = self.QUIZ.create_question_group([{
            'name': name,
            'pick_count': pick_count,
            'question_points': 2
        }])
        self.GROUP_ID = group.id

    def end_group(self):
        if self.GROUP_ID == None:
            raise Exception("Not in a group.")
        self.GROUP_ID = None


    def begin_numeric_question(self, name=''):
        if self.QUESTION_DATA != None:
            raise Exception("In a question. Make sure to use end_question().")
        self.QUESTION_DATA = {
            'question_name': name,
            'question_text': mathjax,
            'points_possible': 1,
            'quiz_group_id': self.GROUP_ID,
            'question_type': "numerical_question",
            'answers': []
        }

    def begin_multiple_choice_question(self, name=''):
        if self.QUESTION_DATA != None:
            raise Exception("In a question. Make sure to use end_question().")
        self.QUESTION_DATA = {
            'question_name': name,
            'question_text': mathjax,
            'points_possible': 1,
            'quiz_group_id': self.GROUP_ID,
            'question_type': "multiple_choice_question",
            'answers': []
        }

    def begin_true_false_question(self, name=''):
        if self.QUESTION_DATA != None:
            raise Exception("In a question. Make sure to use end_question().")
        self.QUESTION_DATA = {
            'question_name': name,
            'question_text': mathjax,
            'points_possible': 1,
            'quiz_group_id': self.GROUP_ID,
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
