class HTMLQuizBuilder:
    def __init__(self, filename):
        print("HTML quiz builder writing to " + filename)
        self.QUIZ = open(filename, "w")
        self.IN_GROUP = False
        self.QUESTION_DATA = None

    def write(self, s):
        self.QUIZ.write(s)

    def begin_quiz(self, id=None, title=None, description=""):
        if title == None:
            raise Exception("Missing quiz title.")
        self.write(f"""
        <!doctype html>
        <html>
        <head>
        <script type="text/javascript" async
          src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.7/MathJax.js?config=TeX-MML-AM_CHTML">
        </script>
        <style>
          div.question_group {{ border: 1px solid #ccc; padding: 0 5px 0 5px; margin-bottom: 1em; }}
          div.question {{ border: 1px solid #ccf; padding-left: 0 5px 0 5px; margin-bottom: 0.5em; }}
          body {{ max-width: 700px; }}
        </style>
        </head>
        <body>
        <h1>{title}</h1>
        <p>Quiz description: {description}</p>
        """)
        if id:
            self.write(f"""
            <p>Will replace quiz with id {id}.</p>
            """)

    def end_quiz(self):
        if self.QUESTION_DATA != None:
            raise Exception("need to end_question()")
        if self.IN_GROUP:
            raise Exception("need to end_group()")
        if self.QUIZ == None:
            raise Exception("not in a quiz")
        self.QUIZ.close()
        self.QUIZ = None

    def begin_group(self, name="", pick_count=1, points=1):
        if self.IN_GROUP:
            raise Exception("Already in a group. Make sure to use end_group().")
        self.IN_GROUP = True
        self.write(f"""
        <div class="question_group">
        <h2>Question group {name}</h2>
        <p>(picking {pick_count} question, {points} {"point" if points == 1 else "points"} each)</p>
        """)
        self.GROUP_HAS_QUESTION = False

    def end_group(self):
        if not self.IN_GROUP:
            raise Exception("Not in a group.")
        if not self.GROUP_HAS_QUESTION:
            raise Exception("Question group has no questions.")
        self.write(f"""
        </div>
        """)
        self.IN_GROUP = False

    def text(self, s):
        if self.QUESTION_DATA == None:
            raise Exception("Not currently in a question.")
        self.write(f"""

        {s}

        """)

    def maybe_points(self, points):
        if not self.IN_GROUP:
            if points == 1:
                return "(1 point)"
            else:
                return f"({points} points)"
        else:
            return ""

    def begin_text_only_question(self, name=''):
        if self.QUESTION_DATA != None:
            raise Exception("In a question. Make sure to use end_question().")

        self.write(f"""
        <div class="question">
        <h3>Text-only question {name}</h3>
        """)

        self.QUESTION_DATA = {
            'question_type': "text_only_question"
        }

    def begin_essay_question(self, name='', points=1):
        if self.QUESTION_DATA != None:
            raise Exception("In a question. Make sure to use end_question().")

        self.write(f"""
        <div class="question">
        <h3>Essay question {name} {self.maybe_points(points)}</h3>
        """)

        self.QUESTION_DATA = {
            'question_type': "essay_question"
        }

    def begin_file_upload_question(self, name='', points=1):
        if self.QUESTION_DATA != None:
            raise Exception("In a question. Make sure to use end_question().")

        self.write(f"""
        <div class="question">
        <h3>File upload question {name} {self.maybe_points(points)}</h3>
        """)

        self.QUESTION_DATA = {
            'question_type': "file_upload_question"
        }

    def begin_short_answer_question(self, name='', points=1):
        if self.QUESTION_DATA != None:
            raise Exception("In a question. Make sure to use end_question().")

        self.write(f"""
        <div class="question">
        <h3>Short answer question {name} {self.maybe_points(points)}</h3>
        """)

        self.QUESTION_DATA = {
            'question_type': "short_answer_question",
        }

    def short_answer(self, text):
        self.write(f"<p>Answer: {text}</p>")

    def begin_fill_in_multiple_blanks_question(self, name='', points=1):
        if self.QUESTION_DATA != None:
            raise Exception("In a question. Make sure to use end_question().")

        self.write(f"""
        <div class="question">
        <h3>Fill in multiple blanks question {name} {self.maybe_points(points)}</h3>
        """)

        self.QUESTION_DATA = {
            'question_type': "fill_in_multiple_blanks_question",
        }

    def fill_in_multiple_blanks_answer(self, blank_id, text):
        self.write(f"<p>Answer for {blank_id}: {text}</p>")

    def begin_multiple_dropdowns_question(self, name='', points=1):
        if self.QUESTION_DATA != None:
            raise Exception("In a question. Make sure to use end_question().")

        self.write(f"""
        <div class="question">
        <h3>Multiple dropdowns question {name} {self.maybe_points(points)}</h3>
        """)

        self.QUESTION_DATA = {
            'question_type': "multiple_dropdowns_question",
        }

    def multiple_dropdowns_answer(self, blank_id, correct, text):
        self.write(f"<p>Answer for {blank_id}: {text}")
        if correct:
            self.write(" <b>(answer)</b>")
        self.write("</p>")

    def begin_matching_question(self, name='', points=1):
        if self.QUESTION_DATA != None:
            raise Exception("In a question. Make sure to use end_question().")

        self.write(f"""
        <div class="question">
        <h3>Matching question {name} {self.maybe_points(points)}</h3>
        """)

        self.QUESTION_DATA = {
            'question_type': "matching_question",
        }

    def matching_answer(self, left, right):
        self.write(f"<p>Match {left!r} to {right!r}</p>")

    def matching_distractor(self, text):
        self.write(f"<p>Nothing matches to {text!r}</p>")

    def begin_numeric_question(self, name='', points=1):
        if self.QUESTION_DATA != None:
            raise Exception("In a question. Make sure to use end_question().")

        self.write(f"""
        <div class="question">
        <h3>Numeric question {name} {self.maybe_points(points)}</h3>
        """)

        self.QUESTION_DATA = {
            'question_type': "numerical_question",
        }

    def numeric_answer(self, val, margin=None, precision=None):
        if margin != None and precision != None:
            raise ValueError("Not both margin and precision can be set")
        if margin == None and precision == None:
            margin = 0
        if margin != None:
            self.write(f"<p>Numeric answer: {val}")
            if margin != 0:
                self.write(f" &pm; {margin}")
        elif precision != None:
            self.write(f"<p>Numeric answer: {val} with precision {precision}</p>")
        else:
            raise Exception

    def numeric_answer_range(self, lo, hi):
        self.write(f"<p>Numeric answer: from {lo} to {hi}</p>")

    def begin_multiple_choice_question(self, name='', points=1, checkboxes=False):
        if self.QUESTION_DATA != None:
            raise Exception("In a question. Make sure to use end_question().")

        self.write(f"""
        <div class="question">
        <h3>Multiple choice question {name} {self.maybe_points(points)}</h3>
        """)
        if checkboxes:
            self.write("<p>Checkboxes (select all options that apply)</p>")

        self.QUESTION_DATA = {
            'question_type': "multiple_choice_question",
        }

    def multiple_choice_answer(self, correct, text):
        if correct:
            self.write(f"<p>Choice: {text} <b>(answer)</b></p>")
        else:
            self.write(f"<p>Choice: {text}</p>")

    def begin_true_false_question(self, name='', points=1):
        if self.QUESTION_DATA != None:
            raise Exception("In a question. Make sure to use end_question().")

        self.write(f"""
        <div class="question">
        <h3>True/false question {name} {self.maybe_points(points)}</h3>
        """)

        self.QUESTION_DATA = {
            'question_type': "true_false_question",
        }

    def true_false_answer(self, correct_value):
        self.write(f"<p>Answer: {correct_value}</p>")

    def end_question(self):
        if self.QUESTION_DATA == None:
            raise Exception("Not in a question")
        self.write(f"""
        </div>
        """)
        self.QUESTION_DATA = None
        self.GROUP_HAS_QUESTION = True

