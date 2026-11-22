import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
from pathlib import Path

# ##= STUDENT MANAGER =##

# ##= COLOUR SETTINGS =##
BLUE = "#2878B5"
DARK_BLUE = "#0E2F52"
MID_BLUE = "#0F4A80"
LIGHT_BLUE = "#EAF2F8"
ACCENT = "#4FA3E0"
WHITE = "#FFFFFF"
DARK = "#183348"
SOFT = "#F5F8FC"
GREY = "#64748B"
PEACH = "#FFD8B8"          # buttons
PEACH_HOVER = "#FFC499"    # button hover
CARD_BLUE = "#F3F9FE"       # student list card (very light blue)

FONT = "Segoe UI"

GRADE_COLOURS = {"A": "#2ECC71", "B": "#3FA9F5", "C": "#F4C542", "D": "#FF9F43", "F": "#E74C3C"}
GRADE_TINTS = {"A": "#E6F7EE", "B": "#E7F1FC", "C": "#FFF7DC", "D": "#FFEEDA", "F": "#FDE7E5"}

OVERVIEW_H = 330

# ##= WINDOW ICON SETTINGS =##
# Use a PNG 
ICON_IMAGE = "student_icon.png"


# ##= STATIC GRADIENT BACKGROUND =##

def draw_gradient(canvas, top, bottom, default_size=(1280, 900)):
    """Draw a static vertical blue gradient on a canvas."""
    w, h = canvas.winfo_width(), canvas.winfo_height()
    if w < 50 or h < 50:
        w, h = default_size

    bands = 48
    canvas.delete("gradient")
    for i in range(bands):
        t = i / (bands - 1)
        col = "#%02x%02x%02x" % tuple(
            int(top[k] + (bottom[k] - top[k]) * t) for k in range(3))
        canvas.create_rectangle(0, i * h / bands, w, (i + 1) * h / bands + 1,
                                fill=col, outline="", tags="gradient")
    canvas.tag_lower("gradient")


# ##= FILE LOCATION (SEARCHES SEVERAL PLACES) =##

BASE_DIR = Path(__file__).resolve().parent
FILE_NAME = "studentMarks.txt"

SEARCH_PATHS = [
    BASE_DIR / FILE_NAME,
    BASE_DIR / "resources" / FILE_NAME,
    Path.cwd() / FILE_NAME,
    Path.cwd() / "resources" / FILE_NAME,
]

FILE_PATH = None      # set when the file is found
students = []
skipped_lines = 0


# ##= WINDOW ICON (TITLE BAR) - GRADUATION CAP =##

ICON_PHOTO = None     


def make_student_icon(size=64):
    """Draws a graduation-cap icon using only Tkinter's PhotoImage."""

    img = tk.PhotoImage(width=size, height=size)

    # light-blue border, then dark-blue square inside it
    img.put(ACCENT, to=(0, 0, size, size))
    img.put(DARK_BLUE, to=(3, 3, size - 3, size - 3))

    # cap base (under the flat top)
    img.put("#9CD0FF", to=(19, 30, 45, 46))
    img.put("#9CD0FF", to=(22, 46, 42, 49))

    # flat diamond top (mortarboard), drawn line by line
    cx, cy, half_w, half_h = 32, 26, 25, 13
    for y in range(cy - half_h, cy + half_h + 1):
        dy = abs(y - cy)
        half = int(half_w * (1 - dy / half_h))
        img.put(WHITE, to=(cx - half, y, cx + half + 1, y + 1))

    # button in the middle of the cap top
    img.put(BLUE, to=(30, 24, 35, 29))

    # tassel hanging from the right corner
    img.put(PEACH, to=(53, 26, 55, 44))
    img.put(PEACH, to=(51, 44, 57, 51))

    return img


