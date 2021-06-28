r"""
This is the quiz uploader for Canvas output.  Quiz authors should not need to refer to this module.

See `pyquiz.builder`.
"""


from canvasapi import Canvas
from canvasapi.exceptions import ResourceDoesNotExist

# By adding this to a Canvas question, it enables MathJax for the page.
MATHJAX=r"""<p style="display: none;" aria-hidden="true"><math></math>Requires JavaScript enabled to see MathJax equations.</p>"""



class CanvasQuizUploader:
    def __init__(self, api_url, api_key, course_id):
        self.canvas = Canvas(api_url, api_key)
        self.course = self.canvas.get_course(course_id)

    def upload_quiz(self, quiz, overwrite_published=False):
        """If the `id` is given, then edit the existing quiz (raising an error
        of no such quiz exists), otherwise look up a quiz by that
        title and if one with that title doesn't exist already, create
        one.  All existing questions are deleted.

        Warning: question groups will only be deleted if it has at
        least one question in it.  You may need to manually delete
        empty question groups in Canvas if they exist.

        If `overwrite_published` is False, then if the quiz is already
        published, fail with an error.  Otherwise, it goes ahead and
        replaces the quiz.  See [this instructor guide](https://community.canvaslms.com/t5/Instructor-Guide/Once-I-publish-a-quiz-how-do-I-make-additional-changes/ta-p/1239)
        to learn about the consequences of doing this if students already have submissions.
        """

        quiz_config = {
            'title': quiz.title,
            'description': f"{MATHJAX} {quiz.description}",
        }
        quiz_config.update(quiz.options)

        self.quiz = self.create_quiz(quiz.id, quiz.title, quiz_config,
                                     overwrite_published=overwrite_published)

        for q in quiz.questions:
            if q.is_group():
                self.upload_group(q)
            else:
                self.upload_question(q)

        id = self.quiz.id
        self.quiz = None
        return id

    def upload_group(self, group):
        print(f"Uploading group with {len(group.questions)} questions")
        group_config = {
            'name': group.name,
            'pick_count': group.pick_count,
            'question_points': group.points
        }
        cgroup = self.quiz.create_question_group([group_config])
        for q in group.questions:
            self.upload_question(q, group_id=cgroup.id)

    def upload_question(self, q, *, group_id=None):
        if group_id == None:
            print(f"Uploading single question")
        def create_question(question_type, answers=None, options=None):
            question_data = {
                'question_name': q.name,
                'question_text': f"{MATHJAX} {q.text}",
                'question_type': question_type,
                'answers': answers or []
            }
            question_data.update(options or {})
            if group_id != None:
                question_data['quiz_group_id'] = group_id
            if q.comment_general:
                question_data['neutral_comments_html'] = q.comment_general
            if q.comment_correct:
                question_data['correct_comments_html'] = q.comment_correct
            if q.comment_incorrect:
                question_data['incorrect_comments_html'] = q.comment_incorrect

            # TODO: remove this when Canvas is fixed.
            # It is a workaround for an error in Canvas (as of deployment week of 2021/05/14)
            # that causes an internal error when the answers list is a list!
            if 'answers' in question_data:
                question_data['answers'] = dict(enumerate(question_data['answers']))

            if False:
                print("creating question ")
                import pprint
                pprint.pprint(question_data)
            self.quiz.create_question(question=question_data)

        t = q.question_type

        if t in ("text_only_question", "essay_question", "file_upload_question"):
            create_question(t)
        elif t in ("short_answer_question", "true_false_question"):
            answers = []
            for ans in q.answers:
                answers.append({'answer_weight': 100 if ans.correct else 0,
                                'answer_text': ans.text,
                                'comments_html': ans.comment})
            create_question(t, answers=answers)
        elif t == "multiple_choice_question":
            if q.options['checkboxes']:
                t = "multiple_answers_question"
            answers = []
            for ans in q.answers:
                answers.append({'answer_weight': 100 if ans.correct else 0,
                                'answer_html': ans.text,
                                'comments_html': ans.comment})
            create_question(t, answers=answers)
        elif t in ("fill_in_multiple_blanks_question", "multiple_dropdowns_question"):
            answers = []
            for ans in q.answers:
                answers.append({'answer_weight': 100 if ans.correct else 0,
                                'blank_id': ans.options['blank_id'],
                                'answer_text': ans.text,
                                'comments_html': ans.comment})
            create_question(t, answers=answers)
        elif t == "matching_question":
            answers = []
            for ans in q.answers:
                answers.append({'answer_match_left': ans.options['match_left'],
                                'answer_match_right': ans.options['match_right'],
                                'comments_html': ans.comment})
            create_question(t, answers=answers,
                            options={
                                "matching_answer_incorrect_matches": "\n".join(q.options['incorrect_matches'])
                            })
        elif t == "numerical_question":
            answers = []
            for ans in q.answers:
                data = {'answer_weight': 100 if ans.correct else 0,
                        'comments_html': ans.comment}
                data.update(ans.options)
                answers.append(data)
            create_question(t, answers=answers)
        else:
            raise Exception(f"(internal error) Unknown question type {t}")


    def create_quiz(self, id, title, quiz_config, overwrite_published=False):
        """Find a quiz if it exists and delete questions.  If it doesn't exist, create it."""

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
                if overwrite_published:
                    print(f"Warning: the quiz with title {title!r} is already published.")
                    print("Pyquiz will not notify students that the quiz has been modified.")
                    print("Changes will not apply until you click \"Save it now\" in Canvas!")
                else:
                    raise Exception(f"The quiz with title {title!r} has already been published.  Unpublish it in Canvas first.")
            print(f"Editing quiz with id {quiz.id} and deleting all existing questions")
            groups = set()
            for question in quiz.get_questions():
                if question.quiz_group_id:
                    groups.add(question.quiz_group_id)
                question.delete()
            # there is apparently no API call to get all the question groups for a quiz!
            for gid in groups:
                quiz.get_quiz_group(gid).delete(gid) # TODO fix bug in canvasapi itself?
            quiz_config['notify_of_update'] = False
            return quiz.edit(quiz=quiz_config)
        else:
            # Create a new quiz
            print(f"Creating a new quiz")
            return self.course.create_quiz(quiz_config)

