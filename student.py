from tkinter import *
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import mysql.connector
import cv2
import re
import os
import calendar
import datetime


# ================================================================
#                   CALENDAR POPUP WIDGET
# ================================================================
class CalendarPicker(Toplevel):
    """Full tabular calendar popup — returns DD/MM/YYYY into a StringVar."""

    def __init__(self, parent, date_var):
        super().__init__(parent)
        self.date_var = date_var
        self.title("Select Date of Birth")
        self.resizable(False, False)
        self.grab_set()
        self.configure(bg="#f0f4f8")

        self.geometry(f"+{parent.winfo_rootx()+200}+{parent.winfo_rooty()+150}")

        today = datetime.date.today()
        try:
            parts = date_var.get().split("/")
            self.current_year  = int(parts[2])
            self.current_month = int(parts[1])
            self.selected_day  = int(parts[0])
        except Exception:
            self.current_year  = today.year - 18
            self.current_month = today.month
            self.selected_day  = None

        self.max_year = today.year - 5
        self.min_year = today.year - 80

        self._build_header()
        self._build_calendar()

    def _build_header(self):
        hdr = Frame(self, bg="#1a237e", pady=6)
        hdr.pack(fill=X)

        Button(hdr, text="◀", bg="#1a237e", fg="white", bd=0,
               font=("Arial", 14, "bold"), cursor="hand2",
               command=self._prev_month).pack(side=LEFT, padx=10)

        self.month_var = StringVar()
        self.year_var  = StringVar()

        months = [calendar.month_name[m] for m in range(1, 13)]
        self.month_combo = ttk.Combobox(hdr, textvariable=self.month_var,
                                        values=months, state="readonly",
                                        width=11, font=("Arial", 11, "bold"))
        self.month_combo.set(calendar.month_name[self.current_month])
        self.month_combo.pack(side=LEFT, padx=4)
        self.month_combo.bind("<<ComboboxSelected>>", self._on_month_change)

        years = [str(y) for y in range(self.max_year, self.min_year - 1, -1)]
        self.year_combo = ttk.Combobox(hdr, textvariable=self.year_var,
                                       values=years, state="readonly",
                                       width=7, font=("Arial", 11, "bold"))
        self.year_combo.set(str(self.current_year))
        self.year_combo.pack(side=LEFT, padx=4)
        self.year_combo.bind("<<ComboboxSelected>>", self._on_year_change)

        Button(hdr, text="▶", bg="#1a237e", fg="white", bd=0,
               font=("Arial", 14, "bold"), cursor="hand2",
               command=self._next_month).pack(side=LEFT, padx=10)

    def _build_calendar(self):
        if hasattr(self, "cal_frame"):
            self.cal_frame.destroy()
        if hasattr(self, "foot_frame"):
            self.foot_frame.destroy()

        self.cal_frame = Frame(self, bg="#f0f4f8", padx=10, pady=6)
        self.cal_frame.pack()

        for i, day in enumerate(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]):
            fg = "#c62828" if day == "Sun" else "#1a237e"
            Label(self.cal_frame, text=day, width=4,
                  font=("Arial", 9, "bold"), bg="#e8eaf6", fg=fg,
                  relief=FLAT).grid(row=0, column=i, padx=1, pady=1)

        cal = calendar.monthcalendar(self.current_year, self.current_month)
        for r, week in enumerate(cal, start=1):
            for c, day in enumerate(week):
                if day == 0:
                    Label(self.cal_frame, text="", width=4,
                          bg="#f0f4f8").grid(row=r, column=c, padx=1, pady=1)
                else:
                    is_selected = (day == self.selected_day)
                    btn_bg = "#1a237e" if is_selected else "white"
                    btn_fg = "white" if is_selected else ("#c62828" if c == 6 else "#212121")
                    b = Button(self.cal_frame, text=str(day), width=4,
                               font=("Arial", 10), bg=btn_bg, fg=btn_fg,
                               relief=FLAT, cursor="hand2",
                               command=lambda d=day: self._select_day(d))
                    b.grid(row=r, column=c, padx=1, pady=1)

        self.foot_frame = Frame(self, bg="#f0f4f8", pady=6)
        self.foot_frame.pack()
        Button(self.foot_frame, text="OK", width=8, bg="#1a237e", fg="white",
               font=("Arial", 10, "bold"), cursor="hand2",
               command=self._confirm).pack(side=LEFT, padx=8)
        Button(self.foot_frame, text="Cancel", width=8, bg="#757575", fg="white",
               font=("Arial", 10, "bold"), cursor="hand2",
               command=self.destroy).pack(side=LEFT, padx=8)

    def _select_day(self, day):
        self.selected_day = day
        self._build_calendar()

    def _confirm(self):
        if self.selected_day is None:
            messagebox.showerror("Error", "Please select a day.", parent=self)
            return
        self.date_var.set(
            f"{self.selected_day:02d}/{self.current_month:02d}/{self.current_year}"
        )
        self.destroy()

    def _prev_month(self):
        self.current_month -= 1
        if self.current_month < 1:
            self.current_month = 12
            self.current_year -= 1
        # FIX: clamp year to allowed range when navigating
        if self.current_year < self.min_year:
            self.current_year = self.min_year
            self.current_month = 1
        self._sync_combos()
        self._build_calendar()

    def _next_month(self):
        self.current_month += 1
        if self.current_month > 12:
            self.current_month = 1
            self.current_year += 1
        # FIX: clamp year to allowed range when navigating
        if self.current_year > self.max_year:
            self.current_year = self.max_year
            self.current_month = 12
        self._sync_combos()
        self._build_calendar()

    def _on_month_change(self, _=None):
        self.current_month = list(calendar.month_name).index(self.month_var.get())
        self._build_calendar()

    def _on_year_change(self, _=None):
        self.current_year = int(self.year_var.get())
        self._sync_combos()
        self._build_calendar()

    def _sync_combos(self):
        self.month_combo.set(calendar.month_name[self.current_month])
        self.year_combo.set(str(self.current_year))