def load_window_icon():
    """Replaces the default Tk feather icon with a student/graduation icon."""

    global ICON_PHOTO
    ICON_PHOTO = None

    # 1) the user's own icon file (PNG)
    if ICON_IMAGE:
        for folder in (BASE_DIR, Path.cwd()):
            candidate = folder / ICON_IMAGE

            if candidate.is_file():
                try:
                    ICON_PHOTO = tk.PhotoImage(file=str(candidate))
                    break
                except tk.TclError as error:
                    print(f"Could not load icon image: {error}")
                    ICON_PHOTO = None

    # 2)  built-in graduation-cap icon
    if ICON_PHOTO is None:
        ICON_PHOTO = make_student_icon()

    try:
        root.iconphoto(True, ICON_PHOTO)
    except tk.TclError as error:
        print(f"Could not set window icon: {error}")


# ##= READ ONE FILE =##

def read_file(path):
    """Read students from a file. Returns (list_of_students, skipped_count)."""
    found = []
    skipped = 0

    with open(path, "r", encoding="utf-8-sig") as file:
        lines = [ln.strip() for ln in file if ln.strip()]

    for line in lines:
        parts = [p.strip() for p in line.split(",")]

        # first line is just the number of students 
        if len(parts) == 1 and parts[0].isdigit():
            continue

        if len(parts) != 6:
            skipped += 1
            continue

        try:
            code = parts[0]
            name = parts[1]

            if not code.isdigit() or not 1000 <= int(code) <= 9999:
                skipped += 1
                continue

            if not name:
                skipped += 1
                continue

            mark1 = int(float(parts[2]))
            mark2 = int(float(parts[3]))
            mark3 = int(float(parts[4]))
            exam = int(float(parts[5]))

            if not all(0 <= m <= 20 for m in (mark1, mark2, mark3)):
                skipped += 1
                continue

            if not 0 <= exam <= 100:
                skipped += 1
                continue

            found.append({
                "code": code,
                "name": name,
                "mark1": mark1,
                "mark2": mark2,
                "mark3": mark3,
                "exam": exam
            })

        except ValueError:
            skipped += 1

    return found, skipped


# ##= LOAD STUDENT RECORDS =##

def load_students():
    global students, FILE_PATH, skipped_lines
    students = []
    skipped_lines = 0

    # 1)  using the first one that has students
    for path in SEARCH_PATHS:
        if path.exists():
            data, skipped = read_file(path)
            if data:
                students = data
                skipped_lines = skipped
                FILE_PATH = path
                return True

    # 2)  the user choose the file
    messagebox.showwarning(
        "File Not Found",
        "studentMarks.txt was not found or has no valid records.\n\n"
        "Click OK and select the file manually."
    )

    chosen = filedialog.askopenfilename(
        title="Select studentMarks.txt",
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
    )

    if chosen:
        path = Path(chosen)
        data, skipped = read_file(path)
        FILE_PATH = path
        students = data
        skipped_lines = skipped
        return bool(data)

    # 3) nothing chosen: new file is created only when the first student is saved
    FILE_PATH = BASE_DIR / FILE_NAME
    return False


# ##= SAVE STUDENT RECORDS =##

def save_students():
    global FILE_PATH

    if FILE_PATH is None:
        FILE_PATH = BASE_DIR / FILE_NAME

    FILE_PATH.parent.mkdir(parents=True, exist_ok=True)

    with open(FILE_PATH, "w", encoding="utf-8") as file:
        file.write(str(len(students)) + "\n")

        for s in students:
            file.write(
                f"{s['code']},{s['name']},"
                f"{s['mark1']},{s['mark2']},"
                f"{s['mark3']},{s['exam']}\n"
            )


# ##= CALCULATE STUDENT RESULTS =##

def coursework(s):
    return s["mark1"] + s["mark2"] + s["mark3"]


def total_score(s):
    return coursework(s) + s["exam"]


def percentage(s):
    return (total_score(s) / 160) * 100


def grade_from_percent(p):
    if p >= 70:
        return "A"
    elif p >= 60:
        return "B"
    elif p >= 50:
        return "C"
    elif p >= 40:
        return "D"
    else:
        return "F"


def grade(s):
    return grade_from_percent(percentage(s))


# ##= SEARCH STUDENT =##

def find_student(search):
    search = search.strip().lower()

    for s in students:
        if s["code"].lower() == search or s["name"].lower() == search:
            return s

    return None


