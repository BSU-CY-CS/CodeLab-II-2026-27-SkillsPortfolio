import os
import math
import random
import tkinter as tk
from tkinter import messagebox, filedialog

# ##= ALEXA | JOKE TELLER =##

# ##= IMAGE SETTINGS =##
BACKGROUND_IMAGE = "JOKES.IMG.JPG"

# one big picture scaled to cover the window
BACKGROUND_MODE = "tile"

IMAGE_EXTENSIONS = (".png",)

# a laughing-face icon is drawn by the program.
ICON_IMAGE = "alexa_icon.png"

# ##= JOKES FILE SETTINGS =##

# the jokes from university: one joke per line  ->  Setup?Punchline
# keep this file in the SAME folder as this program
JOKES_FILE = "randomJokes.txt"

# ##= COLOUR SETTINGS =##

RED = "#D32F2F"
DARK_RED = "#B71C1C"
DEEP_RED = "#7A0E0E"
PUNCH_RED = "#E64B4B"
CREAM = "#FFEFE2"
PEACH = "#FFDAB3"
PEACH_DARK = "#FFC4A0"
INK = "#2B2B2B"

ORANGE = "#FFB347"
ORANGE_HOVER = "#FFC474"
ORANGE_BORDER = "#FF8C00"

PURPLE = "#CE93D8"
PURPLE_HOVER = "#DDB0E5"
PURPLE_BORDER = "#8E24AA"

RED_HOVER = "#E34A4A"

PAGE_BG = "#FFE9D6"                 # same colour as the background image
GRADIENT_TOP = (255, 243, 196)      # used only if the image is missing
GRADIENT_BOTTOM = (255, 208, 204)

FONT = "Segoe UI"
CARD_W = 820

# ##=  I HAVE BUILT-IN JOKES ( USED randomJokes.txt) =##

BUILT_IN_JOKES = [
    ("Why don't scientists trust atoms?", "Because they make up everything!"),
    ("What do you call a fake noodle?", "An impasta!"),
    ("Why did the scarecrow win an award?", "Because he was outstanding in his field!"),
    ("What do you call cheese that isn't yours?", "Nacho cheese!"),
    ("Why can't you give Elsa a balloon?", "Because she will let it go!"),
    ("How does a penguin build its house?", "Igloos it together!"),
    ("Why did the math book look sad?", "Because it had too many problems!"),
    ("What do you call a bear with no teeth?", "A gummy bear!"),
    ("Why did the computer go to the doctor?", "Because it had a virus!"),
    ("What did the ocean say to the beach?", "Nothing, it just waved!"),
    ("Why was the broom late?", "It over-swept!"),
    ("What do you call a sleeping dinosaur?", "A dino-snore!"),
    ("Why did the bicycle fall over?", "Because it was two tired!"),
    ("What's orange and sounds like a parrot?", "A carrot!"),
    ("Why do bees have sticky hair?", "Because they use honeycombs!"),
    ("What did one wall say to the other wall?", "I'll meet you at the corner!"),
    ("Why did the cookie go to the hospital?", "Because it felt crummy!"),
    ("What do you call a snowman in summer?", "A puddle!"),
    ("Why can't a nose be 12 inches long?", "Because then it would be a foot!"),
    ("Why did the student eat his homework?", "Because the teacher said it was a piece of cake!"),
]


# ##= FILE HELPERS =##

def search_folders():
    """Folders where files are looked for: script folder, then current folder."""

    folders = []

    try:
        folders.append(os.path.dirname(os.path.abspath(__file__)))
    except NameError:
        pass

    folders.append(os.getcwd())

    return folders


def find_image(file_name, fallback_names):
    """Finds an image by its name, or by background-style names."""

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