# ================================================================
#                     VALIDATION HELPERS
# ================================================================
def validate_gmail(email: str) -> bool:
    pattern = r'^[a-zA-Z0-9][a-zA-Z0-9._%+\-]*@gmail\.com$'
    return bool(re.match(pattern, email))

def validate_phone(phone: str) -> bool:
    return bool(re.fullmatch(r'[6-9]\d{9}', phone))

def validate_dob(dob: str) -> bool:
    try:
        d = datetime.datetime.strptime(dob, "%d/%m/%Y").date()
        age = (datetime.date.today() - d).days // 365
        return 5 <= age <= 80
    except Exception:
        return False

def validate_student_id(sid: str) -> bool:
    return bool(re.fullmatch(r'[A-Za-z0-9]{3,20}', sid.strip()))

def validate_name(name: str) -> bool:
    return bool(re.fullmatch(r'[A-Za-z ]{2,60}', name.strip()))

def validate_roll(roll: str) -> bool:
    return bool(re.fullmatch(r'[A-Za-z0-9]{1,10}', roll.strip()))

def validate_all_fields(obj, parent) -> bool:
    if obj.var_dep.get() == "Select Department":
        messagebox.showerror("Validation Error", "Please select a Department.", parent=parent)
        return False
    if obj.var_course.get() == "Select Course":
        messagebox.showerror("Validation Error", "Please select a Course.", parent=parent)
        return False
    if obj.var_year.get() == "Select Year":
        messagebox.showerror("Validation Error", "Please select a Year.", parent=parent)
        return False
    if obj.var_semester.get() == "Select Semester":
        messagebox.showerror("Validation Error", "Please select a Semester.", parent=parent)
        return False
    if obj.var_div.get() == "Select Division":
        messagebox.showerror("Validation Error", "Please select a Class Division.", parent=parent)
        return False
    if obj.var_gender.get() == "Select Gender":
        messagebox.showerror("Validation Error", "Please select a Gender.", parent=parent)
        return False
    if not validate_student_id(obj.va_std_id.get()):
        messagebox.showerror("Validation Error",
            "Student ID must be 3–20 alphanumeric characters (no spaces).", parent=parent)
        return False
    if not validate_name(obj.var_std_name.get()):
        messagebox.showerror("Validation Error",
            "Student Name must contain only letters/spaces (2–60 chars).", parent=parent)
        return False
    if not validate_roll(obj.var_roll.get()):
        messagebox.showerror("Validation Error",
            "Roll No must be 1–10 alphanumeric characters.", parent=parent)
        return False
    if not obj.var_dob.get():
        messagebox.showerror("Validation Error",
            "Please select a Date of Birth using the calendar button.", parent=parent)
        return False
    if not validate_dob(obj.var_dob.get()):
        messagebox.showerror("Validation Error",
            "Date of Birth is invalid or age must be between 5 and 80 years.", parent=parent)
        return False
    if not validate_gmail(obj.var_email.get().strip()):
        messagebox.showerror("Validation Error",
            "Email must be a valid Gmail address (e.g. name@gmail.com).", parent=parent)
        return False
    if not validate_phone(obj.var_phone.get().strip()):
        messagebox.showerror("Validation Error",
            "Phone No must be exactly 10 digits and start with 6–9.", parent=parent)
        return False
    if len(obj.var_address.get().strip()) < 5:
        messagebox.showerror("Validation Error",
            "Address must be at least 5 characters.", parent=parent)
        return False
    if not validate_name(obj.var_teacher.get()):
        messagebox.showerror("Validation Error",
            "Teacher Name must contain only letters/spaces (2–60 chars).", parent=parent)
        return False
    if obj.var_radio1.get() == "":
        messagebox.showerror("Validation Error",
            "Please select a Photo Sample option.", parent=parent)
        return False
    return True