# ##= OVERVIEW DASHBOARD  =##

def short(text, limit):
    return text if len(text) <= limit else text[:limit - 1] + "…"


def draw_overview():
    c = overview
    c.delete("chart")

    w, h = c.winfo_width(), c.winfo_height()
    if w < 200 or h < 100:
        w, h = 900, OVERVIEW_H

    draw_gradient(c, (10, 42, 80), (22, 92, 152), default_size=(900, OVERVIEW_H))

    count = len(students)
    pcts = [percentage(s) for s in students]
    avg = sum(pcts) / count if count else 0
    top = max(students, key=total_score) if count else None
    low = min(students, key=total_score) if count else None
    passed = sum(1 for s in students if grade(s) != "F")
    pass_rate = passed / count * 100 if count else 0

    counts = {g: 0 for g in "ABCDF"}
    for s in students:
        counts[grade(s)] += 1

    # ##= TITLE STRIP =##
    c.create_text(20, 18, text="CLASS OVERVIEW", anchor="w", fill=WHITE,
                  font=(FONT, 12, "bold"), tags="chart")
    c.create_text(w - 20, 18, anchor="e", fill="#9CD0FF", font=(FONT, 9),
                  text="GRADES:  A 70+   B 60+   C 50+   D 40+   F BELOW 40", tags="chart")

    # ##= SUMMARY CARDS =##
    cards = [
        ("TOTAL STUDENTS", str(count), "records loaded", "#5DB0F0"),
        ("CLASS AVERAGE", f"{avg:.1f}%", f"grade {grade_from_percent(avg)}" if count else "no data", "#2ECC71"),
        ("HIGHEST SCORE", f"{percentage(top):.1f}%" if top else "-", short(top["name"], 18) if top else "no data", "#F4C542"),
        ("LOWEST SCORE", f"{percentage(low):.1f}%" if low else "-", short(low["name"], 18) if low else "no data", "#FF9F43"),
        ("PASS RATE", f"{pass_rate:.0f}%", f"{passed} of {count} passed", "#B388FF"),
    ]

    gap = 12
    margin = 20
    card_w = (w - 2 * margin - 4 * gap) / 5
    cy0, cy1 = 36, 108

    for i, (label, value, sub, colour) in enumerate(cards):
        x0 = margin + i * (card_w + gap)
        c.create_rectangle(x0, cy0, x0 + card_w, cy1, fill="#176BAD",
                           outline="#5DB0F0", width=1, tags="chart")
        c.create_rectangle(x0, cy0, x0 + 6, cy1, fill=colour, outline="", tags="chart")
        c.create_text(x0 + 18, cy0 + 15, text=label, anchor="w", fill="#BFE0FF",
                      font=(FONT, 8, "bold"), tags="chart")
        c.create_text(x0 + 18, cy0 + 39, text=value, anchor="w", fill=WHITE,
                      font=(FONT, 18, "bold"), tags="chart")
        c.create_text(x0 + 18, cy0 + 60, text=sub, anchor="w", fill="#DCEBFA",
                      font=(FONT, 8), tags="chart")

    # ##= CHART PANELS =##
    y0, y1 = 122, h - 14
    ph = y1 - y0
    total_w = w - 2 * margin - gap
    lw = int(total_w * 0.40)
    rw = total_w - lw
    lx0 = margin
    rx0 = margin + lw + gap

    for px, pw in ((lx0, lw), (rx0, rw)):
        c.create_rectangle(px, y0, px + pw, y1, fill="", outline="#4F9AD6",
                           width=1, tags="chart")

    # ##= PIE (DONUT) CHART: GRADE DISTRIBUTION =##
    c.create_text(lx0 + 16, y0 + 17, text="GRADE DISTRIBUTION", anchor="w",
                  fill=WHITE, font=(FONT, 10, "bold"), tags="chart")

    r = max(30, min((ph - 58) / 2, lw * 0.22))
    cx = lx0 + 20 + r
    cy = y0 + 34 + (ph - 34) / 2

    if count == 0:
        c.create_oval(cx - r, cy - r, cx + r, cy + r, outline="#5DB0F0",
                      width=2, tags="chart")
        c.create_text(cx, cy, text="NO DATA", fill="#BFE0FF",
                      font=(FONT, 9, "bold"), tags="chart")
    else:
        start = 90
        for g in "ABCDF":
            n = counts[g]
            if n == 0:
                continue
            if n == count:
                c.create_oval(cx - r, cy - r, cx + r, cy + r, fill=GRADE_COLOURS[g],
                              outline="#0F3557", width=2, tags="chart")
            else:
                extent = -360 * n / count
                c.create_arc(cx - r, cy - r, cx + r, cy + r, start=start, extent=extent,
                             style="pieslice", fill=GRADE_COLOURS[g],
                             outline="#0F3557", width=2, tags="chart")
                start += extent

        hole = r * 0.58
        c.create_oval(cx - hole, cy - hole, cx + hole, cy + hole, fill="#12406B",
                      outline="#0F3557", width=2, tags="chart")
        c.create_text(cx, cy - 7, text=f"{avg:.0f}%", fill=WHITE,
                      font=(FONT, 15, "bold"), tags="chart")
        c.create_text(cx, cy + 12, text="AVERAGE", fill="#9CD0FF",
                      font=(FONT, 7, "bold"), tags="chart")

    # legend
    lgx = cx + r + 28
    lgy = cy - 2.5 * 22 + 11
    for i, g in enumerate("ABCDF"):
        y = lgy + i * 22
        n = counts[g]
        c.create_rectangle(lgx, y - 6, lgx + 12, y + 6, fill=GRADE_COLOURS[g],
                           outline="", tags="chart")
        c.create_text(lgx + 20, y, text=f"GRADE {g}", anchor="w", fill=WHITE,
                      font=(FONT, 9, "bold"), tags="chart")
        share = n / count * 100 if count else 0
        c.create_text(lx0 + lw - 16, y, text=f"{n}  ({share:.0f}%)", anchor="e",
                      fill="#BFE0FF", font=(FONT, 9), tags="chart")

    # ##= LINE CHART: CLASS PERCENTAGE OF UP TO 10 STUDENTS =##
    shown = students[:10]
    n = len(shown)
    title = (f"CLASS PERCENTAGE  •  FIRST {n} STUDENTS" if count > 10
             else f"CLASS PERCENTAGE  •  {n} STUDENTS")
    c.create_text(rx0 + 16, y0 + 17, text=title, anchor="w", fill=WHITE,
                  font=(FONT, 10, "bold"), tags="chart")

    px0, px1 = rx0 + 56, rx0 + rw - 26
    py0, py1 = y0 + 56, y1 - 40

    def ypos(v):
        return py1 - v / 100 * (py1 - py0)

    for v in (0, 20, 40, 60, 80, 100):
        if v == 0:
            c.create_line(px0, ypos(v), px1, ypos(v), fill="#6FB0E6", tags="chart")
        else:
            c.create_line(px0, ypos(v), px1, ypos(v), fill="#3F7FB8",
                          dash=(2, 4), tags="chart")
        c.create_text(px0 - 10, ypos(v), text=f"{v}%", anchor="e", fill="#9CD0FF",
                      font=(FONT, 8), tags="chart")

    if n == 0:
        c.create_text((px0 + px1) / 2, (py0 + py1) / 2, text="NO DATA",
                      fill="#BFE0FF", font=(FONT, 10, "bold"), tags="chart")
    else:
        if n == 1:
            xs = [(px0 + px1) / 2]
        else:
            step = (px1 - px0 - 30) / (n - 1)
            xs = [px0 + 15 + i * step for i in range(n)]
        vals = [percentage(s) for s in shown]
        ys = [ypos(v) for v in vals]

        # class average line
        mean = sum(vals) / n
        c.create_line(px0, ypos(mean), px1, ypos(mean), fill="#FFD166",
                      dash=(6, 3), width=1, tags="chart")
        c.create_text(px1, ypos(mean) - 9, text=f"AVG {mean:.0f}%", anchor="e",
                      fill="#FFD166", font=(FONT, 8, "bold"), tags="chart")

        if n >= 2:
            flat = [v for pt in zip(xs, ys) for v in pt]
            c.create_line(*flat, smooth=True, width=9, fill="#2B7DBF", tags="chart")
            c.create_line(*flat, smooth=True, width=3, fill="#7FD6FF", tags="chart")

        for x, y, v, s in zip(xs, ys, vals, shown):
            c.create_oval(x - 6, y - 6, x + 6, y + 6, fill=GRADE_COLOURS[grade(s)],
                          outline=WHITE, width=2, tags="chart")
            c.create_text(x, y - 17, text=f"{v:.0f}%", fill=WHITE,
                          font=(FONT, 8, "bold"), tags="chart")
            c.create_text(x, py1 + 18, text=short(s["name"].split()[0], 8),
                          fill="#BFE0FF", font=(FONT, 8), tags="chart")


