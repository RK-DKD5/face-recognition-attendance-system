from tkinter import *
from tkinter import messagebox
from PIL import Image, ImageTk
import mysql.connector
import re
import smtplib
import random
import string


# ================= Database Connection =================
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="rk2025",
        database="face_recognizer"
    )


# ================= Create Users Table If Not Exists =================
def create_users_table():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password VARCHAR(100) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()

        cursor.execute("SELECT COUNT(*) FROM users")
        count = cursor.fetchone()[0]
        if count == 0:
            cursor.execute(
                "INSERT INTO users (username, password, email) VALUES (%s, %s, %s)",
                ("admin", "admin123", "admin@college.com")
            )
            conn.commit()

        conn.close()
    except Exception as e:
        messagebox.showerror("Database Error", str(e))


# ================= Generate Random Password =================
def generate_password(length=8):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))


# ================= Send Email =================
def send_email(to_email, new_password):
    try:
        sender_email = "shivdkd699@gmail.com"
        sender_password = "lkriemmoyhniaxyx"

        subject = "Face Recognition System - Password Reset"
        body = f"""Hello,

Your password has been reset successfully.

Your new password is: {new_password}

Please login and change your password.

Regards,
Face Recognition Attendance System"""

        message = f"Subject: {subject}\n\n{body}"

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, to_email, message)
        server.quit()
        return True
    except Exception as e:
        messagebox.showerror("Email Error", f"Could not send email:\n{str(e)}")
        return False


# ================================================================
#                        LOGIN WINDOW
# ================================================================
class LoginPage:
    def __init__(self, root):
        self.root = root
        self.root.geometry("1530x790+0+0")
        self.root.title("Face Recognition System - Login")
        self.root.resizable(False, False)
        self.root.configure(bg="#0d1117")

        # ---- NEW: track password visibility ----
        self.show_password = False

        # ---- Left Panel ----
        left_panel = Frame(self.root, bg="#161b22", width=765, height=790)
        left_panel.place(x=0, y=0)

        try:
            img7 = Image.open(
                r"C:\Users\ronak\OneDrive\Pictures\Documents\Attachments\Desktop\face detection\img\y.png"
            )
            img7 = img7.resize((765, 790), Image.LANCZOS)
            self.photoimg7 = ImageTk.PhotoImage(img7)
            img_lbl = Label(left_panel, image=self.photoimg7, bd=0)
            img_lbl.place(x=0, y=0, width=765, height=790)
        except Exception as e:
            messagebox.showerror("Image Error", f"Unable to load image:\n{e}", parent=self.root)

        # ---- Right Panel (Login Form) ----
        right_panel = Frame(self.root, bg="#0d1117", width=765, height=790)
        right_panel.place(x=765, y=0)

        # Form Card
        card = Frame(right_panel, bg="#161b22", bd=0)
        card.place(x=100, y=170, width=560, height=420)

        Label(
            card,
            text="Welcome Back",
            font=("Arial Black", 26, "bold"),
            bg="#161b22",
            fg="white"
        ).place(x=40, y=40)

        Label(
            card,
            text="Sign in to continue",
            font=("Arial", 13),
            bg="#161b22",
            fg="#8b949e"
        ).place(x=40, y=90)

        # Username
        Label(
            card,
            text="Username",
            font=("Arial", 12, "bold"),
            bg="#161b22",
            fg="#c9d1d9"
        ).place(x=40, y=145)

        self.entry_username = Entry(
            card,
            font=("Arial", 13),
            bg="#21262d",
            fg="white",
            insertbackground="white",
            bd=0,
            relief=FLAT
        )
        self.entry_username.place(x=40, y=175, width=480, height=42)
        Frame(card, bg="#30363d", height=2, width=480).place(x=40, y=217)

        # Password
        Label(
            card,
            text="Password",
            font=("Arial", 12, "bold"),
            bg="#161b22",
            fg="#c9d1d9"
        ).place(x=40, y=240)

        self.entry_password = Entry(
            card,
            font=("Arial", 13),
            bg="#21262d",
            fg="white",
            insertbackground="white",
            bd=0,
            relief=FLAT,
            show="*"
        )
        # ---- NEW: leave 42px on the right for the eye button ----
        self.entry_password.place(x=40, y=270, width=438, height=42)
        Frame(card, bg="#30363d", height=2, width=480).place(x=40, y=312)

        # ---- NEW: Eye toggle button ----
        self.eye_btn = Button(
            card,
            text="👁",
            font=("Arial", 14),
            bg="#21262d",
            fg="#8b949e",
            activebackground="#21262d",
            activeforeground="#c9d1d9",
            bd=0,
            relief=FLAT,
            cursor="hand2",
            command=self.toggle_password
        )
        self.eye_btn.place(x=482, y=270, width=38, height=42)

        # Forgot Password link
        fp_label = Label(
            card,
            text="Forgot Password?",
            font=("Arial", 11, "underline"),
            bg="#161b22",
            fg="#58a6ff",
            cursor="hand2"
        )
        fp_label.place(x=40, y=328)
        fp_label.bind("<Button-1>", lambda e: self.open_forgot_password())

        # Login Button
        Button(
            card,
            text="LOGIN",
            font=("Arial", 13, "bold"),
            bg="#238636",
            fg="white",
            activebackground="#2ea043",
            activeforeground="white",
            bd=0,
            cursor="hand2",
            command=self.login
        ).place(x=40, y=370, width=480, height=48)

        # Footer
        Label(
            right_panel,
            text="© Face Recognition Attendance System",
            font=("Arial", 10),
            bg="#0d1117",
            fg="#484f58"
        ).place(x=170, y=740)

        self.root.bind("<Return>", lambda e: self.login())
        create_users_table()

    # ================= NEW: Toggle Password Visibility =================
    def toggle_password(self):
        self.show_password = not self.show_password
        if self.show_password:
            self.entry_password.config(show="")
            self.eye_btn.config(text="🔒")   # closed = hiding again option
        else:
            self.entry_password.config(show="*")
            self.eye_btn.config(text="👁")

    # ================= Login =================
    def login(self):
        username = self.entry_username.get().strip()
        password = self.entry_password.get().strip()

        if username == "" or password == "":
            messagebox.showerror("Error", "All fields are required", parent=self.root)
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM users WHERE username=%s AND password=%s",
                (username, password)
            )
            user = cursor.fetchone()
            conn.close()

            if user:
                messagebox.showinfo("Success", f"Welcome, {username}!", parent=self.root)
                self.root.destroy()
                from tkinter import Tk
                from main import Face_Recognition_System
                root = Tk()
                Face_Recognition_System(root)
                root.mainloop()
            else:
                messagebox.showerror("Error", "Invalid username or password", parent=self.root)
        except Exception as e:
            messagebox.showerror("Error", f"Due To: {str(e)}", parent=self.root)

    # ================= Open Forgot Password =================
    def open_forgot_password(self):
        fp_win = Toplevel(self.root)
        ForgotPassword(fp_win)


