from tkinter import *
from tkinter import messagebox
from PIL import Image, ImageTk
from datetime import datetime
import mysql.connector
import cv2
import os


class Face_Recognition:
    def __init__(self, root):
        self.root = root
        self.root.geometry("1530x790+0+0")
        self.root.title("Face Recognition Attendance System")

        title_lbl = Label(
            self.root,
            text="FACE RECOGNITION",
            font=("times new roman", 30, "bold"),
            bg="black", fg="white"
        )
        title_lbl.place(x=0, y=0, width=1530, height=45)

        # FIX: relative path + try/except to prevent crash on other machines
        try:
            img_top = Image.open("img/MM.jpg")
            img_top = img_top.resize((1530, 745), Image.LANCZOS)
            self.photoimg_top = ImageTk.PhotoImage(img_top)
            f_lbl = Label(self.root, image=self.photoimg_top)
            f_lbl.place(x=0, y=45, width=1530, height=745)
        except Exception:
            f_lbl = Label(self.root, bg="#1a1a2e")
            f_lbl.place(x=0, y=45, width=1530, height=745)

        b1 = Button(
            self.root,
            text="FACE RECOGNITION",
            font=("times new roman", 20, "bold"),
            bg="white", fg="purple",
            cursor="hand2",
            command=self.face_recog
        )
        b1.place(x=900, y=350, width=400, height=50)

    # ================================================================
    #   FIX: already_marked is now a set loaded ONCE before the loop.
    #   mark_attendance checks the set (in memory) instead of
    #   opening+reading the CSV file on every single frame.
    # ================================================================
    def mark_attendance(self, s, r, n, d, already_marked: set):
        if s == "Unknown":
            return
        if s in already_marked:
            return
        now = datetime.now()
        d1 = now.strftime("%d/%m/%Y")
        dtString = now.strftime("%H:%M:%S")
        try:
            with open("Ronak.csv", "a", newline="") as f:
                f.write(f"\n{s},{r},{n},{d},{dtString},{d1},Present")
            already_marked.add(s)
            print(f"[Attendance Marked] ID:{s} | Roll:{r} | Name:{n} | Dept:{d}")
        except Exception as e:
            print(f"[CSV Write Error] {e}")

    def face_recog(self):

        # FIX: validate required files before doing anything else
        if not os.path.exists("haarcascade_frontalface_default.xml"):
            messagebox.showerror("Error", "haarcascade_frontalface_default.xml not found.")
            return
        if not os.path.exists("classifier.xml"):
            messagebox.showerror("Error", "classifier.xml not found. Train the data first.")
            return

        faceCascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
        clf = cv2.face.LBPHFaceRecognizer_create()
        clf.read("classifier.xml")

        video_cap = cv2.VideoCapture(0)
        if not video_cap.isOpened():
            messagebox.showerror("Error", "Cannot access webcam.")
            return

        # FIX: open ONE database connection for the whole session
        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="rk2025",
                database="face_recognizer"
            )
            my_cursor = conn.cursor()
        except Exception as e:
            messagebox.showerror("DB Error", f"Cannot connect to database:\n{e}")
            video_cap.release()
            return

        # FIX: load already-marked IDs once into a set before starting the loop
        already_marked = set()
        try:
            if os.path.exists("Ronak.csv"):
                with open("Ronak.csv", "r") as f:
                    for line in f:
                        parts = line.strip().split(",")
                        if parts and parts[0].strip():
                            already_marked.add(parts[0].strip())
        except Exception as e:
            print(f"[CSV Read Warning] {e}")

        # ---- helper: fetch student using the shared cursor ----
        def get_student_from_db(face_id):
            try:
                my_cursor.execute(
                    "SELECT Student_id, Roll, Name, Dep FROM student WHERE Student_id=%s",
                    (face_id,)
                )
                result = my_cursor.fetchone()
                if result:
                    return str(result[0]), str(result[1]), str(result[2]), str(result[3])
                return "Unknown", "Unknown", "Unknown", "Unknown"
            except Exception as e:
                print(f"[DB Query Error] {e}")
                return "Unknown", "Unknown", "Unknown", "Unknown"

        # ---- draw bounding boxes and recognise faces ----
        # FIX: removed unused 'color' parameter; green/red are now the explicit intent
        def draw_boundary(img):
            gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            features = faceCascade.detectMultiScale(gray_image, scaleFactor=1.1,
                                                    minNeighbors=10)
            for (x, y, w, h) in features:
                face_id, predict = clf.predict(gray_image[y:y+h, x:x+w])
                confidence = int(100 * (1 - predict / 300))

                if confidence > 77:
                    s, r, n, d = get_student_from_db(face_id)
                    if s != "Unknown":
                        cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 3)
                        cv2.putText(img, f"ID: {s}",   (x, y-75),
                                    cv2.FONT_HERSHEY_COMPLEX, 0.8, (255, 255, 255), 2)
                        cv2.putText(img, f"Roll: {r}", (x, y-55),
                                    cv2.FONT_HERSHEY_COMPLEX, 0.8, (255, 255, 255), 2)
                        cv2.putText(img, f"Name: {n}", (x, y-35),
                                    cv2.FONT_HERSHEY_COMPLEX, 0.8, (255, 255, 255), 2)
                        cv2.putText(img, f"Dept: {d}", (x, y-10),
                                    cv2.FONT_HERSHEY_COMPLEX, 0.8, (255, 255, 255), 2)
                        # FIX: pass already_marked set so CSV is not re-read every frame
                        self.mark_attendance(s, r, n, d, already_marked)
                    else:
                        cv2.rectangle(img, (x, y), (x+w, y+h), (0, 0, 255), 3)
                        cv2.putText(img, "Not In DB", (x, y-10),
                                    cv2.FONT_HERSHEY_COMPLEX, 0.8, (0, 0, 255), 2)
                else:
                    cv2.rectangle(img, (x, y), (x+w, y+h), (0, 0, 255), 3)
                    cv2.putText(img, "Unknown Face", (x, y-10),
                                cv2.FONT_HERSHEY_COMPLEX, 0.8, (0, 0, 255), 2)
            return img

        # ---- main video loop ----
        while True:
            ret, img = video_cap.read()
            if not ret:
                break
            img = draw_boundary(img)
            cv2.imshow("Face Recognition — Press Enter to Exit", img)
            if cv2.waitKey(1) == 13:   # Enter key
                break

        # FIX: always close camera and DB connection cleanly
        video_cap.release()
        cv2.destroyAllWindows()
        conn.close()


if __name__ == "__main__":
    root = Tk()
    obj = Face_Recognition(root)
    root.mainloop()