def find_jokes_file():
    """Looks for randomJokes.txt in the script folder, the current folder and a
    'resources' folder. The capital letters / spaces in the name do not matter."""

    wanted = JOKES_FILE.lower().replace(" ", "").replace("_", "")

    for folder in search_folders():
        for place in (folder, os.path.join(folder, "resources")):

            exact = os.path.join(place, JOKES_FILE)
            if os.path.isfile(exact):
                return exact

            try:
                names = os.listdir(place)
            except OSError:
                continue

            for name in names:
                if name.lower().replace(" ", "").replace("_", "") == wanted:
                    return os.path.join(place, name)

    return None


def read_jokes_file(path):
    """Reads the jokes file (Setup?Punchline on every line).
    Returns a list of (setup, punchline)."""

    text = None

    # university files are sometimes saved as UTF-8 and sometimes as Windows text
    for encoding in ("utf-8-sig", "cp1252", "latin-1"):
        try:
            with open(path, "r", encoding=encoding) as file:
                text = file.read()
            break
        except UnicodeDecodeError:
            continue
        except OSError:
            return []

    if text is None:
        return []

    found = []

    for line in text.splitlines():
        line = line.strip()

        # an optional "- " at the start of a line is removed
        if line.startswith("- "):
            line = line[2:]

        if "?" not in line:
            continue

        setup, punchline = line.split("?", 1)
        setup = setup.strip()
        punchline = punchline.strip()

        if setup and punchline:
            found.append((setup + "?", punchline))

    return found


# ##= DRAWN LAUGHING FACE (HEADER + FALLBACK BACKGROUND) =##

def draw_laughing_face(c, x, y, r, face="#FFD43B", edge="#F2A900", ink="#5A3A00",
                       mouth="#8B1E2D", tongue="#FF7A8A", tears=True, tag="bg_item"):
    """Draws a laughing face (closed happy eyes, open mouth, tongue, tears)."""

    # head
    c.create_oval(x - r, y - r, x + r, y + r,
                  fill=face, outline=edge, width=2, tags=tag)

    # happy closed eyes  ^ ^
    for side in (-1, 1):
        ex = x + side * r * 0.38
        ey = y - r * 0.12
        c.create_arc(ex - r * 0.2, ey - r * 0.16, ex + r * 0.2, ey + r * 0.16,
                     start=0, extent=180, style="arc", outline=ink,
                     width=max(2, int(r / 9)), tags=tag)

    # big open mouth
    c.create_arc(x - r * 0.55, y - r * 0.05, x + r * 0.55, y + r * 0.75,
                 start=180, extent=180, style="chord", fill=mouth, outline=ink,
                 width=max(1, int(r / 14)), tags=tag)

    # tongue
    c.create_oval(x - r * 0.28, y + r * 0.4, x + r * 0.28, y + r * 0.66,
                  fill=tongue, outline="", tags=tag)

    # tears of joy
    if tears:
        for side in (-1, 1):
            tx = x + side * r * 0.8
            c.create_oval(tx - r * 0.11, y - r * 0.02, tx + r * 0.11, y + r * 0.3,
                          fill="#5BC0FF", outline="#2D9CDB", tags=tag)


def draw_gradient(c, w, h):
    """Soft vertical cream -> pink gradient (fallback only)."""

    bands = 60
    c.delete("gradient")

    for i in range(bands):
        t = i / (bands - 1)
        colour = "#%02x%02x%02x" % tuple(
            int(GRADIENT_TOP[k] + (GRADIENT_BOTTOM[k] - GRADIENT_TOP[k]) * t)
            for k in range(3)
        )
        c.create_rectangle(0, i * h / bands, w, (i + 1) * h / bands + 1,
                           fill=colour, outline="", tags="gradient")