# ================================================================
#                    FORGOT PASSWORD WINDOW
# ================================================================
class ForgotPassword:
    def __init__(self, root):
        self.root = root
        self.root.geometry("460x320+530+230")
        self.root.title("Forgot Password")
        self.root.resizable(False, False)
        self.root.configure(bg="#161b22")
        self.root.grab_set()

        Label(self.root, text="Reset Password", font=("Arial Black", 20, "bold"), bg="#161b22", fg="white").place(x=120, y=30)
        Label(self.root, text="Enter your registered email address", font=("Arial", 12), bg="#161b22", fg="#8b949e").place(x=70, y=75)
        Label(self.root, text="Email Address", font=("Arial", 12, "bold"), bg="#161b22", fg="#c9d1d9").place(x=50, y=120)

        self.email_entry = Entry(self.root, font=("Arial", 13), bg="#21262d", fg="white", insertbackground="white", bd=0)
        self.email_entry.place(x=50, y=150, width=360, height=42)
        Frame(self.root, bg="#30363d", height=2, width=360).place(x=50, y=192)

        Label(self.root, text="A new password will be sent to your email.", font=("Arial", 10), bg="#161b22", fg="#484f58").place(x=60, y=208)

        Button(self.root, text="SEND NEW PASSWORD", font=("Arial", 13, "bold"), bg="#1f6feb", fg="white", activebackground="#388bfd", bd=0, cursor="hand2", command=self.reset_password).place(x=50, y=248, width=360, height=45)

    def reset_password(self):
        email = self.email_entry.get().strip()

        if email == "":
            messagebox.showerror("Error", "Please enter your email", parent=self.root)
            return

        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            messagebox.showerror("Error", "Invalid email address", parent=self.root)
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
            user = cursor.fetchone()

            if not user:
                messagebox.showerror("Error", "Email not found in our records", parent=self.root)
                conn.close()
                return

            new_password = generate_password()
            cursor.execute("UPDATE users SET password=%s WHERE email=%s", (new_password, email))
            conn.commit()
            conn.close()

            if send_email(email, new_password):
                messagebox.showinfo("Success", f"New password sent to {email}\nPlease check your inbox.", parent=self.root)
                self.root.destroy()

        except Exception as e:
            messagebox.showerror("Error", f"Due To: {str(e)}", parent=self.root)


# ================================================================
#                          MAIN
# ================================================================
if __name__ == "__main__":
    root = Tk()
    obj = LoginPage(root)
    root.mainloop()