from tkinter import *
import tkinter
from PIL import Image, ImageTk
from tkinter import messagebox
from student import Student
import os
from train import Train
from face_recognition import Face_Recognition
from attendance import Attendance


class Face_Recognition_System:
    def __init__(self, root):
        self.root = root
        self.root.geometry("1530x790+0+0")
        self.root.title("Face Recognition System")

        try:
            # ================= Background =================
            img = Image.open(
                r"C:\Users\ronak\OneDrive\Pictures\Documents\Attachments\Desktop\face detection\img\Gemini_Generated_Image_52j1un52j1un52j1.png"
            )
            img = img.resize((1530, 790), Image.LANCZOS)
            self.photoimg = ImageTk.PhotoImage(img)

            bg_img = Label(self.root, image=self.photoimg)
            bg_img.place(x=0, y=0, width=1530, height=790)

            # ================= Student Details =================
            img5 = Image.open(
                r"C:\Users\ronak\OneDrive\Pictures\Documents\Attachments\Desktop\face detection\img\yy.webp"
            )
            img5 = img5.resize((150, 150), Image.LANCZOS)
            self.photoimg5 = ImageTk.PhotoImage(img5)

            b2 = Button(
                bg_img,
                image=self.photoimg5,
                cursor="hand2",
                command=self.student_details
            )
            b2.place(x=30, y=30, width=150, height=150)

            b2_1 = Button(
                bg_img,
                text="Student Details",
                cursor="hand2",
                font=("times new roman", 15, "bold"),
                bg="darkgreen",
                fg="white",
                command=self.student_details
            )
            b2_1.place(x=30, y=170, width=150, height=40)

            # ================= Face Detector =================
            img6 = Image.open(
                r"C:\Users\ronak\OneDrive\Pictures\Documents\Attachments\Desktop\face detection\img\facedetector.avif"
            )
            img6 = img6.resize((150, 150), Image.LANCZOS)
            self.photoimg6 = ImageTk.PhotoImage(img6)

            b3 = Button(
                bg_img,
                image=self.photoimg6,
                cursor="hand2",
                command=self.face_data
            )
            b3.place(x=30, y=220, width=150, height=150)

            b3_1 = Button(
                bg_img,
                text="Face Detector",
                cursor="hand2",
                font=("times new roman", 15, "bold"),
                bg="darkgreen",
                fg="white",
                command=self.face_data
            )
            b3_1.place(x=30, y=360, width=150, height=40)

            # ================= Attendance =================
            img7 = Image.open(
                r"C:\Users\ronak\OneDrive\Pictures\Documents\Attachments\Desktop\face detection\img\a1.jpg"
            )
            img7 = img7.resize((150, 150), Image.LANCZOS)
            self.photoimg7 = ImageTk.PhotoImage(img7)

            b4 = Button(
                bg_img,
                image=self.photoimg7,
                cursor="hand2",
                command=self.attendance_data
            )
            b4.place(x=30, y=410, width=150, height=150)

            b4_1 = Button(
                bg_img,
                text="Attendance",
                cursor="hand2",
                font=("times new roman", 15, "bold"),
                bg="darkgreen",
                fg="white",
                command=self.attendance_data
            )
            b4_1.place(x=30, y=550, width=150, height=40)

            # ================= Training Data =================
            img8 = Image.open(
                r"C:\Users\ronak\OneDrive\Pictures\Documents\Attachments\Desktop\face detection\img\t.jpg"
            )
            img8 = img8.resize((150, 150), Image.LANCZOS)
            self.photoimg8 = ImageTk.PhotoImage(img8)

            b5 = Button(
                bg_img,
                image=self.photoimg8,
                cursor="hand2",command=self.train_data,

            )
            b5.place(x=30, y=600, width=150, height=150)

            b5_1 = Button(
                bg_img,
                text="Training Data",command=self.train_data,
                cursor="hand2",
                font=("times new roman", 15, "bold"),
                bg="darkgreen",
                fg="white",

            )
            b5_1.place(x=30, y=750, width=150, height=35)

            # ================= Photo Data =================
            img9 = Image.open(
                r"C:\Users\ronak\OneDrive\Pictures\Documents\Attachments\Desktop\face detection\img\ph.png"
            )
            img9 = img9.resize((150, 150), Image.LANCZOS)
            self.photoimg9 = ImageTk.PhotoImage(img9)

            b6 = Button(
                bg_img,
                image=self.photoimg9,
                cursor="hand2",command=self.open_img,
            )
            b6.place(x=1300, y=50, width=150, height=140)

            b6_1 = Button(
                bg_img,
                text="Photo Data",
                cursor="hand2",command=self.open_img,
                font=("times new roman", 15, "bold"),
                bg="darkgreen",
                fg="white",
                
            )
            b6_1.place(x=1300, y=175, width=150, height=40)

            
            b6_1 = Button(
                bg_img,
                text="EXIT",
                cursor="hand2",command=self.iExit,
                font=("times new roman", 15, "bold"),
                bg="darkgreen",
                fg="white",
                
            )
            b6_1.place(x=1430, y=0, width=100, height=30)

        except Exception as e:
            messagebox.showerror("Error", f"{str(e)}")

    # ================= Student Details =================
    def student_details(self):
        self.new_window = Toplevel(self.root)
        self.app = Student(self.new_window)
    def open_img(self):
        os.startfile("data")
    def iExit(self):
        self.iExit=tkinter.messagebox.askyesno("Face Recognition","Are you sure exit this project",parent=self.root)
        if self.iExit >0:
            self.root.destroy()
        else:
            return        

    # ================= Face Detector =================
    def face_detector(self):
        print("Face Detector Button Clicked")
    def train_data(self):
        self.new_window = Toplevel(self.root)
        self.app =Train(self.new_window)

    def face_data(self):
        self.new_window = Toplevel(self.root)
        self.app =Face_Recognition(self.new_window)    
    def attendance_data(self):
        self.new_window = Toplevel(self.root)
        self.app =Attendance(self.new_window)    
    

if __name__ == "__main__":
    root = Tk()
    obj = Face_Recognition_System(root)
    root.mainloop()