# ##= TABLE DISPLAY FUNCTIONS =##

def clear_table():
    for item in tree.get_children():
        tree.delete(item)


def display_student(s):
    tree.insert(
        "",
        "end",
        values=(
            s["code"],
            s["name"],
            f"{coursework(s)} / 60",
            f"{s['exam']} / 100",
            f"{total_score(s)} / 160",
            f"{percentage(s):.2f}%",
            grade(s)
        ),
        tags=(grade(s),)
    )


def show_summary():
    count = len(students)

    if count == 0:
        average = 0
    else:
        average = sum(percentage(s) for s in students) / count

    summary_label.config(
        text=f"TOTAL STUDENTS: {count}     |     "
             f"CLASS AVERAGE: {average:.2f}%"
    )

    draw_overview()


# ##= 1. VIEW ALL STUDENT RECORDS =##

def show_all():
    clear_table()

    for s in students:
        display_student(s)

    show_summary()
    status_label.config(text="Showing all student records")


# ##= 2. VIEW INDIVIDUAL STUDENT =##

def show_individual():
    search = simpledialog.askstring(
        "Individual Student",
        "Enter student name or student number:",
        parent=root
    )

    if not search:
        return

    s = find_student(search)
    clear_table()

    if s:
        display_student(s)
        status_label.config(text=f"Student record: {s['name']}")
    else:
        messagebox.showerror("Not Found", "Student record not found!")
        status_label.config(text="No matching student found")

    show_summary()


