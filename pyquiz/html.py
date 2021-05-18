r"""
Module to create previews of quizzes as HTML files.  Quiz authors should not need to refer to this module.

See `pyquiz.builder`.
"""

__all__ = [
    "write_quizzes"
]

def write_header(fout):
    fout.write(r"""
    <!doctype html>
    <html>
      <head>
        <script type="text/javascript" async
          src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.7/MathJax.js?config=TeX-MML-AM_CHTML">
        </script>
        <style>
          html { font-family: "Helvetica Neue",Helvetica,Arial,sans-serif; }
          body { line-height: 1.5; font-size: 16px; max-width: 700px; }
          table.options { margin: 1em; }
          table.options th { text-align: right; padding: 2px 8px 2px 0; }
          div.question_group { border: 1px solid #aaa; background-color: #fff; padding-left: 0; margin-bottom: 1em; }
          div.question_group_body { clear: left; padding: 10px 20px; }
          div.question { border: 1px solid #aaa; background-color: #fff; padding-left: 0; margin-bottom: 1em; }
          div.question_header {
            font-size: 1.2em; font-weight: bold; border-bottom: 1px solid #aaa; background-color: #f5f5f5;
            padding: 8px 20px; margin: 0;
          }
          span.name { }
          span.points { float: right; font-size: 0.9em; color: #595959; margin-top: 0.1em; }
          div.question_body { clear: left; padding: 5px 20px 20px 20px; }
          div.question_text { margin-top: 1.5em; margin-bottom: 1.5em; max-width: 100%; min-height: 5px; }
          .answer { padding: 5px; margin: 0; border-top: 1px solid #ddd; }
          div.quiz_comment {
            border: 1px solid #b5bfc7;
            background-image: linear-gradient(to bottom, #fff, #f4f5f6);
            border-radius: 5px;
            box-shadow: 0 1px 2px rgb(0 0 0 / 20%);
            font-size: 16px;
            min-width: 100px; padding: 14px; position: relative; margin: 16px 30px; text-align: left;
          }
          div.quiz_comment::before {
            border: 10px solid transparent; content: " "; height: 0; position: absolute; width: 0;
            border-bottom-color: #b5bfc7; left: 30px; top: -20px;
          }
          div.quiz_comment::after {
            border: 10px solid transparent; content: " "; height: 0; position: absolute; width: 0;
            border-bottom-color: #fff; left: 30px; top: -19px;
          }
        </style>
      </head>
      <body>
    """)
def write_footer(fout):
    fout.write(r"""
      </body>
    </html>
    """)

def write_quiz(fout, quiz):
    fout.write(rf"""
    <h1>{quiz.title}</h1>
    <p>Quiz description: {quiz.description}</p>
    """)
    if quiz.id != None:
        fout.write(f"""
        <p>Will replace quiz with id {quiz.id}.</p>
        """)
    if quiz.options:
        fout.write('<table class="options">')
        for k, v in quiz.options.items():
            fout.write(f"""<tr><th>{k}</th><td>{v}</td></tr>\n""")
        fout.write("</table>\n")
    for i, q in enumerate(quiz.questions):
        if q.is_group():
            write_group(fout, q, i)
        else:
            write_question(fout, q, i)

def write_group(fout, group, i):
    fout.write(rf"""
    <div class="question_group">
      <div class="question_header">
        <span class="name">Question group {group.name}</span>
        <span class="points">picking {group.pick_count} {"question" if group.pick_count == 1 else "questions"} for
          {group.points} {"pt" if group.points == 1 else "pts"} each</span>
      </div>
      <div class="question_group_body">
    """)
    for q in group.questions:
        write_question(fout, q, i, in_group=True)
    fout.write(rf"""
      </div>
    </div>
    """)