# ================================================================
#                   PHONE ENTRY RESTRICTION
# ================================================================
def make_phone_validator(root):
    def _validate(action, value_if_allowed):
        if action == "1":
            if not value_if_allowed.isdigit():
                return False
            if len(value_if_allowed) > 10:
                return False
        return True
    return root.register(_validate)


# ================================================================
#                   DATABASE CONNECTION
# ================================================================
def get_connection():
    # FIX: changed 'username' to 'user' — mysql.connector uses 'user', not 'username'
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="rk2025",
        database="face_recognizer"
    )


# ================================================================
#                        STUDENT CLASS
# ================================================================
class Student:
    def __init__(self, root):
        self.root = root
        self.root.geometry("1530x790+0+0")
        self.root.title("Face Recognition Attendance System")

        self.var_dep      = StringVar()
        self.var_course   = StringVar()
        self.var_year     = StringVar()
        self.var_semester = StringVar()
        self.va_std_id    = StringVar()
        self.var_std_name = StringVar()
        self.var_div      = StringVar()
        self.var_roll     = StringVar()
        self.var_gender   = StringVar()
        self.var_dob      = StringVar()
        self.var_email    = StringVar()
        self.var_phone    = StringVar()
        self.var_address  = StringVar()
        self.var_teacher  = StringVar()
        self.var_radio1   = StringVar()

        # FIX: use relative path instead of hardcoded absolute path
        try:
            img = Image.open("img/sd.jpg")
            img = img.resize((1530, 790), Image.LANCZOS)
            self.photoimg = ImageTk.PhotoImage(img)
            bg_img = Label(self.root, image=self.photoimg)
            bg_img.place(x=0, y=0, width=1530, height=790)
        except Exception:
            bg_img = Label(self.root, bg="#e8f4f8")
            bg_img.place(x=0, y=0, width=1530, height=790)

        title_lbl = Label(
            bg_img,
            text="FACE RECOGNITION ATTENDANCE SYSTEM",
            font=("times new roman", 30, "bold"),
            bg="navy", fg="white"
        )
        title_lbl.place(x=0, y=0, width=1530, height=45)

        main_frame = Frame(bg_img, bd=2, bg="white")
        main_frame.place(x=20, y=55, width=1480, height=700)

        # ---- Left Frame ----
        Left_frame = LabelFrame(
            main_frame, bd=2, bg="white", relief=RIDGE,
            text="Student Details", font=("times new roman", 12, "bold")
        )
        Left_frame.place(x=10, y=10, width=730, height=670)

        current_course_frame = LabelFrame(
            Left_frame, bd=2, bg="white", relief=RIDGE,
            text="Current Course Information", font=("times new roman", 12, "bold")
        )
        current_course_frame.place(x=5, y=10, width=720, height=150)

        # Department
        Label(current_course_frame, text="Department",
              font=("times new roman", 13, "bold"), bg="white"
              ).grid(row=0, column=0, padx=10, pady=10, sticky=W)
        dep_combo = ttk.Combobox(current_course_frame, textvariable=self.var_dep,
                                 width=17, state="readonly",
                                 font=("times new roman", 13, "bold"))
        dep_combo["values"] = (
            "Select Department",
            "ARCH - Architecture", "CHEM - Chemistry",
            "CH - Chemical Engineering", "CE - Civil Engineering",
            "CSE - Computer Science & Engineering",
            "CA - Computer Applications (MCA)",
            "EEE - Electrical & Electronics Engineering",
            "ECE - Electronics & Communication Engineering",
            "ICE - Instrumentation & Control Engineering",
            "MECH - Mechanical Engineering",
            "MME - Metallurgical & Materials Engineering",
            "PROD - Production Engineering", "MATHS - Mathematics",
            "PHY - Physics", "MBA/DOMS - Department of Management Studies",
            "HSS - Humanities & Social Sciences", "EEEC - Energy & Environment",
            "CECASE - Advanced Communication Engineering Systems"
        )
        dep_combo.current(0)
        dep_combo.grid(row=0, column=1, padx=2)

        # Course
        Label(current_course_frame, text="Course",
              font=("times new roman", 13, "bold"), bg="white"
              ).grid(row=0, column=2, padx=10, sticky=W)
        course_combo = ttk.Combobox(current_course_frame, textvariable=self.var_course,
                                    width=17, state="readonly",
                                    font=("times new roman", 13, "bold"))
        course_combo["values"] = (
            "Select Course",
            "B.Tech (Bachelor of Technology)", "B.Arch (Bachelor of Architecture)",
            "B.Sc. B.Ed. (Integrated)", "M.Tech (Master of Technology)",
            "M.Arch (Master of Architecture)", "M.Sc (Master of Science)",
            "MCA (Master of Computer Applications)", "MBA (Master of Business Administration)",
            "M.A. (Master of Arts – English)", "M.S. (By Research)", "Ph.D. (Doctor of Philosophy)",
        )
        course_combo.current(0)
        course_combo.grid(row=0, column=3)

        # Year
        Label(current_course_frame, text="Year",
              font=("times new roman", 13, "bold"), bg="white"
              ).grid(row=1, column=0, padx=10, pady=10, sticky=W)
        year_combo = ttk.Combobox(current_course_frame, textvariable=self.var_year,
                                  width=17, state="readonly",
                                  font=("times new roman", 13, "bold"))
        year_combo["values"] = ("Select Year", "2026-27", "2027-28", "2028-29", "2029-30")
        year_combo.current(0)
        year_combo.grid(row=1, column=1)

        # Semester
        Label(current_course_frame, text="Semester",
              font=("times new roman", 13, "bold"), bg="white"
              ).grid(row=1, column=2, padx=10, sticky=W)
        semester_combo = ttk.Combobox(current_course_frame, textvariable=self.var_semester,
                                      width=17, state="readonly",
                                      font=("times new roman", 13, "bold"))
        semester_combo["values"] = (
            "Select Semester", "Semester-1", "Semester-2",
            "Semester-3", "Semester-4", "Semester-5", "Semester-6"
        )
        semester_combo.current(0)
        semester_combo.grid(row=1, column=3)

        # ---- Student Info Frame ----
        class_Student_frame = LabelFrame(
            Left_frame, bd=2, bg="white", relief=RIDGE,
            text="Class Student Information", font=("times new roman", 12, "bold")
        )
        class_Student_frame.place(x=5, y=170, width=720, height=480)

        # FIX: corrected validatecommand signature — only pass %d and %P
        phone_vcmd = make_phone_validator(self.root)

        # Student ID
        Label(class_Student_frame, text="Student ID:",
              font=("times new roman", 13, "bold"), bg="white"
              ).grid(row=0, column=0, padx=10, pady=5, sticky=W)
        ttk.Entry(class_Student_frame, textvariable=self.va_std_id,
                  width=20, font=("times new roman", 13, "bold")
                  ).grid(row=0, column=1, padx=10, pady=5, sticky=W)

        # Student Name
        Label(class_Student_frame, text="Student Name:",
              font=("times new roman", 13, "bold"), bg="white"
              ).grid(row=0, column=2, padx=10, pady=5, sticky=W)
        ttk.Entry(class_Student_frame, textvariable=self.var_std_name,
                  width=20, font=("times new roman", 13, "bold")
                  ).grid(row=0, column=3, padx=10, pady=5, sticky=W)

        # Division
        Label(class_Student_frame, text="Class Division:",
              font=("times new roman", 13, "bold"), bg="white"
              ).grid(row=1, column=0, padx=10, pady=5, sticky=W)
        division_combo = ttk.Combobox(class_Student_frame, textvariable=self.var_div,
                                      width=18, state="readonly",
                                      font=("times new roman", 13, "bold"))
        division_combo["values"] = ("Select Division", "A", "B", "C")
        division_combo.current(0)
        division_combo.grid(row=1, column=1, padx=10, pady=5, sticky=W)

        # Roll No
        Label(class_Student_frame, text="Roll No:",
              font=("times new roman", 13, "bold"), bg="white"
              ).grid(row=1, column=2, padx=10, pady=5, sticky=W)
        ttk.Entry(class_Student_frame, textvariable=self.var_roll,
                  width=20, font=("times new roman", 13, "bold")
                  ).grid(row=1, column=3, padx=10, pady=5, sticky=W)

        # Gender
        Label(class_Student_frame, text="Gender:",
              font=("times new roman", 13, "bold"), bg="white"
              ).grid(row=2, column=0, padx=10, pady=5, sticky=W)
        gender_combo = ttk.Combobox(class_Student_frame, textvariable=self.var_gender,
                                    width=18, state="readonly",
                                    font=("times new roman", 13, "bold"))
        gender_combo["values"] = ("Select Gender", "Male", "Female", "Other")
        gender_combo.current(0)
        gender_combo.grid(row=2, column=1, padx=10, pady=5, sticky=W)

        # DOB
        Label(class_Student_frame, text="DOB:",
              font=("times new roman", 13, "bold"), bg="white"
              ).grid(row=2, column=2, padx=10, pady=5, sticky=W)
        dob_frame = Frame(class_Student_frame, bg="white")
        dob_frame.grid(row=2, column=3, padx=10, pady=5, sticky=W)
        ttk.Entry(dob_frame, textvariable=self.var_dob,
                  width=13, font=("times new roman", 13, "bold"),
                  state="readonly").pack(side=LEFT)
        Button(dob_frame, text="Pick Date", font=("times new roman", 10, "bold"),
               bg="blue", fg="white", relief=FLAT, cursor="hand2",
               command=self._open_calendar).pack(side=LEFT, padx=5)

        # Email
        Label(class_Student_frame, text="Email:",
              font=("times new roman", 13, "bold"), bg="white"
              ).grid(row=3, column=0, padx=10, pady=5, sticky=W)
        ttk.Entry(class_Student_frame, textvariable=self.var_email,
                  width=20, font=("times new roman", 13, "bold")
                  ).grid(row=3, column=1, padx=10, pady=5, sticky=W)

        # Phone — FIX: corrected validatecommand to only pass %d and %P
        Label(class_Student_frame, text="Phone No:",
              font=("times new roman", 13, "bold"), bg="white"
              ).grid(row=3, column=2, padx=10, pady=5, sticky=W)
        ttk.Entry(class_Student_frame, textvariable=self.var_phone,
                  width=20, font=("times new roman", 13, "bold"),
                  validate="key",
                  validatecommand=(phone_vcmd, "%d", "%P")
                  ).grid(row=3, column=3, padx=10, pady=5, sticky=W)

        # Address
        Label(class_Student_frame, text="Address:",
              font=("times new roman", 13, "bold"), bg="white"
              ).grid(row=4, column=0, padx=10, pady=5, sticky=W)
        ttk.Entry(class_Student_frame, textvariable=self.var_address,
                  width=20, font=("times new roman", 13, "bold")
                  ).grid(row=4, column=1, padx=10, pady=5, sticky=W)

        # Teacher Name
        Label(class_Student_frame, text="Teacher Name:",
              font=("times new roman", 13, "bold"), bg="white"
              ).grid(row=4, column=2, padx=10, pady=5, sticky=W)
        ttk.Entry(class_Student_frame, textvariable=self.var_teacher,
                  width=20, font=("times new roman", 13, "bold")
                  ).grid(row=4, column=3, padx=10, pady=5, sticky=W)

        # Radio Buttons
        ttk.Radiobutton(class_Student_frame, text="Take Photo Sample",
                        variable=self.var_radio1, value="Yes"
                        ).grid(row=5, column=0, padx=10, sticky=W)
        ttk.Radiobutton(class_Student_frame, text="No Photo Sample",
                        variable=self.var_radio1, value="No"
                        ).grid(row=5, column=1, padx=10, sticky=W)

        # Buttons
        btn_frame = Frame(class_Student_frame, bd=2, relief=RIDGE, bg="white")
        btn_frame.place(x=0, y=300, width=715, height=40)
        Button(btn_frame, text="Save",   command=self.add_data,    width=17,
               font=("times new roman", 12, "bold"), bg="blue", fg="white").grid(row=0, column=0)
        Button(btn_frame, text="Update", command=self.update_data, width=17,
               font=("times new roman", 12, "bold"), bg="blue", fg="white").grid(row=0, column=1)
        Button(btn_frame, text="Delete", command=self.delete_data, width=17,
               font=("times new roman", 12, "bold"), bg="blue", fg="white").grid(row=0, column=2)
        Button(btn_frame, text="Reset",  command=self.reset_data,  width=17,
               font=("times new roman", 12, "bold"), bg="blue", fg="white").grid(row=0, column=3)

        btn_frame1 = Frame(class_Student_frame, bd=2, relief=RIDGE, bg="white")
        btn_frame1.place(x=0, y=340, width=715, height=40)
        Button(btn_frame1, text="Take Photo Sample",   command=self.generate_dataset,
               width=35, font=("times new roman", 12, "bold"), bg="green", fg="white"
               ).grid(row=0, column=0)
        Button(btn_frame1, text="Update Photo Sample", width=35,
               font=("times new roman", 12, "bold"), bg="green", fg="white"
               ).grid(row=0, column=1)

        # ---- Right Frame ----
        Right_frame = LabelFrame(
            main_frame, bd=2, bg="white", relief=RIDGE,
            text="Student Details", font=("times new roman", 12, "bold")
        )
        Right_frame.place(x=750, y=10, width=710, height=670)

        # FIX: relative path for right-frame image
        try:
            img_right = Image.open("img/kk.png")
            img_right = img_right.resize((700, 130), Image.LANCZOS)
            self.photoimg_right = ImageTk.PhotoImage(img_right)
            f_lbl = Label(Right_frame, image=self.photoimg_right)
            f_lbl.place(x=5, y=0, width=700, height=130)
        except Exception:
            f_lbl = Label(Right_frame, bg="lightgray")
            f_lbl.place(x=5, y=0, width=700, height=130)

        # Search Frame
        Search_frame = LabelFrame(
            Right_frame, bd=2, bg="white", relief=RIDGE,
            text="Search System", font=("times new roman", 12, "bold")
        )
        Search_frame.place(x=5, y=135, width=700, height=70)

        Label(Search_frame, text="Search By:", font=("times new roman", 15, "bold"),
              bg="red", fg="white").grid(row=0, column=0, padx=10, pady=5, sticky=W)

        self.search_combo = ttk.Combobox(Search_frame, font=("times new roman", 13, "bold"),
                                         state="readonly", width=15)
        self.search_combo["values"] = ("Select", "Roll_No", "Phone_No")
        self.search_combo.current(0)
        self.search_combo.grid(row=0, column=1, padx=5, pady=10)

        self.search_entry = ttk.Entry(Search_frame, width=20,
                                      font=("times new roman", 13, "bold"))
        self.search_entry.grid(row=0, column=2, padx=5, pady=10)

        Button(Search_frame, text="Search", width=12,
               font=("times new roman", 12, "bold"), bg="blue", fg="white",
               cursor="hand2", command=self.search_data).grid(row=0, column=3, padx=4)
        Button(Search_frame, text="Show All", width=7,
               font=("times new roman", 12, "bold"), bg="green", fg="white",
               cursor="hand2", command=self.fetch_data).grid(row=0, column=4, padx=4)

        # Table
        table_frame = Frame(Right_frame, bd=2, bg="white", relief=RIDGE)
        table_frame.place(x=5, y=210, width=700, height=430)

        scroll_x = ttk.Scrollbar(table_frame, orient=HORIZONTAL)
        scroll_y = ttk.Scrollbar(table_frame, orient=VERTICAL)

        self.student_table = ttk.Treeview(
            table_frame,
            columns=("dep","course","year","sem","id","name","div","roll",
                     "gender","dob","email","phone","address","teacher","photo"),
            xscrollcommand=scroll_x.set,
            yscrollcommand=scroll_y.set
        )

        scroll_x.pack(side=BOTTOM, fill=X)
        scroll_y.pack(side=RIGHT, fill=Y)
        scroll_x.config(command=self.student_table.xview)
        scroll_y.config(command=self.student_table.yview)

        headings = {
            "dep": "Department", "course": "Course", "year": "Year",
            "sem": "Semester", "id": "Student ID", "name": "Name",
            "div": "Division", "roll": "Roll No", "gender": "Gender",
            "dob": "DOB", "email": "Email", "phone": "Phone",
            "address": "Address", "teacher": "Teacher",
            "photo": "Photo Sample Status"
        }
        for col, text in headings.items():
            self.student_table.heading(col, text=text)
            self.student_table.column(col, width=120)

        self.student_table["show"] = "headings"
        self.student_table.pack(fill=BOTH, expand=1)
        self.student_table.bind("<ButtonRelease>", self.get_cursor)
        self.fetch_data()

    # ================================================================
    def _open_calendar(self):
        CalendarPicker(self.root, self.var_dob)

    # ================================================================
    #                       DATA FUNCTIONS
    # ================================================================
    def add_data(self):
        if not validate_all_fields(self, self.root):
            return
        try:
            conn = get_connection()
            my_cursor = conn.cursor()
            my_cursor.execute(
                "INSERT INTO student VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                (
                    self.var_dep.get(), self.var_course.get(), self.var_year.get(),
                    self.var_semester.get(), self.va_std_id.get(), self.var_std_name.get(),
                    self.var_div.get(), self.var_roll.get(), self.var_gender.get(),
                    self.var_dob.get(), self.var_email.get(), self.var_phone.get(),
                    self.var_address.get(), self.var_teacher.get(), self.var_radio1.get()
                )
            )
            conn.commit()
            conn.close()
            self.fetch_data()
            messagebox.showinfo("Success", "Student details added successfully.", parent=self.root)
        except Exception as es:
            messagebox.showerror("Error", f"Due To: {str(es)}", parent=self.root)

    def fetch_data(self):
        try:
            conn = get_connection()
            my_cursor = conn.cursor()
            my_cursor.execute("SELECT * FROM student")
            data = my_cursor.fetchall()
            conn.close()
            self.student_table.delete(*self.student_table.get_children())
            for row in data:
                self.student_table.insert("", END, values=row)
        except Exception as es:
            messagebox.showerror("Error", f"Failed to load data: {str(es)}", parent=self.root)

    def search_data(self):
        field = self.search_combo.get()
        value = self.search_entry.get().strip()
        if field == "Select" or value == "":
            messagebox.showerror("Error", "Please select a search field and enter a value.",
                                 parent=self.root)
            return
        # FIX: map combo label to actual DB column name
        col_map = {"Roll_No": "Roll", "Phone_No": "Phone"}
        col = col_map.get(field, field)
        try:
            conn = get_connection()
            my_cursor = conn.cursor()
            my_cursor.execute(f"SELECT * FROM student WHERE {col}=%s", (value,))
            data = my_cursor.fetchall()
            conn.close()
            self.student_table.delete(*self.student_table.get_children())
            for row in data:
                self.student_table.insert("", END, values=row)
        except Exception as es:
            messagebox.showerror("Error", f"Due To: {str(es)}", parent=self.root)

    def get_cursor(self, event=""):
        cursor_focus = self.student_table.focus()
        content = self.student_table.item(cursor_focus)
        data = content["values"]
        if not data:
            return
        self.var_dep.set(data[0])
        self.var_course.set(data[1])
        self.var_year.set(data[2])
        self.var_semester.set(data[3])
        self.va_std_id.set(data[4])
        self.var_std_name.set(data[5])
        self.var_div.set(data[6])
        self.var_roll.set(data[7])
        self.var_gender.set(data[8])
        self.var_dob.set(data[9])
        self.var_email.set(data[10])
        self.var_phone.set(data[11])
        self.var_address.set(data[12])
        self.var_teacher.set(data[13])
        self.var_radio1.set(data[14])

    def update_data(self):
        if not validate_all_fields(self, self.root):
            return
        try:
            do_update = messagebox.askyesno(
                "Update", "Do you want to update this student's details?", parent=self.root
            )
            if not do_update:
                return
            conn = get_connection()
            my_cursor = conn.cursor()
            my_cursor.execute(
                """UPDATE student SET
                Dep=%s, Course=%s, Year=%s, Semester=%s, Name=%s,
                Division=%s, Roll=%s, Gender=%s, Dob=%s, Email=%s,
                Phone=%s, Address=%s, Teacher=%s, PhotoSample=%s
                WHERE Student_id=%s""",
                (
                    self.var_dep.get(), self.var_course.get(), self.var_year.get(),
                    self.var_semester.get(), self.var_std_name.get(), self.var_div.get(),
                    self.var_roll.get(), self.var_gender.get(), self.var_dob.get(),
                    self.var_email.get(), self.var_phone.get(), self.var_address.get(),
                    self.var_teacher.get(), self.var_radio1.get(), self.va_std_id.get()
                )
            )
            conn.commit()
            conn.close()
            self.fetch_data()
            messagebox.showinfo("Success", "Student details updated successfully.", parent=self.root)
        except Exception as es:
            messagebox.showerror("Error", f"Due To: {str(es)}", parent=self.root)

    def delete_data(self):
        if self.va_std_id.get() == "":
            messagebox.showerror("Error", "Student ID is required.", parent=self.root)
            return
        try:
            do_delete = messagebox.askyesno(
                "Delete Student", "Do you want to delete this student?", parent=self.root
            )
            if not do_delete:
                return
            conn = get_connection()
            my_cursor = conn.cursor()
            my_cursor.execute("DELETE FROM student WHERE Student_id=%s",
                              (self.va_std_id.get(),))
            conn.commit()
            conn.close()
            self.fetch_data()
            messagebox.showinfo("Deleted", "Student deleted successfully.", parent=self.root)
        except Exception as es:
            messagebox.showerror("Error", f"Due To: {str(es)}", parent=self.root)

    def reset_data(self):
        self.var_dep.set("Select Department")
        self.var_course.set("Select Course")
        self.var_year.set("Select Year")
        self.var_semester.set("Select Semester")
        self.va_std_id.set("")
        self.var_std_name.set("")
        self.var_div.set("Select Division")
        self.var_roll.set("")
        self.var_gender.set("Select Gender")
        self.var_dob.set("")
        self.var_email.set("")
        self.var_phone.set("")
        self.var_address.set("")
        self.var_teacher.set("")
        self.var_radio1.set("")

    def generate_dataset(self):
        if not validate_all_fields(self, self.root):
            return

        # FIX: check that haarcascade file exists before opening camera
        if not os.path.exists("haarcascade_frontalface_default.xml"):
            messagebox.showerror("Error",
                "haarcascade_frontalface_default.xml not found.", parent=self.root)
            return

        # FIX: check/create data folder
        if not os.path.exists("data"):
            os.makedirs("data")

        try:
            conn = get_connection()
            my_cursor = conn.cursor()
            my_cursor.execute("SELECT * FROM student")
            myresult = my_cursor.fetchall()
            # FIX: use student ID from field instead of row count (avoids ID collision)
            student_id = self.va_std_id.get()

            my_cursor.execute(
                """UPDATE student SET
                Dep=%s, Course=%s, Year=%s, Semester=%s, Name=%s,
                Division=%s, Roll=%s, Gender=%s, Dob=%s, Email=%s,
                Phone=%s, Address=%s, Teacher=%s, PhotoSample=%s
                WHERE Student_id=%s""",
                (
                    self.var_dep.get(), self.var_course.get(), self.var_year.get(),
                    self.var_semester.get(), self.var_std_name.get(), self.var_div.get(),
                    self.var_roll.get(), self.var_gender.get(), self.var_dob.get(),
                    self.var_email.get(), self.var_phone.get(), self.var_address.get(),
                    self.var_teacher.get(), self.var_radio1.get(), student_id
                )
            )
            conn.commit()
            conn.close()
            self.fetch_data()
            self.reset_data()

            face_classifier = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")

            def face_cropped(img):
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                faces = face_classifier.detectMultiScale(gray, 1.3, 5)
                for (x, y, w, h) in faces:
                    return img[y:y+h, x:x+w]
                return None   # FIX: explicit None return when no face detected

            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                messagebox.showerror("Error", "Cannot access webcam.", parent=self.root)
                return

            img_id = 0
            while True:
                ret, my_frame = cap.read()
                if not ret:
                    break
                cropped = face_cropped(my_frame)
                # FIX: call face_cropped only once per frame (was called twice before)
                if cropped is not None:
                    img_id += 1
                    face = cv2.resize(cropped, (450, 450))
                    face = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
                    file_name_path = f"data/User.{student_id}.{img_id}.jpg"
                    cv2.imwrite(file_name_path, face)
                    cv2.putText(face, str(img_id), (50, 50),
                                cv2.FONT_HERSHEY_COMPLEX, 2, (0, 255, 0), 2)
                    cv2.imshow("Cropped Face", face)
                if cv2.waitKey(1) == 13 or img_id == 100:
                    break

            cap.release()
            cv2.destroyAllWindows()
            messagebox.showinfo("Result",
                f"Dataset complete! {img_id} images saved.", parent=self.root)

        except Exception as es:
            messagebox.showerror("Error", f"Due To: {str(es)}", parent=self.root)


# ================================================================
if __name__ == "__main__":
    root = Tk()
    obj = Student(root)
    root.mainloop()
