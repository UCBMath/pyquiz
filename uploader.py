import tkinter, tkinter.ttk
import tkinter.filedialog
import tkinter.messagebox
import os, sys, subprocess, traceback, json
import urllib.parse
import pyquiz, pyquiz.html
import pyquiz.dynamic

#import logging
#logging.basicConfig(level=logging.DEBUG)

NO_QUIZ_SELECT_MESSAGE = "No quiz file selected"
NO_QUIZ_SELECT_ERROR = "No quiz file selected."
NO_CANVAS_CONFIG = "Missing canvas_config.json file."
BAD_CANVAS_CONFIG_ERROR = "Malformed canvas_config.json file."
MISSING_END_QUIZ = "Missing end_quiz() in quiz file."
NO_PREVIEW_FILE = "Generate an HTML preview first."
NO_UPLOAD = "Need to upload a quiz to Canvas first."

UPLOADER_STATE_FILE = ".uploader_state.json"

quiz_file = None
uploader_state = None
canvas_config = None
canvas_config_error = None
the_canvas_config = None

def load_uploader_state():
    global uploader_state, quiz_file
    try:
        with open(UPLOADER_STATE_FILE, "r") as fin:
            uploader_state = json.load(fin)
    except:
        pass

    if not isinstance(uploader_state, dict):
        uploader_state = {}

    if "quiz_file" in uploader_state:
        quiz_file = uploader_state['quiz_file']

load_uploader_state()

def load_canvas_config():
    try:
        config_file = open("canvas_config.json", "r")
    except FileNotFoundError:
        canvas_config_error = NO_CANVAS_CONFIG
        return

    try:
        config = json.load(config_file)
    except:
        canvas_config_error = BAD_CANVAS_CONFIG_ERROR
        traceback.print_exc()
        return

    config_file.close()

    # look for old-style format (single entry rather than list)
    if type(config) == dict:
        config = [config]

    if type(config) != list or len(config) == 0:
        canvas_config_error = BAD_CANVAS_CONFIG_ERROR
        return

    for entry in config:
        if type(entry) != dict or "API_URL" not in entry:
            canvas_config_error = BAD_CANVAS_CONFIG_ERROR
            return
        if "name" not in entry:
            entry['name'] = entry['API_URL']

    global canvas_config, the_canvas_config
    canvas_config = config
    the_canvas_config = canvas_config[0]

    if 'canvas_config' in uploader_state:
        for entry in canvas_config:
            if entry['name'] == uploader_state['canvas_config']:
                the_canvas_config = entry
                break

load_canvas_config()

# Build UI

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
        tkinter.ttk.Button(button_frame, text='Ok', command=self.destroy).grid(row=1, column=1, sticky='e')

        self.textbox = tkinter.Text(text_frame, height=12)
        self.textbox.insert('1.0', detail)
        self.textbox.config(state='disabled')
        self.scrollb = tkinter.ttk.Scrollbar(text_frame, command=self.textbox.yview)
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
    pyquiz.dynamic.reset()
    with open(quiz_filename) as fin:
        with additional_path(os.path.dirname(quiz_filename)):
            c = compile(fin.read(), quiz_filename, 'exec')
            quiz_globals = {}
            exec(c, quiz_globals, quiz_globals)

    print("Loaded quizzes with titles: " + ", ".join(q.title for q in pyquiz.get_loaded_quizzes()))

def do_exec_quiz(quiz_filename):
    """Run exec_quiz and return the list of quizzes.  Show error popups on errors."""
    pyquiz.reset_quiz_builder()
    exec_quiz(quiz_file)
    if pyquiz.is_in_quiz():
        tkinter.messagebox.showerror("Error", MISSING_END_QUIZ)
        print("Error: " + MISSING_END_QUIZ)
        return
    return pyquiz.get_loaded_quizzes()

def get_html_file(quiz_file):
    #return quiz_file + ".html"
    return "preview.qz.py.html"

def preview_command():
    print("----")
    if quiz_file == None:
        tkinter.messagebox.showerror("Error", NO_QUIZ_SELECT_ERROR)
        return

    quizzes = do_exec_quiz(quiz_file)

    if quizzes:
        html_file = get_html_file(quiz_file)
        pyquiz.html.write_quizzes(html_file, quizzes)
        print("Click 'View' to open generated HTML file")
    else:
        print("No quizzes so did not generate HTML file")

def view_command():
    if quiz_file == None:
        tkinter.messagebox.showerror("Error", NO_QUIZ_SELECT_ERROR)
        return

    html_file = get_html_file(quiz_file)

    if not os.path.isfile(html_file):
        tkinter.messagebox.showerror("Error", NO_PREVIEW_FILE)
        return

    platform_open_file(html_file)