# ##= 3. HIGHEST OVERALL SCORE =##

def show_highest():
    if not students:
        messagebox.showwarning("No Records", "No students available.")
        return

    s = max(students, key=total_score)

    clear_table()
    display_student(s)
    show_summary()
    status_label.config(text=f"Highest scoring student: {s['name']}")


# ##= 4. LOWEST OVERALL SCORE =##

def show_lowest():
    if not students:
        messagebox.showwarning("No Records", "No students available.")
        return

    s = min(students, key=total_score)

    clear_table()
    display_student(s)
    show_summary()
    status_label.config(text=f"Lowest scoring student: {s['name']}")


# ##= 5. SORT STUDENT RECORDS =##

def sort_students(reverse=False):
    if not students:
        messagebox.showwarning("No Records", "No students available.")
        return

    students.sort(key=lambda s: percentage(s), reverse=reverse)
    show_all()

    if reverse:
        status_label.config(text="Sorted: Highest to Lowest")
    else:
        status_label.config(text="Sorted: Lowest to Highest")


# ##= VALIDATE STUDENT INFORMATION =##

def validate_student(code, name, mark1, mark2, mark3, exam, old=None):
    code = code.strip()
    name = name.strip()

    if not code.isdigit() or not 1000 <= int(code) <= 9999:
        raise ValueError("Student number must be between 1000 and 9999.")

    if not name or "," in name:
        raise ValueError("Please enter a valid student name.")

    if any(s["code"] == code and s is not old for s in students):
        raise ValueError("This student number already exists.")

    marks = [int(mark1), int(mark2), int(mark3)]
    exam = int(exam)

    if any(m < 0 or m > 20 for m in marks):
        raise ValueError("Coursework marks must be between 0 and 20.")

    if not 0 <= exam <= 100:
        raise ValueError("Exam mark must be between 0 and 100.")

    return {
        "code": code,
        "name": name,
        "mark1": marks[0],
        "mark2": marks[1],
        "mark3": marks[2],
        "exam": exam
    }


