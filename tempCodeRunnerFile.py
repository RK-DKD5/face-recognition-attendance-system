from tkinter import *
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from time import strftime
from datetime import datetime
import mysql.connector
import cv2
import os
import numpy as np


class Face_Recognition:
    def __init__(self, root):
        self.root = root
        self.root.geometry("1530x790+0+0")
        self.root.title("Face Recognition Attendance System")

        title_lbl = Label(
            self.root,
            text="FACE RECOGNITION",
            font=("times new roman", 30, "bold"),
            bg="black",
            fg="white"
        )
        title_lbl.place(x=0, y=0, width=1530, height=45)

        img_top = Image.open(
            r"C:\Users\ronak\OneDrive\Pictures\Documents\Attachments\Desktop\face detection\img\MM.jpg"
        )
        img_top = img_top.resize((1530, 745), Image.LANCZOS)
        self.photoimg_top = ImageTk.PhotoImage(img_top)

        f_lbl = Label(self.root, image=self.photoimg_top)
        f_lbl.place(x=0, y=45, width=1530, height=745)

        b1 = Button(
            self.root,
            text="FACE RECOGNITION",
            font=("times new roman", 20, "bold"),
            bg="WHITE",
            fg="purple",
            cursor="hand2",
            command=self.face_recog
        )
        b1.place(x=900, y=350, width=400, height=50)

    # ============= FIX 1: Corrected attendance marking ======================
    # Only check Student_id (column 0) to prevent duplicate entries.
    # Previously checking all 4 fields caused wrong duplicate detection.
    def mark_attendance(self, s, r, n, d):
        # Skip marking attendance for unknown faces
        if s == "Unknown":
            return

        with open("Ronak.csv", "a+", newline="\n") as f:
            # Move to start to read existing entries
            f.seek(0)
            myDataList = f.readlines()

            # FIX: Collect only Student_ids (column 0) for duplicate check
            existing_ids = []
            for line in myDataList:
                line = line.strip()
                if line:  # skip empty lines
                    entry = line.split(",")
                    existing_ids.append(entry[0].strip())

            # FIX: Only mark attendance if this Student_id is NOT already recorded
            if s not in existing_ids:
                now = datetime.now()
                d1 = now.strftime("%d/%m/%Y")
                dtString = now.strftime("%H:%M:%S")
                f.write(f"\n{s},{r},{n},{d},{dtString},{d1},Present")
                print(f"[Attendance Marked] ID:{s} | Roll:{r} | Name:{n} | Dept:{d}")

    def face_recog(self):

        # ============= FIX 2: Fetch DB record by face ID ======================
        # Connect once per recognition session, not per face detected per frame.
        def get_student_from_db(face_id):
            try:
                conn = mysql.connector.connect(
                    host="localhost",
                    user="root",
                    password="rk2025",
                    database="face_recognizer"
                )
                my_cursor = conn.cursor()
                my_cursor.execute(
                    "SELECT Student_id, Roll, Name, Dep FROM student WHERE Student_id=%s",
                    (face_id,)
                )
                result = my_cursor.fetchone()
                conn.close()

                if result:
                    return str(result[0]), str(result[1]), str(result[2]), str(result[3])
                else:
                    return "Unknown", "Unknown", "Unknown", "Unknown"

            except Exception as e:
                print("Database Error:", e)
                return "Unknown", "Unknown", "Unknown", "Unknown"

        # ============= FIX 3: draw_boundary now handles each face independently =
        # Each face detection gets its OWN id/predict call, so details won't bleed.
        def draw_boundary(img, classifier, scaleFactor, minNeighbors, color, clf):

            gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            features = classifier.detectMultiScale(
                gray_image,
                scaleFactor,
                minNeighbors
            )

            for (x, y, w, h) in features:
                # FIX: predict is called per face box — each face gets its own result
                face_id, predict = clf.predict(gray_image[y:y + h, x:x + w])
                confidence = int((100 * (1 - predict / 300)))

                if confidence > 77:
                    # FIX: fetch student details using the predicted face_id
                    s, r, n, d = get_student_from_db(face_id)

                    if s != "Unknown":
                        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 3)

                        cv2.putText(img, f"ID: {s}",         (x, y - 75),
                                    cv2.FONT_HERSHEY_COMPLEX, 0.8, (255, 255, 255), 2)
                        cv2.putText(img, f"Roll: {r}",       (x, y - 55),
                                    cv2.FONT_HERSHEY_COMPLEX, 0.8, (255, 255, 255), 2)
                        cv2.putText(img, f"Name: {n}",       (x, y - 35),
                                    cv2.FONT_HERSHEY_COMPLEX, 0.8, (255, 255, 255), 2)
                        cv2.putText(img, f"Dept: {d}",       (x, y - 10),
                                    cv2.FONT_HERSHEY_COMPLEX, 0.8, (255, 255, 255), 2)

                        self.mark_attendance(s, r, n, d)

                    else:
                        # Known face_id but not in DB
                        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 3)
                        cv2.putText(img, "Not In DB", (x, y - 10),
                                    cv2.FONT_HERSHEY_COMPLEX, 0.8, (0, 0, 255), 2)
                else:
                    # Low confidence = Unknown face
                    cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 3)
                    cv2.putText(img, "Unknown Face", (x, y - 10),
                                cv2.FONT_HERSHEY_COMPLEX, 0.8, (0, 0, 255), 2)

            return img

        # ============= Validate required files =================================
        if not os.path.exists("haarcascade_frontalface_default.xml"):
            messagebox.showerror("Error", "haarcascade_frontalface_default.xml not found")
            return

        if not os.path.exists("classifier.xml"):
            messagebox.showerror("Error", "classifier.xml not found. Train the data first.")
            return

        faceCascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
        clf = cv2.face.LBPHFaceRecognizer_create()
        clf.read("classifier.xml")

        video_cap = cv2.VideoCapture(0)

        if not video_cap.isOpened():
            messagebox.showerror("Error", "Cannot access webcam")
            return

        while True:
            ret, img = video_cap.read()
            if not ret:
                break

            # FIX: pass img directly; draw_boundary now returns the annotated image
            img = draw_boundary(img, faceCascade, 1.1, 10, (255, 25, 255), clf)

            cv2.imshow("Welcome To Face Recognition", img)

            if cv2.waitKey(1) == 13:  # Press Enter to quit
                break

        video_cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    root = Tk()
    obj = Face_Recognition(root)
    root.mainloop()