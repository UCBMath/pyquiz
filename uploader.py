import tkinter
import tkinter.filedialog
import tkinter.messagebox
import os, sys, subprocess, traceback, json
import pyquiz, pyquiz.html, pyquiz.canvas

NO_QUIZ_SELECT_MESSAGE = "No quiz file selected"
NO_QUIZ_SELECT_ERROR = "No quiz file selected."
NO_CANVAS_CONFIG_ERROR = "Missing canvas_config.json file.  See the documentation for how to create one."
BAD_CANVAS_CONFIG_ERROR = "Malformed canvas_config.json file."

root = tkinter.Tk()
root.title("PyQuiz Uploader")

class ErrorWindow(tkinter.Toplevel):
    def __init__(self, title, message, detail):
        super().__init__()
        self.title(title)
        self.minsize(350, 100)
        self.resizable(True, True)
        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)

        button_frame = tkinter.Frame(self)
        button_frame.grid(row=0, column=0, sticky='nsew')
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)

        text_frame = tkinter.Frame(self)
        text_frame.grid(row=1, column=0, padx=(7, 7), pady=(7, 7), sticky='nsew')
        text_frame.rowconfigure(0, weight=1)
        text_frame.columnconfigure(0, weight=1)

        tkinter.Message(button_frame, text=message, width=500).grid(row=0, column=0, columnspan=2, pady=(7, 7), padx=(7, 7), sticky='w')
        tkinter.Button(button_frame, text='Ok', command=self.destroy).grid(row=1, column=1, sticky='e')

        self.textbox = tkinter.Text(text_frame, height=12)
        self.textbox.insert('1.0', detail)
        self.textbox.config(state='disabled')
        self.scrollb = tkinter.Scrollbar(text_frame, command=self.textbox.yview)
        self.textbox.config(yscrollcommand=self.scrollb.set)
        self.textbox.grid(row=0, column=0, sticky='nsew')
        self.scrollb.grid(row=0, column=1, sticky='nsew')

def report_callback_error(self, exc, val, tb):
    traceback.print_exc()
    ErrorWindow("Exception",
                traceback.format_exception_only(exc, val)[-1].strip(),
                traceback.format_exc())
tkinter.Tk.report_callback_exception = report_callback_error

window = tkinter.Frame(master=root)
window.pack(fill=tkinter.BOTH, expand=True)

quiz_file = None

def choose_command():
    global quiz_file
    filepath = tkinter.filedialog.askopenfilename(
        filetypes=[("Quiz files (Python)", "*.py")]
    )
    if not filepath:
        choose_label['text'] = NO_QUIZ_SELECT_MESSAGE
        quiz_file = None
    else:
        choose_label['text'] = f"'{os.path.basename(filepath)}'"
        quiz_file = filepath

def exec_quiz(quiz_filename):
    exec(open(quiz_filename).read())

def preview_command():
    if quiz_file == None:
        tkinter.messagebox.showerror("Error", NO_QUIZ_SELECT_ERROR)
        return

    html_file = quiz_file + ".html"
    builder = pyquiz.html.HTMLQuizBuilder(html_file)
    pyquiz.set_quiz_builder(builder)

    exec_quiz(quiz_file)

    if pyquiz.is_in_quiz():
        raise Exception("Missing end_quiz()")

    print(pyquiz.get_loaded_quizzes())

    if sys.platform == "win32":
        # Windows
        os.startfile(html_file)
    elif sys.platform == "darwin":
        # Mac OS
        subprocess.call(["open", html_file])
    else:
        # Linux?
        subprocess.call(["xdg-open", html_file])

def upload_command():
    if quiz_file == None:
        tkinter.messagebox.showerror("Error", NO_QUIZ_SELECT_ERROR)
        return

    try:
        config_file = open("canvas_config.json", "r")
    except FileNotFoundError:
        tkinter.messagebox.showerror("Error", NO_CANVAS_CONFIG_ERROR)
        return

    try:
        config = json.load(config_file)
    except:
        tkinter.messagebox.showerror("Error", BAD_CANVAS_CONFIG_ERROR)
        traceback.print_exc()
        return

    builder = pyquiz.canvas.CanvasQuizBuilder(
        api_url=config['API_URL'],
        api_key=config['API_KEY'],
        course_id=config['COURSE_ID']
    )
    pyquiz.set_quiz_builder(builder)

    exec_quiz(quiz_file)

    if pyquiz.is_in_quiz():
        raise Exception("Missing end_quiz()")

    tkinter.messagebox.showinfo("Success",
                                "Uploaded the following quizzes: " + ", ".join(pyquiz.get_loaded_quizzes()))

###
### Choose file
###

fileframe = tkinter.Frame(master=window, padx=10, pady=10)
fileframe.pack(fill=tkinter.X)
fileframe.columnconfigure(1, minsize=50, weight=1)
choose_button = tkinter.Button(master=fileframe, text="Choose quiz", command=choose_command)
choose_button.grid(row=0, column=0, sticky="W")
choose_label = tkinter.Label(master=fileframe, text=NO_QUIZ_SELECT_MESSAGE, padx=3)
choose_label.grid(row=0, column=1, sticky="W")

###
### Preview quiz
###

preview_frame = tkinter.Frame(master=window, borderwidth=2, relief=tkinter.RIDGE, padx=5, pady=5)
preview_frame.pack(fill=tkinter.X, padx=10, pady=0)

preview_label = tkinter.Label(master=preview_frame, text="Generate HTML preview")
preview_label.pack(anchor="w")

#entry = tkinter.Entry(master=preview_frame)
#entry.pack()

preview_generate = tkinter.Button(master=preview_frame, text="Generate", command=preview_command)
preview_generate.pack(anchor="w")

###
### Upload quiz to Canvas
###

upload_frame = tkinter.Frame(master=window, borderwidth=2, relief=tkinter.RIDGE, padx=5, pady=5)
upload_frame.pack(fill=tkinter.X, padx=10, pady=10)

upload_label = tkinter.Label(master=upload_frame, text="Upload to Canvas")
upload_label.pack(anchor="w")

upload_button = tkinter.Button(master=upload_frame, text="Upload", command=upload_command)
upload_button.pack(anchor="w")

window.mainloop()
