import os
import math
import random
import tkinter as tk

# ##= IMAGE SETTINGS =##

BACKGROUND_IMAGE = "math img.jpg"
LOGO_IMAGE = "logo.png"
ICON_IMAGE = "icon.png"

LOGO_SIZE = 70
IMAGE_EXTENSIONS = (".png",)

# ##= COLOUR SETTINGS =##

BG = "#EAF2F8"
NAVY = "#12304A"
BLUE = "#176B9A"
DARK_BLUE = "#105477"
LIGHT_BLUE = "#DCECF7"
WHITE = "#FFFFFF"

BODY = "#4E2A78"
BODY_TEXT = "#FFFFFF"
BODY_ACCENT = "#8EC4EA"
BODY_MUTED = "#D2C3E8"

OK_GREEN = "#5EE6A8"
BAD_RED = "#FF7A8C"

GREEN = "#16845B"
RED = "#C33D50"
GREY = "#4A5A6A"

HEADER_BLUE = "#8EC4EA"
BORDER = "#E8618C"
BORDER_HOVER = "#FFB703"

TOTAL_QUESTIONS = 10
CARD_WIDTH = 660
PROGRESS_W = 640


# ##= IMAGE SEARCH =##

def search_folders():

    folders = []

    try:
        folders.append(os.path.dirname(os.path.abspath(__file__)))
    except NameError:
        pass

    folders.append(os.getcwd())

    return folders


def find_image(file_name, fallback_names=None):

    if fallback_names is None:
        fallback_names = []

    folders = search_folders()

    if file_name:

        if os.path.isabs(file_name) and os.path.isfile(file_name):
            return file_name

        for folder in folders:

            candidate = os.path.join(folder, file_name)

            if os.path.isfile(candidate):
                return candidate

    for folder in folders:

        for name in fallback_names:

            for ext in IMAGE_EXTENSIONS:

                candidate = os.path.join(folder, name + ext)

                if os.path.isfile(candidate):
                    return candidate

    return None


# ##= MATH ICON =##

def make_math_icon(size=64):

    img = tk.PhotoImage(width=size, height=size)

    img.put(BORDER, to=(0, 0, size, size))
    img.put(NAVY, to=(4, 4, size - 4, size - 4))

    img.put(WHITE, to=(11, 19, 29, 22))
    img.put(WHITE, to=(18, 12, 21, 29))

    img.put(BORDER_HOVER, to=(35, 19, 53, 22))

    for i in range(-8, 9):

        img.put(
            HEADER_BLUE,
            to=(20 + i - 1, 44 + i - 1, 20 + i + 2, 44 + i + 2)
        )

        img.put(
            HEADER_BLUE,
            to=(20 + i - 1, 44 - i - 1, 20 + i + 2, 44 - i + 2)
        )

    img.put(WHITE, to=(35, 40, 53, 43))
    img.put(WHITE, to=(35, 47, 53, 50))

    return img


# ##= MAIN APPLICATION =##

