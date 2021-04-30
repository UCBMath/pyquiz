class HTMLQuizBuilder:
    def __init__(self, filename):
        print("HTML quiz builder writing to " + filename)
        self.QUIZ = open(filename, "w")
        self.IN_GROUP = False
        self.QUESTION_DATA = None

    def write(self, s):
        self.QUIZ.write(s)

    def begin_quiz(self, id=None, title=None, description="", replace=True):
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

    def begin_group(self, name="", pick_count=1, points=1):
        if self.IN_GROUP:
            raise Exception("Already in a group. Make sure to use end_group().")
        self.IN_GROUP = True
        self.write(f"""
        <div class="question_group">
        <h2>Question group {name}</h2>
        <p>(picking {pick_count} question, {points} points each)</p>
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

    def begin_numeric_question(self, name=''):
        if self.QUESTION_DATA != None:
            raise Exception("In a question. Make sure to use end_question().")

        self.write(f"""
        <div class="question">
        <h3>Numeric question {name}</h3>
        """)

        self.QUESTION_DATA = {
            'question_type': "numerical_question",
        }

    def begin_multiple_choice_question(self, name=''):
        if self.QUESTION_DATA != None:
            raise Exception("In a question. Make sure to use end_question().")

        self.write(f"""
        <div class="question">
        <h3>Multiple choice question {name}</h3>
        """)

        self.QUESTION_DATA = {
            'question_type': "multiple_choice_question",
        }

    def begin_true_false_question(self, name=''):
        if self.QUESTION_DATA != None:
            raise Exception("In a question. Make sure to use end_question().")

        self.write(f"""
        <div class="question">
        <h3>True/false question {name}</h3>
        """)

        self.QUESTION_DATA = {
            'question_type': "true_false_question",
        }

    def text(self, s):
        if self.QUESTION_DATA == None:
            raise Exception("Not currently in a question.")
        self.write(f"""

        {s}

        """)

    def end_question(self):
        if self.QUESTION_DATA == None:
            raise Exception("Not in a question")
        self.write(f"""
        </div>
        """)
        self.QUESTION_DATA = None
        self.GROUP_HAS_QUESTION = True

    def numeric_answer(self, val, precision=2):
        self.write(f"<p>Numeric answer: {val} with precision {precision}</p>")

    def multiple_choice_answer(self, correct, text):
        if correct:
            self.write(f"<p>Choice: {text} <b>(answer)</b></p>")
        else:
            self.write(f"<p>Choice: {text}</p>")

    def true_false_answer(self, correct_value):
        self.write(f"<p>Answer: {correct_value}</p>")

    def end_quiz(self):
        if self.QUESTION_DATA != None:
            raise Exception("need to end_question()")
        if self.IN_GROUP:
            raise Exception("need to end_group()")
        if self.QUIZ == None:
            raise Exception("not in a quiz")
        self.QUIZ.close()
        self.QUIZ = None