def write_question(fout, q, i, *, in_group=False):
    if in_group or q.points == None:
        points = ""
    elif q.points == 1:
        points = "1 pt"
    else :
        points = f"{q.points} pts"

    def write_question_header(qtype):
        fout.write(rf"""
        <div class="question">
          <div class="question_header">
            <span class="name">{i+1}. {qtype} {q.name or ""}</span>
            <span class="points">{points}</span>
          </div>
          <div class="question_body">
            <div class="question_text">{q.text}</div>
            <div class="question_answers">
        """)

    t = q.question_type

    if t == "text_only_question":
        write_question_header("Text-only question")
    elif t == "essay_question":
        write_question_header("Essay question")
    elif t == "file_upload_question":
        write_question_header("File upload question")
    elif t == "short_answer_question":
        write_question_header("Short answer question")
        fout.write("""<div class="answer"><ul>\n""")
        for ans in q.answers:
            fout.write("<li>\n")
            if ans.correct:
                fout.write(f"Answer: {ans.text}")
            else:
                fout.write(f"Incorrect answer: {ans.text}")
            maybe_write_answer_comment(fout, ans)
            fout.write("</li>\n")
        fout.write("</ul></div>\n")
    elif t == "fill_in_multiple_blanks_question":
        write_question_header("Fill in multiple blanks question")
        fout.write("""<div class="answer"><ul>\n""")
        for ans in q.answers:
            fout.write("<li>\n")
            fout.write("Answer" if ans.correct else "Incorrect answer")
            fout.write(f" for {ans.options['blank_id']}: {ans.text}")
            maybe_write_answer_comment(fout, ans)
            fout.write("</li>\n")
        fout.write("</ul></div>\n")
    elif t == "multiple_dropdowns_question":
        write_question_header("Multiple dropdowns question")
        fout.write("""<div class="answer"><ul>\n""")
        for ans in q.answers:
            fout.write("<li>\n")
            fout.write("Answer" if ans.correct else "Incorrect answer")
            fout.write(f" for {ans.options['blank_id']}: {ans.text}")
            maybe_write_answer_comment(fout, ans)
            fout.write("</li>\n")
        fout.write("</ul></div>\n")
    elif t == "matching_question":
        write_question_header("Matching question")
        fout.write("""<div class="answer"><ul>\n""")
        for ans in q.answers:
            fout.write("<li>\n")
            fout.write(f"Match {ans.options['match_left']!r} to {ans.options['match_right']!r}")
            maybe_write_answer_comment(fout, ans)
            fout.write("</li>\n")
        for inc in q.options['incorrect_matches']:
            fout.write("<li>\n")
            fout.write(f"Nothing matches to {inc!r}")
            fout.write("</li>\n")
        fout.write("</ul></div>\n")
    elif t == "numerical_question":
        write_question_header("Numeric question")
        fout.write("""<div class="answer"><ul>\n""")
        def float_str(x):
            x = float(x)
            if int(x) == x:
                return repr(int(x))
            else:
                return repr(x)
        for ans in q.answers:
            fout.write("<li>\n")
            nat = ans.options['numerical_answer_type']
            if nat == "exact_answer":
                fout.write(f"{float_str(ans.options['answer_exact'])}")
                if ans.options['answer_error_margin']:
                    fout.write(f" &pm; {ans.options['answer_error_margin']}")
            elif nat == "precision_answer":
                fout.write(f"{float_str(ans.options['answer_approximate'])}")
                fout.write(f" with precision {ans.options['answer_precision']} ")
            elif nat == "range_answer":
                fout.write(f"from {float_str(ans.options['answer_range_start'])}")
                fout.write(f" to {float_str(ans.options['answer_range_end'])}")
            else:
                raise Exception("Internal error: unknown numerical_answer_type")

            maybe_write_answer_comment(fout, ans)
            fout.write("</li>\n")
        fout.write("</ul></div>\n")
    elif t == "multiple_choice_question":
        checkbox = q.options['checkboxes']
        write_question_header("Multiple choice question")
        #if checkbox:
        #    fout.write("<p>Checkboxes (select all options that apply)</p>")
        for ans in q.answers:
            fout.write("<div class=answer>\n")
            fout.write(f"""
            <input type={'checkbox' if checkbox else 'radio'}
                   {'checked' if ans.correct else ''}>
            <label display="inline-block">{ans.text}</label>
            """)
            maybe_write_answer_comment(fout, ans)
            fout.write("</div>\n")
    elif t == "true_false_question":
        write_question_header("True/false question")
        for ans in q.answers:
            fout.write("<div class=answer>\n")
            fout.write(f"""
            <input type=radio
                   {'checked' if ans.correct else ''}>
            <label>{ans.text}</label>
            """)
            fout.write("</div>\n")
    else:
        raise Exception(f"(internal error) Unknown question type {t}")

    comments = ""

    if q.comment_correct:
        comments += f"""
        <p>General comment if correct: {q.comment_correct}</p>
        """
    if q.comment_incorrect:
        comments += f"""
        <p>General comment if incorrect: {q.comment_incorrect}</p>
        """
    if q.comment_general:
        comments += f"""
        <p>General comment: {q.comment_general}</p>
        """

    if comments:
        fout.write(f"""<div class="quiz_comment">{comments}</div>""")

    fout.write(f"""
        </div>
      </div>
    </div>
    """)

def maybe_write_answer_comment(fout, ans):
    if ans.comment:
        fout.write(rf"""<div class="quiz_comment">Comment for this answer: {ans.comment}</div>""")

def write_quizzes(filename, quizzes):
    print("Writing HTML to " + filename)
    with open(filename, "w") as fout:
        write_header(fout)
        for quiz in quizzes:
            write_quiz(fout, quiz)
        write_footer(fout)