def platform_open_file(html_file):
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

    quizzes = do_exec_quiz(quiz_file)

    if not quizzes:
        print("No quizzes to upload")
        return

    uploader = pyquiz.canvas.CanvasQuizUploader(
        api_url=the_canvas_config['API_URL'],
        api_key=the_canvas_config['API_KEY'],
        course_id=the_canvas_config['COURSE_ID']
    )
    urls = []
    for quiz in quizzes:
        id = uploader.upload_quiz(quiz)
        print(f"Uploaded quiz {quiz.title!r} with id {id} to {the_canvas_config['name']!r}")
        url = urllib.parse.urljoin(the_canvas_config['API_URL'],
                                   f"courses/{the_canvas_config['COURSE_ID']}/quizzes/{id}")
        urls.append(url)
    uploaded_quizzes.configure(value=urls)
    uploaded_quizzes.set(urls[0])

    tkinter.messagebox.showinfo("Success",
                                "Uploaded the following quizzes: " + ", ".join(q.title for q in quizzes))

def view_upload_command():
    url = uploaded_quizzes.get()
    if not url:
        tkinter.messagebox.showerror("Error", NO_UPLOAD)
        return
    platform_open_file(url)

###
### Choose file
###

fileframe = tkinter.Frame(master=window, padx=10, pady=5)
fileframe.pack(fill=tkinter.X)
fileframe.columnconfigure(1, minsize=50, weight=1)
choose_button = tkinter.ttk.Button(master=fileframe, text="Choose quiz", command=choose_command)
choose_button.grid(row=0, column=0, sticky="W")
choose_label = tkinter.ttk.Label(master=fileframe, text=NO_QUIZ_SELECT_MESSAGE)
choose_label.grid(row=0, column=1, sticky="W")

update_choose_label()

###
### Preview quiz
###

preview_frame = tkinter.ttk.LabelFrame(master=window, borderwidth=2, relief=tkinter.RIDGE, padding=5,
                                       text="Generate HTML preview")
preview_frame.pack(fill=tkinter.X, padx=10, pady=5)

preview_buttons = tkinter.Frame(master=preview_frame)
preview_buttons.pack(anchor="w")

preview_generate = tkinter.ttk.Button(master=preview_buttons, text="Generate", command=preview_command)
preview_generate.grid(row=0, column=0)

preview_view = tkinter.ttk.Button(master=preview_buttons, text="View", command=view_command)
preview_view.grid(row=0, column=1)

###
### Upload quiz to Canvas
###

upload_frame = tkinter.ttk.LabelFrame(master=window, borderwidth=2, relief=tkinter.RIDGE, padding=5,
                                      text="Upload to Canvas")
upload_frame.pack(fill=tkinter.X, padx=10, pady=5)

if canvas_config_error != None:
    config_error_msg = tkinter.ttk.Label(master=upload_frame, text=canvas_config_error)
else:
    upload_buttons = tkinter.Frame(master=upload_frame)
    upload_buttons.pack(anchor="w")

    def canvas_dests_select(event):
        global the_canvas_config
        for entry in canvas_config:
            if entry['name'] == canvas_dests.get():
                the_canvas_config = entry
                uploader_state['canvas_config'] = the_canvas_config['name']
                save_uploader_state()
                return

    canvas_dests = tkinter.ttk.Combobox(master=upload_buttons, state="readonly",
                                        value=[entry['name'] for entry in canvas_config])
    canvas_dests.bind("<<ComboboxSelected>>", canvas_dests_select)
    canvas_dests.grid(row=0, column=0)
    canvas_dests.set(the_canvas_config['name'])
    canvas_dests_select(None)

    upload_button = tkinter.ttk.Button(master=upload_buttons, text="Upload", command=upload_command)
    upload_button.grid(row=0, column=1)

    uploaded_quizzes = tkinter.ttk.Combobox(master=upload_buttons, state="readonly", value=[])
    uploaded_quizzes.grid(row=1, column=0)
    view_uploaded_quizzes = tkinter.ttk.Button(master=upload_buttons, text="View", command=view_upload_command)
    view_uploaded_quizzes.grid(row=1, column=1)


###
### Stdout redirector
###

stdout_frame = tkinter.ttk.LabelFrame(master=window, borderwidth=2, relief=tkinter.RIDGE, padding=5,
                                      text="Messages (stdout)")
stdout_frame.pack(fill=tkinter.X, padx=10, pady=5)

stdout_text_frame = tkinter.Frame(master=stdout_frame)
stdout_text_frame.pack(fill=tkinter.X)
stdout_text_frame.rowconfigure(0, weight=1)
stdout_text_frame.columnconfigure(0, weight=1)

stdout_text = tkinter.Text(master=stdout_text_frame, height=12)
stdout_text.grid(row=0, column=0, sticky="nsew")

stdout_text_scroll = tkinter.ttk.Scrollbar(master=stdout_text_frame, command=stdout_text.yview)
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

window.mainloop()