# ##= ADD / UPDATE STUDENT FORM =##

def student_form(title, old=None):
    window = tk.Toplevel(root)
    window.title(title)
    window.geometry("440x560")
    window.configure(bg=LIGHT_BLUE)
    window.resizable(False, False)
    window.transient(root)
    window.grab_set()

    tk.Label(
        window,
        text=title.upper(),
        font=(FONT, 18, "bold"),
        bg=LIGHT_BLUE,
        fg=DARK_BLUE
    ).pack(pady=20)

    fields = [
        ("Student Number", "code"),
        ("Student Name", "name"),
        ("Coursework Mark 1 (0-20)", "mark1"),
        ("Coursework Mark 2 (0-20)", "mark2"),
        ("Coursework Mark 3 (0-20)", "mark3"),
        ("Exam Mark (0-100)", "exam")
    ]

    entries = {}

    for label_text, key in fields:
        tk.Label(
            window,
            text=label_text,
            font=(FONT, 10, "bold"),
            bg=LIGHT_BLUE,
            fg=DARK_BLUE
        ).pack(anchor="w", padx=45, pady=(5, 0))

        entry = tk.Entry(
            window,
            font=(FONT, 12),
            width=34,
            bg=WHITE,
            fg=DARK,
            relief="flat",
            bd=6
        )

        if old:
            entry.insert(0, str(old[key]))

        entry.pack(pady=5)
        entries[key] = entry

    def submit():
        try:
            record = validate_student(
                entries["code"].get(),
                entries["name"].get(),
                entries["mark1"].get(),
                entries["mark2"].get(),
                entries["mark3"].get(),
                entries["exam"].get(),
                old
            )

            if old:
                old.update(record)
                success_text = "Student record updated successfully!"
            else:
                students.append(record)
                success_text = "Student added successfully!"

            save_students()
            show_all()

            messagebox.showinfo("Success", success_text)
            window.destroy()

        except ValueError as error:
            messagebox.showerror("Invalid Information", str(error))

    tk.Button(
        window,
        text="SAVE RECORD",
        command=submit,
        font=(FONT, 12, "bold"),
        bg=BLUE,
        fg=WHITE,
        activebackground=DARK_BLUE,
        activeforeground=WHITE,
        relief="flat",
        cursor="hand2"
    ).pack(pady=22, ipadx=35, ipady=10)


# ##= 6. ADD STUDENT RECORD =##

def add_student():
    student_form("Add Student Record")


# ##= 7. DELETE STUDENT RECORD =##

def delete_student():
    search = simpledialog.askstring(
        "Delete Student",
        "Enter student name or student number:",
        parent=root
    )

    if not search:
        return

    s = find_student(search)

    if not s:
        messagebox.showerror("Not Found", "Student record not found!")
        return

    confirm = messagebox.askyesno(
        "Confirm Delete",
        f"Are you sure you want to delete {s['name']}?"
    )

    if confirm:
        students.remove(s)
        save_students()
        show_all()
        messagebox.showinfo("Deleted", "Student record deleted successfully!")


# ##= 8. UPDATE STUDENT RECORD =##

def update_student():
    search = simpledialog.askstring(
        "Update Student",
        "Enter student name or student number:",
        parent=root
    )

    if not search:
        return

    s = find_student(search)

    if not s:
        messagebox.showerror("Not Found", "Student record not found!")
        return

    student_form("Update Student Record", s)


# ##= MAIN WINDOW + STATIC BLUE BACKGROUND =##

root = tk.Tk()
root.title("Student Manager - Academic System")
root.geometry("1280x900")
root.minsize(1100, 780)
root.configure(bg="#0A2A4D")

# replace the default Tk feather with the student icon
load_window_icon()

bg_canvas = tk.Canvas(root, highlightthickness=0, bg="#0A2A4D")
bg_canvas.place(x=0, y=0, relwidth=1, relheight=1)
bg_canvas.bind("<Configure>",
               lambda e: draw_gradient(bg_canvas, (8, 38, 74), (38, 120, 190)))
