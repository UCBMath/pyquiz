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
          table.options { margin: 1em; }
          table.options th { text-align: right; padding: 2px 8px 2px 0; }
          div.question_group { border: 1px solid #ccc; padding: 0 5px 0 5px; margin-bottom: 1em; }
          div.question { border: 1px solid #ccf; padding-left: 0 5px 0 5px; margin-bottom: 0.5em; }
          body { max-width: 700px; }
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
        <p>Will replace quiz with id {id}.</p>
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
    <h2>Question group {group.name}</h2>
    <p>(picking {group.pick_count} question, {group.points} {"point" if group.points == 1 else "points"} each)</p>
    """)
    for q in group.questions:
        write_question(fout, q, i, in_group=True)
    fout.write(rf"""
    </div>
    """)

def write_question(fout, q, i, *, in_group=False):
    if in_group or q.points == None:
        points = ""
    elif q.points == 1:
        points = "(1 point)"
    else :
        points = f"({q.points} points)"

    def write_question_header(qtype):
        fout.write(f"""
        <div class="question">
        <h3>{i+1}. {qtype} {q.name or ""} {points}</h3>
        """)

        fout.write(rf"<p>{q.text}</p>")

    t = q.question_type

    if t == "text_only_question":
        write_question_header("Text-only question")
    elif t == "essay_question":
        write_question_header("Essay question")
    elif t == "file_upload_question":
        write_question_header("File upload question")
    elif t == "short_answer_question":
        write_question_header("Short answer question")
        fout.write("<ul>\n")
        for ans in q.answers:
            fout.write("<li>\n")
            if ans.correct:
                fout.write(f"Answer: {ans.text}")
            else:
                fout.write(f"Incorrect answer: {ans.text}")
            maybe_write_answer_comment(fout, ans)
            fout.write("</li>\n")
        fout.write("</ul>\n")
    elif t == "fill_in_multiple_blanks_question":
        write_question_header("Fill in multiple blanks question")
        fout.write("<ul>\n")
        for ans in q.answers:
            fout.write("<li>\n")
            fout.write("Answer" if ans.correct else "Incorrect answer")
            fout.write(f" for {ans.options['blank_id']}: {ans.text}")
            maybe_write_answer_comment(fout, ans)
            fout.write("</li>\n")
        fout.write("</ul>\n")
    elif t == "multiple_dropdowns_question":
        write_question_header("Multiple dropdowns question")
        fout.write("<ul>\n")
        for ans in q.answers:
            fout.write("<li>\n")
            fout.write("Answer" if ans.correct else "Incorrect answer")
            fout.write(f" for {ans.options['blank_id']}: {ans.text}")
            maybe_write_answer_comment(fout, ans)
            fout.write("</li>\n")
        fout.write("</ul>\n")
    elif t == "matching_question":
        write_question_header("Matching question")
        fout.write("<ul>\n")
        for ans in q.answers:
            fout.write("<li>\n")
            fout.write(f"Match {ans.options['match_left']!r} to {ans.options['match_right']!r}")
            maybe_write_answer_comment(fout, ans)
            fout.write("</li>\n")
        for inc in q.options['incorrect_matches']:
            fout.write("<li>\n")
            fout.write(f"Nothing matches to {inc!r}")
            fout.write("</li>\n")
        fout.write("</ul>\n")
    elif t == "numerical_question":
        write_question_header("Numeric question")
        fout.write("<ul>\n")
        for ans in q.answers:
            fout.write("<li>\n")
            nat = ans.options['numerical_answer_type']
            if nat == "exact_answer":
                fout.write(f"{ans.options['answer_exact']}")
                if ans.options['answer_error_margin']:
                    fout.write(f" &pm; {ans.options['answer_error_margin']}")
            elif nat == "precision_answer":
                fout.write(f"{ans.options['answer_approximate']}")
                fout.write(f" with precision {ans.options['answer_precision']} ")
            elif nat == "range_answer":
                fout.write(f"from {ans.options['answer_range_start']}")
                fout.write(f" to {ans.options['answer_range_end']}")
            else:
                raise Exception("Internal error: unknown numerical_answer_type")

            maybe_write_answer_comment(fout, ans)
            fout.write("</li>\n")
    elif t == "multiple_choice_question":
        checkbox = q.options['checkboxes']
        write_question_header("Multiple choices question")
        if checkbox:
            fout.write("<p>Checkboxes (select all options that apply)</p>")
        for ans in q.answers:
            fout.write("<div>\n")
            fout.write(f"""
            <input type={'checkbox' if checkbox else 'radio'}
                   {'checked' if ans.correct else ''}>
            <label>{ans.text}</label>
            """)
            maybe_write_answer_comment(fout, ans)
            fout.write("</div>\n")
    elif t == "true_false_question":
        write_question_header("True/false question")
        for ans in q.answers:
            fout.write("<div>\n")
            fout.write(f"""
            <input type=radio
                   {'checked' if ans.correct else ''}>
            <label>{ans.text}</label>
            """)
            fout.write("</div>\n")
    else:
        raise Exception(f"(internal error) Unknown question type {t}")

    if q.comment_correct:
        fout.write(f"""
        <p>Comment for correct answers: {q.comment_correct}</p>
        """)
    if q.comment_incorrect:
        fout.write(f"""
        <p>General for incorrect answers: {q.comment_incorrect}</p>
        """)
    if q.comment_general:
        fout.write(f"""
        <p>General comment (for all responses): {q.comment_general}</p>
        """)

    fout.write(f"""
    </div>
    """)

def maybe_write_answer_comment(fout, ans):
    if ans.comment:
        fout.write(rf"""<p>Comment for this answer: {ans.comment}</p>""")

def write_quizzes(filename, quizzes):
    print("Writing HTML to " + filename)
    with open(filename, "w") as fout:
        write_header(fout)
        for quiz in quizzes:
            write_quiz(fout, quiz)
        write_footer(fout)