class MathQuest:

    def __init__(self, root):

        self.root = root

        self.root.title("MATH QUIZ")
        self.root.geometry("960x930")
        self.root.minsize(820, 880)
        self.root.configure(bg=BG)
        self.root.resizable(True, True)

        self.score = 0
        self.question_number = 0
        self.attempt = 1

        self.minimum = 1
        self.maximum = 9

        self.answer_locked = False

        self.loadWindowIcon()
        self.loadLogo()
        self.createBackground()

        self.displayMenu()

    # ##= WINDOW ICON =##

    def loadWindowIcon(self):

        self.icon_photo = None

        if ICON_IMAGE:

            path = find_image(ICON_IMAGE, ["icon"])

            if path:

                try:
                    self.icon_photo = tk.PhotoImage(file=path)

                except Exception as error:
                    print(f"Could not load icon: {error}")

        if self.icon_photo is None:
            self.icon_photo = make_math_icon()

        try:
            self.root.iconphoto(True, self.icon_photo)

        except Exception as error:
            print(f"Could not set window icon: {error}")

    # ##= LOGO =##

    def loadLogo(self):

        self.logo_photo = None

        if not LOGO_IMAGE:
            return

        path = find_image(LOGO_IMAGE, ["logo"])

        if not path:
            return

        try:

            logo = tk.PhotoImage(file=path)

            factor = max(
                1,
                math.ceil(logo.width() / LOGO_SIZE),
                math.ceil(logo.height() / LOGO_SIZE)
            )

            self.logo_photo = logo.subsample(factor)

        except Exception as error:

            print(f"Could not load logo: {error}")

            self.logo_photo = None

    # ##= BACKGROUND =##

    def createBackground(self):

        self.bg_canvas = tk.Canvas(
            self.root,
            highlightthickness=0,
            bg=BG
        )

        self.bg_canvas.place(
            x=0,
            y=0,
            relwidth=1,
            relheight=1
        )

        self.bg_source = None
        self.bg_photo = None
        self.resize_job = None

        if BACKGROUND_IMAGE:

            path = find_image(BACKGROUND_IMAGE, ["background", "bg"])

            if path:
                self.setBackground(path)

        self.bg_canvas.bind("<Configure>", self.onResize)

        self.drawBackground()

    def setBackground(self, path):

        try:

            source = tk.PhotoImage(file=path)

        except Exception as error:

            print(f"Could not load background: {error}")
            print("Only PNG and GIF images are supported.")

            return False

        self.bg_source = source

        self.drawBackground()

        return True

    def onResize(self, event=None):

        if self.resize_job is not None:
            self.root.after_cancel(self.resize_job)

        self.resize_job = self.root.after(
            60,
            self.drawBackground
        )

    def drawBackground(self, event=None):

        self.resize_job = None

        if self.bg_source is None:

            self.drawGradient()
            return

        w = self.bg_canvas.winfo_width()
        h = self.bg_canvas.winfo_height()

        if w < 50:
            w = 900

        if h < 50:
            h = 820

        try:

            iw = self.bg_source.width()
            ih = self.bg_source.height()

            scale = max(w / iw, h / ih)

            if scale > 1:

                photo = self.bg_source.zoom(math.ceil(scale))

            elif scale < 0.5:

                photo = self.bg_source.subsample(int(1 / scale))

            else:

                photo = self.bg_source

        except Exception as error:

            print(f"Could not draw background: {error}")

            self.bg_source = None
            self.drawGradient()

            return

        self.bg_photo = photo

        self.bg_canvas.delete("gradient")
        self.bg_canvas.delete("bg_image")

        self.bg_canvas.create_image(
            w // 2,
            h // 2,
            image=self.bg_photo,
            anchor="center",
            tags="bg_image"
        )

        self.bg_canvas.tag_lower("bg_image")

    def drawGradient(self, event=None):

        w = self.bg_canvas.winfo_width()
        h = self.bg_canvas.winfo_height()

        if w < 50:
            w = 900

        if h < 50:
            h = 820

        stops = [
            (0.00, (8, 18, 82)),
            (0.50, (82, 24, 128)),
            (1.00, (140, 14, 40))
        ]

        def colour_at(t):

            for (t0, c0), (t1, c1) in zip(stops, stops[1:]):

                if t <= t1:

                    k = (t - t0) / (t1 - t0)

                    return "#%02x%02x%02x" % tuple(
                        int(c0[i] + (c1[i] - c0[i]) * k)
                        for i in range(3)
                    )

            return "#%02x%02x%02x" % stops[-1][1]

        bands = 90

        self.bg_canvas.delete("gradient")
        self.bg_canvas.delete("bg_image")

        for i in range(bands):

            a = 2.0 * i / bands
            b = 2.0 * (i + 1) / bands + 0.01

            mid = (a + b) / 4

            self.bg_canvas.create_polygon(
                a * w, 0,
                b * w, 0,
                0, b * h,
                0, a * h,
                fill=colour_at(mid),
                outline="",
                tags="gradient"
            )

        self.bg_canvas.tag_lower("gradient")

    # ##= SCREEN DESIGN =##

    def screen(self, title, subtitle, footer_text):

        self.clear_screen()

        card = tk.Frame(
            self.root,
            bg=BODY,
            highlightbackground=BORDER,
            highlightcolor=BORDER,
            highlightthickness=4
        )

        card.pack(expand=True)

        head = tk.Frame(card, bg=HEADER_BLUE)
        head.pack(fill="x")

        title_top = 32

        if self.logo_photo is not None:

            tk.Label(
                head,
                image=self.logo_photo,
                bg=HEADER_BLUE
            ).pack(pady=(20, 0))

            title_top = 8

        tk.Label(
            head,
            text=title,
            font=("Arial", 28, "bold"),
            fg=NAVY,
            bg=HEADER_BLUE
        ).pack(pady=(title_top, 2), padx=40)

        tk.Label(
            head,
            text=subtitle,
            font=("Arial", 10, "bold"),
            fg=NAVY,
            bg=HEADER_BLUE
        ).pack(pady=(0, 28))

        tk.Frame(
            card,
            bg=BORDER,
            height=4
        ).pack(fill="x")

        body = tk.Frame(card, bg=BODY)

        body.pack(
            fill="both",
            expand=True,
            padx=50,
            pady=(46, 42)
        )

        tk.Frame(
            body,
            bg=BODY,
            width=CARD_WIDTH,
            height=1
        ).pack()

        tk.Label(
            card,
            text=footer_text,
            font=("Arial", 9, "bold"),
            fg="#C8DCEB",
            bg=NAVY,
            pady=9
        ).pack(fill="x")

        return body

    def clear_screen(self):

        for widget in self.root.winfo_children():

            if widget is not self.bg_canvas:
                widget.destroy()

    # ##= DIFFICULTY MENU =##

    def displayMenu(self):

        body = self.screen(
            "MATH QUIZ",
            "Challenge Your Mind | Improve Your Skills",
            "MATH QUIZ | THINK • SOLVE • SUCCEED"
        )

        tk.Label(
            body,
            text="SELECT DIFFICULTY LEVEL",
            font=("Arial", 12, "bold"),
            fg=BODY_ACCENT,
            bg=BODY
        ).pack(pady=(4, 6))

        tk.Label(
            body,
            text="Choose Your Challenge",
            font=("Arial", 25, "bold"),
            fg=BODY_TEXT,
            bg=BODY
        ).pack(pady=(0, 12))

        levels = [

            (
                "ADVANCED",
                "Four Digit Numbers (1000-9999)",
                "advanced",
                "#1F4E8C",
                WHITE,
                "#2B66B3"
            ),

            (
                "EASY",
                "Single Digit Numbers (1-9)",
                "easy",
                "#CDE9FA",
                NAVY,
                "#B3DBF4"
            ),

            (
                "MODERATE",
                "Double Digit Numbers (10-99)",
                "moderate",
                "#3A8FD6",
                WHITE,
                "#5BA9E6"
            )
        ]

        for title, description, level, box_bg, box_fg, box_hover in levels:

            self.levelBox(
                body,
                title,
                description,
                level,
                box_bg,
                box_fg,
                box_hover
            )

        tk.Label(
            body,
            text="10 QUESTIONS | 100 POINTS",
            font=("Arial", 10, "bold"),
            fg=BODY_MUTED,
            bg=BODY
        ).pack(pady=(14, 4))

    def levelBox(
        self,
        parent,
        title,
        description,
        level,
        box_bg,
        box_fg,
        box_hover
    ):

        box = tk.Frame(
            parent,
            bg=BODY,
            highlightbackground=BORDER,
            highlightcolor=BORDER,
            highlightthickness=3
        )

        box.pack(pady=12)

        button = tk.Button(
            box,
            text=f"{title}\n{description}",
            command=lambda l=level: self.startQuiz(l),
            font=("Arial", 12, "bold"),
            bg=box_bg,
            fg=box_fg,
            activebackground=box_hover,
            activeforeground=box_fg,
            relief="flat",
            bd=0,
            cursor="hand2",
            width=40,
            height=2
        )

        button.pack(padx=3, pady=3)

        def on_enter(event):

            box.config(
                highlightbackground=BORDER_HOVER,
                highlightcolor=BORDER_HOVER
            )

            button.config(bg=box_hover)

        def on_leave(event):

            box.config(
                highlightbackground=BORDER,
                highlightcolor=BORDER
            )

            button.config(bg=box_bg)

        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)

    # ##= RANDOM NUMBER =##

    def randomInt(self):

        return random.randint(self.minimum, self.maximum)

    # ##= RANDOM OPERATION =##

    def decideOperation(self):

        return random.choice(["+", "-"])

    # ##= START QUIZ =##

    def startQuiz(self, level):

        if level == "easy":

            self.minimum = 1
            self.maximum = 9

        elif level == "moderate":

            self.minimum = 10
            self.maximum = 99

        else:

            self.minimum = 1000
            self.maximum = 9999

        self.difficulty = level

        self.score = 0
        self.question_number = 0

        self.quizScreen()
        self.displayProblem()

    # ##= QUIZ SCREEN =##

    def quizScreen(self):

        body = self.screen(
            "MATH QUIZ",
            f"{self.difficulty.upper()} LEVEL | ARITHMETIC CHALLENGE",
            "FIRST ATTEMPT = 10 POINTS | SECOND ATTEMPT = 5 POINTS"
        )

        # ##= BACK BUTTON ADDED =##

        tk.Button(
            body,
            text="← BACK TO MENU",
            command=self.displayMenu,
            font=("Arial", 10, "bold"),
            bg=LIGHT_BLUE,
            fg=NAVY,
            activebackground=HEADER_BLUE,
            relief="flat",
            cursor="hand2",
            padx=20,
            pady=8
        ).pack(anchor="w", pady=(0, 15))

        top = tk.Frame(body, bg=BODY)
        top.pack(fill="x")

        self.question_count = tk.Label(
            top,
            text="QUESTION 01 / 10",
            font=("Arial", 11, "bold"),
            fg=BODY_ACCENT,
            bg=BODY
        )

        self.question_count.pack(side="left")

        self.score_label = tk.Label(
            top,
            text="SCORE: 0",
            font=("Arial", 12, "bold"),
            fg=OK_GREEN,
            bg=BODY
        )

        self.score_label.pack(side="right")

        self.progress_label = tk.Label(
            body,
            text="0 of 10 completed",
            font=("Arial", 9),
            fg=BODY_MUTED,
            bg=BODY
        )

        self.progress_label.pack(anchor="w", pady=(8, 3))

        self.progress = tk.Canvas(
            body,
            width=PROGRESS_W,
            height=9,
            bg="#7C65A8",
            highlightthickness=0
        )

        self.progress.pack(pady=(0, 12))

        tk.Label(
            body,
            text="SOLVE THIS QUESTION",
            font=("Arial", 11, "bold"),
            fg=BODY_MUTED,
            bg=BODY
        ).pack(pady=(6, 4))

        self.question_label = tk.Label(
            body,
            text="",
            font=("Arial", 32, "bold"),
            fg=BODY_TEXT,
            bg=BODY
        )

        self.question_label.pack(pady=8)

        self.answer_entry = tk.Entry(
            body,
            font=("Arial", 19),
            justify="center",
            width=18,
            bd=1,
            relief="solid"
        )

        self.answer_entry.pack(ipady=8, pady=8)

        self.answer_entry.bind(
            "<Return>",
            lambda event: self.checkAnswer()
        )

        self.attempt_label = tk.Label(
            body,
            text="FIRST ATTEMPT | 10 POINTS",
            font=("Arial", 10, "bold"),
            fg=BODY_ACCENT,
            bg=BODY
        )

        self.attempt_label.pack(pady=4)

        self.submit_button = tk.Button(
            body,
            text="SUBMIT ANSWER",
            command=self.checkAnswer,
            font=("Arial", 12, "bold"),
            bg=BLUE,
            fg=WHITE,
            activebackground=DARK_BLUE,
            activeforeground=WHITE,
            relief="flat",
            cursor="hand2",
            padx=35,
            pady=12
        )

        self.submit_button.pack(pady=10)

        self.feedback = tk.Label(
            body,
            text="Enter your answer and press Submit.",
            font=("Arial", 11, "bold"),
            fg=BODY_MUTED,
            bg=BODY
        )

        self.feedback.pack(pady=(6, 4))

    # ##= DISPLAY PROBLEM =##

    def displayProblem(self):

        self.question_number += 1

        self.attempt = 1
        self.answer_locked = False

        self.num1 = self.randomInt()
        self.num2 = self.randomInt()

        self.operation = self.decideOperation()

        if self.operation == "+":

            self.correct_answer = self.num1 + self.num2

        else:

            self.correct_answer = self.num1 - self.num2

        self.question_label.config(
            text=f"{self.num1} {self.operation} {self.num2} = ?"
        )

        self.question_count.config(
            text=f"QUESTION {self.question_number:02d} / 10"
        )

        self.progress_label.config(
            text=f"{self.question_number - 1} of 10 completed"
        )

        self.progress.delete("all")

        progress_width = PROGRESS_W * (
            (self.question_number - 1) / TOTAL_QUESTIONS
        )

        self.progress.create_rectangle(
            0, 0,
            progress_width, 9,
            fill="#5DB0F0",
            outline=""
        )

        self.answer_entry.config(state="normal")
        self.answer_entry.delete(0, tk.END)
        self.answer_entry.focus_set()

        self.feedback.config(
            text="Enter your answer and press Submit.",
            fg=BODY_MUTED
        )

        self.attempt_label.config(
            text="FIRST ATTEMPT | 10 POINTS"
        )

        self.submit_button.config(
            text="SUBMIT ANSWER",
            command=self.checkAnswer,
            state="normal"
        )

    # ##= CHECK ANSWER =##

    def isCorrect(self, answer):

        return answer == self.correct_answer

    def checkAnswer(self):

        if self.answer_locked:
            return

        user_input = self.answer_entry.get().strip()

        if not user_input:

            self.feedback.config(
                text="Please enter your answer!",
                fg=BAD_RED
            )

            return

        try:

            answer = int(user_input)

        except ValueError:

            self.feedback.config(
                text="Please enter a valid whole number!",
                fg=BAD_RED
            )

            return

        if self.isCorrect(answer):

            if self.attempt == 1:

                points = 10

            else:

                points = 5

            self.score += points

            self.score_label.config(
                text=f"SCORE: {self.score}"
            )

            self.feedback.config(
                text=f"CORRECT! +{points} POINTS. WELL DONE!",
                fg=OK_GREEN
            )

            self.answer_locked = True

            self.submit_button.config(
                text="NEXT QUESTION",
                command=self.nextQuestion
            )

            self.attempt_label.config(
                text="ANSWER CORRECT!"
            )

        else:

            if self.attempt == 1:

                self.attempt = 2

                self.feedback.config(
                    text="WRONG ANSWER! TRY ONE MORE TIME.",
                    fg=BAD_RED
                )

                self.attempt_label.config(
                    text="SECOND ATTEMPT | 5 POINTS"
                )

                self.answer_entry.delete(0, tk.END)
                self.answer_entry.focus_set()

            else:

                self.feedback.config(
                    text=f"INCORRECT! ANSWER: {self.correct_answer}",
                    fg=BAD_RED
                )

                self.answer_locked = True

                self.submit_button.config(
                    text="NEXT QUESTION",
                    command=self.nextQuestion
                )

                self.attempt_label.config(
                    text="NO POINTS FOR THIS QUESTION"
                )

    # ##= NEXT QUESTION =##

    def nextQuestion(self):

        if self.question_number < TOTAL_QUESTIONS:

            self.displayProblem()

        else:

            self.displayResults()

    # ##= RESULTS =##

    def displayResults(self):

        if self.score >= 90:

            grade = "A+"
            result = "OUTSTANDING PERFORMANCE!"

        elif self.score >= 80:

            grade = "A"
            result = "EXCELLENT WORK!"

        elif self.score >= 70:

            grade = "B"
            result = "GREAT EFFORT!"

        elif self.score >= 60:

            grade = "C"
            result = "GOOD TRY!"

        elif self.score >= 50:

            grade = "D"
            result = "KEEP PRACTISING!"

        else:

            grade = "NEEDS PRACTICE"
            result = "TRY AGAIN TO IMPROVE!"

        body = self.screen(
            "QUIZ COMPLETED",
            "Your MATH QUIZ results are ready!",
            "THANK YOU FOR PLAYING MATH QUIZ!"
        )

        tk.Label(
            body,
            text="YOUR FINAL SCORE",
            font=("Arial", 12, "bold"),
            fg=BODY_MUTED,
            bg=BODY
        ).pack(pady=(6, 4))

        tk.Label(
            body,
            text=f"{self.score} / 100",
            font=("Arial", 42, "bold"),
            fg=BODY_ACCENT,
            bg=BODY
        ).pack()

        tk.Label(
            body,
            text=f"YOUR RANK: {grade}",
            font=("Arial", 20, "bold"),
            fg=BODY_TEXT,
            bg=BODY
        ).pack(pady=12)

        tk.Label(
            body,
            text=result,
            font=("Arial", 12, "bold"),
            fg=OK_GREEN,
            bg=BODY
        ).pack(pady=8)

        tk.Button(
            body,
            text="PLAY AGAIN",
            command=self.displayMenu,
            font=("Arial", 12, "bold"),
            bg=BLUE,
            fg=WHITE,
            relief="flat",
            cursor="hand2",
            padx=35,
            pady=12
        ).pack(pady=10)

        tk.Button(
            body,
            text="EXIT",
            command=self.root.destroy,
            font=("Arial", 10, "bold"),
            bg=LIGHT_BLUE,
            fg=NAVY,
            relief="flat",
            cursor="hand2",
            padx=35,
            pady=9
        ).pack(pady=(0, 4))


# ##= RUN PROGRAM =##

if __name__ == "__main__":

    root = tk.Tk()

    app = MathQuest(root)

    root.mainloop()