draw_gradient(bg_canvas, (8, 38, 74), (38, 120, 190))


# ##= HEADER =##

header = tk.Frame(root, bg=DARK_BLUE, height=102,
                  highlightbackground=ACCENT, highlightthickness=2)
header.pack(fill="x", padx=26, pady=(18, 10))
header.pack_propagate(False)

tk.Label(header, text="STUDENT MANAGER", font=(FONT, 27, "bold"),
         bg=DARK_BLUE, fg=WHITE).pack(pady=(10, 0))

tk.Label(header, text="Academic Records Management System", font=(FONT, 11),
         bg=DARK_BLUE, fg="#DCEBFA").pack()


# ##= EXIT BUTTON (PACKED FIRST SO IT STAYS VISIBLE) =##

quit_button = tk.Button(
    root,
    text="EXIT APPLICATION",
    command=root.destroy,
    font=(FONT, 10, "bold"),
    bg=DARK_BLUE,
    fg=WHITE,
    activebackground=BLUE,
    activeforeground=WHITE,
    relief="flat",
    cursor="hand2",
    highlightbackground=ACCENT,
    highlightthickness=1
)

quit_button.pack(side="bottom", pady=(8, 16), ipadx=22, ipady=7)
quit_button.bind("<Enter>", lambda e: quit_button.config(bg=BLUE))
quit_button.bind("<Leave>", lambda e: quit_button.config(bg=DARK_BLUE))


# ##= LEFT NAVIGATION SIDEBAR =##

sidebar = tk.Frame(root, bg=MID_BLUE, width=250, padx=14, pady=14,
                   highlightbackground=ACCENT, highlightthickness=1)
sidebar.pack(side="left", fill="y", padx=(26, 12), pady=(0, 0))
sidebar.pack_propagate(False)

tk.Label(
    sidebar,
    text="NAVIGATION",
    font=(FONT, 14, "bold"),
    bg=MID_BLUE,
    fg=WHITE
).pack(pady=(4, 12))


def menu_button(text, command):
    button = tk.Button(
        sidebar,
        text=text,
        command=command,
        font=(FONT, 10, "bold"),
        bg=PEACH,
        fg=DARK_BLUE,
        activebackground=PEACH_HOVER,
        activeforeground=DARK_BLUE,
        relief="flat",
        cursor="hand2",
        anchor="w",
        padx=14
    )

    button.pack(fill="x", pady=4, ipady=6)
    button.bind("<Enter>", lambda event: button.config(bg=PEACH_HOVER))
    button.bind("<Leave>", lambda event: button.config(bg=PEACH))


def section_label(text):
    tk.Label(
        sidebar,
        text=text,
        font=(FONT, 11, "bold"),
        bg=MID_BLUE,
        fg="#BFE0FF"
    ).pack(pady=(16, 6))


# ##= VIEW RECORDS =##
menu_button("📋  All Student Records", show_all)
menu_button("🔍  Individual Student Record", show_individual)
menu_button("🏆  Highest Total Score", show_highest)
menu_button("📉  Lowest Total Score", show_lowest)

# ##= SORT RECORDS =##
section_label("SORT RECORDS")
menu_button("⬆  Ascending Order", lambda: sort_students(False))
menu_button("⬇  Descending Order", lambda: sort_students(True))

# ##= MANAGE STUDENTS =##
section_label("MANAGE STUDENTS")
menu_button("➕  Add Student Record", add_student)
menu_button("🗑  Delete Student Record", delete_student)
menu_button("✏  Update Student Record", update_student)


# ##= RIGHT SIDE: OVERVIEW (TOP) + STUDENT LIST (BOTTOM) =##

right = tk.Frame(root, bg="#0C2D4F", padx=10, pady=10,
                 highlightbackground=ACCENT, highlightthickness=1)
right.pack(side="left", fill="both", expand=True, padx=(0, 26))