def draw_fallback_background(c, w, h):
    """Used when the image file is missing: gradient + drawn laughing faces."""

    draw_gradient(c, w, h)

    rng = random.Random(11)     # same pattern every time the window is resized
    spacing = 108
    row = 0

    for y in range(30, h + spacing, spacing):
        offset = 0 if row % 2 == 0 else spacing // 2
        col = 0

        for x in range(30 + offset, w + spacing, spacing):
            px = x + rng.randint(-10, 10)
            py = y + rng.randint(-10, 10)

            if (row + col) % 3 == 2:
                c.create_text(px, py, text=rng.choice(["HA HA", "HAHA", "LOL"]),
                              fill="#FFFFFF", font=(FONT, rng.choice([14, 16, 18]), "bold"),
                              tags="bg_item")
            else:
                draw_laughing_face(c, px, py, rng.choice([18, 22, 26]))

            col += 1

        row += 1


# ##= DRAWN WINDOW ICON (used only if alexa_icon.png is missing) =##

def make_laugh_icon(size=64):
    """Draws a laughing-face icon using only Tkinter's PhotoImage."""

    img = tk.PhotoImage(width=size, height=size)     # unset pixels stay transparent
    c = size / 2

    def fill_circle(cx, cy, r, colour):
        for y in range(int(cy - r), int(cy + r) + 1):
            dy = y + 0.5 - cy
            if abs(dy) > r:
                continue
            half = int((r * r - dy * dy) ** 0.5)
            img.put(colour, to=(int(cx - half), y, int(cx + half) + 1, y + 1))

    def half_disc(cx, cy, r, colour):
        for y in range(int(cy), int(cy + r) + 1):
            dy = y - cy
            half = int(max(0, r * r - dy * dy) ** 0.5)
            img.put(colour, to=(int(cx - half), y, int(cx + half) + 1, y + 1))

    # head: orange edge, then yellow face
    fill_circle(c, c, size / 2 - 2, "#F2A900")
    fill_circle(c, c, size / 2 - 5, "#FFD43B")

    # happy closed eyes  ^ ^
    for side in (-1, 1):
        ex = c + side * size * 0.2
        ey = size * 0.4
        r = size * 0.1
        for deg in range(200, 341, 6):
            x = ex + r * math.cos(math.radians(deg))
            y = ey - r * math.sin(math.radians(deg))
            img.put("#5A3A00", to=(int(x), int(y), int(x) + 3, int(y) + 3))

    # big open mouth + tongue
    mouth_r = size * 0.3
    mouth_y = size * 0.52
    half_disc(c, mouth_y, mouth_r, "#8B1E2D")
    fill_circle(c, mouth_y + mouth_r * 0.62, mouth_r * 0.34, "#FF7A8A")

    # tears of joy
    for side in (-1, 1):
        fill_circle(c + side * size * 0.4, size * 0.55, size * 0.06, "#5BC0FF")

    return img


# ##= MAIN APP =##

