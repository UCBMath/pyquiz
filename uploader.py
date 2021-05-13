import tkinter
import tkinter.filedialog
import tkinter.messagebox
import os, sys, subprocess, traceback, json
import pyquiz, pyquiz.html

NO_QUIZ_SELECT_MESSAGE = "No quiz file selected"
NO_QUIZ_SELECT_ERROR = "No quiz file selected."
NO_CANVAS_CONFIG_ERROR = "Missing canvas_config.json file.  See the documentation for how to create one."
BAD_CANVAS_CONFIG_ERROR = "Malformed canvas_config.json file."
MISSING_END_QUIZ = "Missing end_quiz() in quiz file."
NO_PREVIEW_FILE = "Generate an HTML preview first."

UPLOADER_STATE_FILE = ".uploader_state.json"

root = tkinter.Tk()
root.geometry("+50+50")
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

window = tkinter.Frame(master=root, pady=5)
window.pack(fill=tkinter.BOTH, expand=True)

quiz_file = None

uploader_state = None

def save_uploader_state():
    try:
        with open(UPLOADER_STATE_FILE, "w") as fout:
            json.dump(uploader_state, fout)
    except:
        pass

def update_choose_label():
    if quiz_file:
        choose_label['text'] = f"'{os.path.basename(quiz_file)}'"
    else:
        choose_label['text'] = NO_QUIZ_SELECT_MESSAGE

def choose_command():
    global quiz_file
    options = {}
    if quiz_file:
        try:
            options['initialdir'] = os.path.dirname(quiz_file)
        except:
            pass
    filepath = tkinter.filedialog.askopenfilename(
        parent=root,
        filetypes=[("Quiz files", "*.py"),
                   ("All files", "*")],
        **options
    )
    if filepath:
        quiz_file = filepath
        uploader_state['quiz_file'] = filepath
        save_uploader_state()

    update_choose_label()

class additional_path:
    def __init__(self, path):
        self.path = path
    def __enter__(self):
        if self.path in sys.path:
            self.remove = False
        else:
            self.remove = True
            sys.path.insert(0, self.path)
    def __exit__(self, exc_type, exc_value, traceback):
        if self.remove:
            try:
                sys.path.remove(self.path)
            except ValueError:
                pass

def exec_quiz(quiz_filename):
    print("Executing quiz file " + quiz_filename)
    with open(quiz_filename) as fin:
        with additional_path(os.path.dirname(quiz_filename)):
            c = compile(fin.read(), quiz_filename, 'exec')
            quiz_globals = {}
            exec(c, quiz_globals, quiz_globals)

    print("Loaded quizzes with titles: " + ", ".join(pyquiz.get_loaded_quizzes()))

def get_html_file(quiz_file):
    #return quiz_file + ".html"
    return "preview.qz.py.html"

def preview_command():
    print("----")
    if quiz_file == None:
        tkinter.messagebox.showerror("Error", NO_QUIZ_SELECT_ERROR)
        return

    html_file = get_html_file(quiz_file)
    builder = pyquiz.html.HTMLQuizBuilder(html_file)
    pyquiz.set_quiz_builder(builder)

    exec_quiz(quiz_file)

    if pyquiz.is_in_quiz():
        tkinter.messagebox.showerror("Error", MISSING_END_QUIZ)
        print("Error: " + MISSING_END_QUIZ)
        return

    print("Click 'View' to open generated HTML file")

def view_command():
    if quiz_file == None:
        tkinter.messagebox.showerror("Error", NO_QUIZ_SELECT_ERROR)
        return

    html_file = get_html_file(quiz_file)

    if not os.path.isfile(html_file):
        tkinter.messagebox.showerror("Error", NO_PREVIEW_FILE)
        return

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
    import pyquiz.canvas
    print("----")
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
        tkinter.messagebox.showerror("Error", MISSING_END_QUIZ)
        print("Error: " + MISSING_END_QUIZ)
        return

    tkinter.messagebox.showinfo("Success",
                                "Uploaded the following quizzes: " + ", ".join(pyquiz.get_loaded_quizzes()))

###
### Choose file
###

fileframe = tkinter.Frame(master=window, padx=10, pady=5)
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
preview_frame.pack(fill=tkinter.X, padx=10, pady=5)

preview_label = tkinter.Label(master=preview_frame, text="Generate HTML preview")
preview_label.pack(anchor="w")

preview_buttons = tkinter.Frame(master=preview_frame)
preview_buttons.pack(anchor="w")

preview_generate = tkinter.Button(master=preview_buttons, text="Generate", command=preview_command)
preview_generate.grid(row=0, column=0)

preview_view = tkinter.Button(master=preview_buttons, text="View", command=view_command)
preview_view.grid(row=0, column=1)

###
### Upload quiz to Canvas
###

upload_frame = tkinter.Frame(master=window, borderwidth=2, relief=tkinter.RIDGE, padx=5, pady=5)
upload_frame.pack(fill=tkinter.X, padx=10, pady=5)

upload_label = tkinter.Label(master=upload_frame, text="Upload to Canvas")
upload_label.pack(anchor="w")

upload_button = tkinter.Button(master=upload_frame, text="Upload", command=upload_command)
upload_button.pack(anchor="w")

###
### Stdout redirector
###

stdout_frame = tkinter.Frame(master=window, borderwidth=2, relief=tkinter.RIDGE, padx=5, pady=5)
stdout_frame.pack(fill=tkinter.X, padx=10, pady=5)

stdout_label=tkinter.Label(master=stdout_frame, text="Messages (stdout)")
stdout_label.pack(anchor="w")

stdout_text_frame = tkinter.Frame(master=stdout_frame)
stdout_text_frame.pack(fill=tkinter.X)
stdout_text_frame.rowconfigure(0, weight=1)
stdout_text_frame.columnconfigure(0, weight=1)

stdout_text = tkinter.Text(master=stdout_text_frame, height=12)
stdout_text.grid(row=0, column=0, sticky="nsew")

stdout_text_scroll = tkinter.Scrollbar(master=stdout_text_frame, command=stdout_text.yview)
stdout_text_scroll.grid(row=0, column=1, sticky="nsew")
stdout_text.config(yscrollcommand=stdout_text_scroll.set)

class StdoutRedirector:
    def __init__(self, text, old_stdout):
        self.text = text
        self.old_stdout = old_stdout
    def write(self, s):
        self.old_stdout.write(s)
        self.text.insert("end", s)
        self.text.see(tkinter.END)
    def flush(self):
        self.old_stdout.flush()

sys.stdout = StdoutRedirector(stdout_text, sys.stdout)
sys.stderr = StdoutRedirector(stdout_text, sys.stderr)

try:
    with open(UPLOADER_STATE_FILE, "r") as fin:
        uploader_state = json.load(fin)
except:
    pass

if not isinstance(uploader_state, dict):
    uploader_state = {}

if "quiz_file" in uploader_state:
    quiz_file = uploader_state['quiz_file']
    update_choose_label()

window.mainloop()