# ##= OVERVIEW DASHBOARD (STATIC) =##
overview = tk.Canvas(right, height=OVERVIEW_H, highlightthickness=0, bg="#0B2A4A")
overview.pack(fill="x")
overview.bind("<Configure>", lambda e: draw_overview())

# ##= STUDENT LIST CARD =##
table_card = tk.Frame(right, bg=CARD_BLUE)
table_card.pack(fill="both", expand=True, pady=(10, 0))

table_card.grid_columnconfigure(0, weight=1)
table_card.grid_rowconfigure(1, weight=1)

title_bar = tk.Frame(table_card, bg=CARD_BLUE)
title_bar.grid(row=0, column=0, sticky="ew", padx=16, pady=(12, 8))

tk.Frame(title_bar, bg=BLUE, width=6, height=26).pack(side="left", padx=(0, 10))
tk.Label(
    title_bar,
    text="STUDENT LIST",
    font=(FONT, 15, "bold"),
    bg=CARD_BLUE,
    fg=DARK_BLUE
).pack(side="left")

status_label = tk.Label(
    title_bar,
    text="Welcome to Student Manager",
    font=(FONT, 9),
    bg=CARD_BLUE,
    fg=GREY
)
status_label.pack(side="right")


# ##= TABLE DESIGN =##

style = ttk.Style()
style.theme_use("clam")

style.configure(
    "Treeview",
    background=CARD_BLUE,
    foreground=DARK,
    rowheight=34,
    fieldbackground=CARD_BLUE,
    borderwidth=0,
    font=(FONT, 10)
)

style.configure(
    "Treeview.Heading",
    background=DARK_BLUE,
    foreground=WHITE,
    font=(FONT, 10, "bold"),
    padding=10,
    relief="flat"
)

style.map(
    "Treeview",
    background=[("selected", BLUE)],
    foreground=[("selected", WHITE)]
)

style.map(
    "Treeview.Heading",
    background=[("active", BLUE)]
)

columns = ("code", "name", "coursework", "exam", "total", "percentage", "grade")

table_frame = tk.Frame(table_card, bg=CARD_BLUE)
table_frame.grid(row=1, column=0, sticky="nsew", padx=16)

table_frame.grid_columnconfigure(0, weight=1)
table_frame.grid_rowconfigure(0, weight=1)

tree = ttk.Treeview(table_frame, columns=columns, show="headings")

tree.heading("code", text="STUDENT NO.")
tree.heading("name", text="STUDENT NAME")
tree.heading("coursework", text="COURSEWORK")
tree.heading("exam", text="EXAM")
tree.heading("total", text="TOTAL")
tree.heading("percentage", text="PERCENTAGE")
tree.heading("grade", text="GRADE")

tree.column("code", width=100, minwidth=80, anchor="center")
tree.column("name", width=200, minwidth=130, anchor="w")
tree.column("coursework", width=110, minwidth=90, anchor="center")
tree.column("exam", width=90, minwidth=70, anchor="center")
tree.column("total", width=100, minwidth=80, anchor="center")
tree.column("percentage", width=110, minwidth=90, anchor="center")
tree.column("grade", width=70, minwidth=55, anchor="center")

# soft row colour for each grade
for g, tint in GRADE_TINTS.items():
    tree.tag_configure(g, background=tint)

scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
tree.configure(yscrollcommand=scrollbar.set)

tree.grid(row=0, column=0, sticky="nsew")
scrollbar.grid(row=0, column=1, sticky="ns")


# ##= SUMMARY SECTION =##

summary_label = tk.Label(
    table_card,
    text="TOTAL STUDENTS: 0 | CLASS AVERAGE: 0.00%",
    font=(FONT, 11, "bold"),
    bg=LIGHT_BLUE,
    fg=DARK_BLUE,
    pady=10
)

summary_label.grid(row=2, column=0, sticky="ew", padx=16, pady=(10, 14))


# ##= START APPLICATION =##

loaded = load_students()
show_all()

if loaded:
    msg = f"Loaded {len(students)} students from: {FILE_PATH.name}"
    if skipped_lines:
        msg += f"   ({skipped_lines} invalid lines skipped)"
    status_label.config(text=msg)

root.mainloop()