class AlexaJokeTeller:

    def __init__(self, root):

        self.root = root
        self.root.title("ALEXA | JOKE TELLER")
        self.root.geometry("980x960")
        self.root.minsize(900, 900)
        self.root.configure(bg=PAGE_BG)

        self.loadWindowIcon()

        self.jokes, self.jokes_source = self.loadJokes()
        self.queue = []
        self.current = None
        self.punchline_shown = False
        self.resize_job = None

        self.createBackground()
        self.buildCard()
        self.buildFooter()

        self.root.bind("<Return>", lambda event: self.nextStep())
        self.root.bind("<space>", lambda event: self.nextStep())

    # ##= JOKES FILE (randomJokes.txt) =##

    def loadJokes(self):
        """Loads the jokes from randomJokes.txt. Asks for the file if it is not found."""

        path = find_jokes_file()

        if path:
            found = read_jokes_file(path)

            if found:
                return found, path

        messagebox.showwarning(
            "JOKES FILE NOT FOUND",
            f"{JOKES_FILE} was not found or has no valid jokes.\n\n"
            "Click OK and select the file manually."
        )

        chosen = filedialog.askopenfilename(
            title=f"SELECT {JOKES_FILE}",
            filetypes=[("TEXT FILES", "*.txt"), ("ALL FILES", "*.*")]
        )

        if chosen:
            found = read_jokes_file(chosen)

            if found:
                return found, chosen

        # last choice: the built-in jokes, so the program still works
        return list(BUILT_IN_JOKES), None

    # ##= WINDOW ICON (TITLE BAR) =##

    def loadWindowIcon(self):
        """Replaces the default Tk feather icon with a laughing-face icon."""

        self.icon_photo = None

        if ICON_IMAGE:
            path = find_image(ICON_IMAGE, ["alexa_icon", "icon"])

            if path:
                try:
                    self.icon_photo = tk.PhotoImage(file=path)
                except Exception as error:
                    print(f"Could not load icon image: {error}")
                    self.icon_photo = None

        # no icon file -> use the drawn laughing face
        if self.icon_photo is None:
            self.icon_photo = make_laugh_icon()

        # keep a reference (self.icon_photo) so Tk doesn't discard it
        try:
            self.root.iconphoto(True, self.icon_photo)
        except Exception as error:
            print(f"Could not set window icon: {error}")

    # ##= BACKGROUND IMAGE =##

    def createBackground(self):

        self.bg_canvas = tk.Canvas(self.root, highlightthickness=0, bg=PAGE_BG)
        self.bg_canvas.place(x=0, y=0, relwidth=1, relheight=1)

        self.bg_source = None      # original image
        self.bg_photo = None       # keeps a reference so Tk doesn't discard it

        path = find_image(BACKGROUND_IMAGE, ["laugh_background", "background", "bg"])

        if path:
            try:
                self.bg_source = tk.PhotoImage(file=path)
            except Exception as error:
                print(f"Could not load background image: {error}")
                print("Only PNG or GIF files work in this version.")
                self.bg_source = None
        else:
            print("Background image not found - using drawn laughing faces instead.")

        self.bg_canvas.bind("<Configure>", self.onResize)
        self.drawBackground()

    def onResize(self, event=None):

        # wait until the user stops resizing, so the window stays smooth
        if self.resize_job is not None:
            self.root.after_cancel(self.resize_job)

        self.resize_job = self.root.after(60, self.drawBackground)

    def drawBackground(self):

        self.resize_job = None

        w = self.bg_canvas.winfo_width()
        h = self.bg_canvas.winfo_height()

        if w < 50:
            w = 980
        if h < 50:
            h = 960

        self.bg_canvas.delete("gradient")
        self.bg_canvas.delete("bg_item")

        # no image -> drawn faces
        if self.bg_source is None:
            draw_fallback_background(self.bg_canvas, w, h)
            return

        try:
            if BACKGROUND_MODE == "stretch":
                self.drawStretched(w, h)
            else:
                self.drawTiled(w, h)

        except Exception as error:
            print(f"Could not draw background image: {error}")
            self.bg_source = None
            draw_fallback_background(self.bg_canvas, w, h)

    def drawTiled(self, w, h):
        """Repeats the image so it covers the whole window (stays sharp)."""

        self.bg_photo = self.bg_source

        tw = self.bg_photo.width()
        th = self.bg_photo.height()

        for x in range(0, w, tw):
            for y in range(0, h, th):
                self.bg_canvas.create_image(
                    x, y,
                    image=self.bg_photo,
                    anchor="nw",
                    tags="bg_item"
                )

    def drawStretched(self, w, h):
        """Scales ONE picture (whole-number zoom/shrink) to cover the window."""

        iw = self.bg_source.width()
        ih = self.bg_source.height()

        scale = max(w / iw, h / ih)

        if scale > 1:
            photo = self.bg_source.zoom(int(scale) + (0 if scale == int(scale) else 1))
        elif scale < 0.5:
            photo = self.bg_source.subsample(int(1 / scale))
        else:
            photo = self.bg_source

        self.bg_photo = photo

        self.bg_canvas.create_image(
            w // 2, h // 2,
            image=self.bg_photo,
            anchor="center",
            tags="bg_item"
        )

    # ##= CARD =##

    def buildCard(self):

        self.card = tk.Frame(
            self.root,
            bg=CREAM,
            highlightbackground=RED,
            highlightcolor=RED,
            highlightthickness=4
        )
        self.card.place(relx=0.5, rely=0.465, anchor="center")

        # ##= RED HEADER WITH DRAWN LAUGHING FACES =##
        header = tk.Frame(self.card, bg=RED)
        header.pack(fill="x")

        title_canvas = tk.Canvas(header, width=CARD_W, height=104,
                                 bg=RED, highlightthickness=0)
        title_canvas.pack(pady=(14, 0))

        for fx in (CARD_W / 2 - 205, CARD_W / 2 + 205):
            draw_laughing_face(title_canvas, fx, 52, 38, face="#FFFFFF", edge="#FFFFFF",
                               ink=RED, mouth=RED, tongue="#FF9AA2", tears=False,
                               tag="title")

        title_canvas.create_text(CARD_W / 2, 52, text="ALEXA", fill="#FFFFFF",
                                 font=(FONT, 46, "bold"))

        tk.Label(header, text="TELL ME A JOKE  😄", font=(FONT, 20, "bold"),
                 fg="#FFFFFF", bg=RED).pack(pady=(0, 2))

        tk.Label(header, text="YOUR DAILY DOSE OF LAUGHTER  ✨", font=(FONT, 12),
                 fg="#FFE3E0", bg=RED).pack(pady=(0, 16))

        # dark red line under the header
        tk.Frame(self.card, bg=DARK_RED, height=4).pack(fill="x")

        # ##= CREAM BODY =##
        body = tk.Frame(self.card, bg=CREAM)
        body.pack(fill="both", expand=True, padx=36, pady=(26, 22))

        # ##= PEACH JOKE BOX (SETUP + PUNCHLINE) =##
        joke_box = tk.Frame(body, bg=PEACH, highlightbackground=RED,
                            highlightcolor=RED, highlightthickness=4)
        joke_box.pack(fill="x")

        tk.Label(joke_box, text="🤣  THE SETUP  🤣", font=(FONT, 11, "bold"),
                 fg=DARK_RED, bg=PEACH_DARK, padx=16, pady=5).pack(pady=(18, 0))

        setup_area = tk.Frame(joke_box, bg=PEACH, height=112)
        setup_area.pack(fill="x")
        setup_area.pack_propagate(False)

        self.setup_label = tk.Label(
            setup_area,
            text="PRESS THE RED BUTTON TO HEAR A JOKE!",
            font=(FONT, 21, "bold"),
            fg=INK,
            bg=PEACH,
            wraplength=640,
            justify="center"
        )
        self.setup_label.pack(expand=True)

        punch_area = tk.Frame(joke_box, bg=PUNCH_RED, height=150)
        punch_area.pack(fill="x", padx=12, pady=(0, 12))
        punch_area.pack_propagate(False)

        tk.Label(punch_area, text="😂  THE PUNCHLINE  😂", font=(FONT, 11, "bold"),
                 fg="#FFFFFF", bg=DARK_RED, padx=16, pady=5).pack(pady=(10, 0))

        self.punch_label = tk.Label(
            punch_area,
            text="...",
            font=(FONT, 20, "bold"),
            fg="#FFFFFF",
            bg=PUNCH_RED,
            wraplength=620,
            justify="center"
        )
        self.punch_label.pack(expand=True)

        # ##= BUTTONS =##
        buttons = tk.Frame(body, bg=CREAM)
        buttons.pack(pady=(18, 0))

        self.tell_button = self.makeButton(
            buttons, "🎤  ALEXA TELL ME A JOKE", RED, "#FFFFFF",
            DEEP_RED, RED_HOVER, self.nextJoke)

        self.show_button = self.makeButton(
            buttons, "😈  SHOW PUNCHLINE", ORANGE, "#000000",
            ORANGE_BORDER, ORANGE_HOVER, self.showPunchline)

        self.next_button = self.makeButton(
            buttons, "😆  NEXT JOKE  ➜", PURPLE, "#000000",
            PURPLE_BORDER, PURPLE_HOVER, self.nextJoke)

        self.setShowEnabled(False)

        # ##= QUIT BUTTON =##
        bottom = tk.Frame(body, bg=CREAM)
        bottom.pack(fill="x", pady=(14, 0))

        self.makeButton(
            bottom, "🚪  QUIT", DARK_RED, "#FFFFFF",
            DEEP_RED, "#C62828", self.root.destroy,
            width=9, side="left")

    def makeButton(self, parent, text, bg, fg, border, hover, command,
                   width=30, side=None):
        """Button with a thick coloured border. Returns the button."""

        outer = tk.Frame(parent, bg=border, padx=3, pady=3)

        if side:
            outer.pack(side=side)
        else:
            outer.pack(pady=6)

        button = tk.Button(
            outer,
            text=text,
            command=command,
            font=(FONT, 13, "bold"),
            bg=bg,
            fg=fg,
            activebackground=hover,
            activeforeground=fg,
            disabledforeground="#8A6A4A",
            relief="flat",
            bd=0,
            cursor="hand2",
            width=width,
            pady=10
        )
        button.pack()

        button.base_bg = bg
        button.hover_bg = hover

        def on_enter(event):
            if str(button["state"]) == "normal":
                button.config(bg=button.hover_bg)

        def on_leave(event):
            if str(button["state"]) == "normal":
                button.config(bg=button.base_bg)

        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)

        return button

    def buildFooter(self):

        if self.jokes_source:
            note = f"{len(self.jokes)} JOKES LOADED FROM {os.path.basename(self.jokes_source).upper()}"
        else:
            note = f"{len(self.jokes)} BUILT-IN JOKES"

        tk.Label(
            self.root,
            text=f"ALEXA JOKE TELLER  •  {note}  •  MADE WITH PYTHON",
            font=(FONT, 9, "bold"),
            fg="#FFE3E0",
            bg=RED,
            pady=9
        ).place(relx=0, rely=1, relwidth=1, anchor="sw")

    # ##= BUTTON STATES =##

    def setShowEnabled(self, enabled):

        if enabled:
            self.show_button.config(state="normal", bg=ORANGE, cursor="hand2")
        else:
            self.show_button.config(state="disabled", bg="#F0D9B5", cursor="arrow")

    # ##= JOKE LOGIC =##

    def pickJoke(self):
        """Gives every joke once (in random order) before any repeats."""

        if not self.queue:
            self.queue = self.jokes[:]
            random.shuffle(self.queue)

            # avoid the same joke twice in a row when the list restarts
            if self.current is not None and len(self.queue) > 1 and self.queue[-1] == self.current:
                self.queue[0], self.queue[-1] = self.queue[-1], self.queue[0]

        return self.queue.pop()

    def nextJoke(self):

        self.current = self.pickJoke()
        self.punchline_shown = False

        self.setup_label.config(text=self.current[0].upper())
        self.punch_label.config(text="...")
        self.setShowEnabled(True)

    def showPunchline(self):

        if self.current is None or self.punchline_shown:
            return

        self.punch_label.config(text=self.current[1].upper())
        self.punchline_shown = True
        self.setShowEnabled(False)

    def nextStep(self):
        """Enter / Space: tell a joke, then the punchline, then the next joke."""

        if self.current is None or self.punchline_shown:
            self.nextJoke()
        else:
            self.showPunchline()


# ##= RUN PROGRAM =##

if __name__ == "__main__":

    root = tk.Tk()

    app = AlexaJokeTeller(root)

    root.mainloop()