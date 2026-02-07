import os
import cv2
import tkinter as tk
from tkinter import messagebox
import face_recognition
import datetime
import numpy as np


def get_button(window, text, color, command, fg='white'):
    button = tk.Button(
        window,
        text=text,
        activebackground=color,
        activeforeground="white",
        fg='#E6EDF3',
        bg=color,
        command=command,
        height=1,
        relief='flat',
        cursor='hand2',
        font=("Segoe UI", 11, "bold"),
        borderwidth=0
    )
    
    # Hover effects
    def on_enter(e):
        if color == '#238636':  # Green
            button.config(bg='#2EA043')
        elif color == '#1F6FEB':  # Blue
            button.config(bg='#388BFD')
        elif color == '#DA3633':  # Red
            button.config(bg='#F85149')
        else:
            button.config(bg='#30363D')

    def on_leave(e):
        button.config(bg=color)

    button.bind("<Enter>", on_enter)
    button.bind("<Leave>", on_leave)

    return button


def get_img_label(window):
    label = tk.Label(window, bg='#000000', bd=0)
    label.grid(row=0, column=0)
    return label


def get_text_label(window, text, size=14):
    label = tk.Label(window, text=text, bg='#161B22', fg='#E6EDF3')
    label.config(font=("Segoe UI", size), justify="left")
    return label


class ToolTip:
    """Simple tooltip for tkinter widgets"""
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event=None):
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25

        self.tooltip = tk.Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")

        label = tk.Label(
            self.tooltip,
            text=self.text,
            background="#1F6FEB",
            foreground="#FFFFFF",
            relief="solid",
            borderwidth=1,
            font=("Segoe UI", 9),
            padx=8,
            pady=4
        )
        label.pack()

    def hide_tooltip(self, event=None):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None


def get_entry_text(window):
    inputtxt = tk.Text(window,
                       height=1,
                       width=15, 
                       font=("Helvetica", 24),
                       relief='solid',
                       borderwidth=1)
    return inputtxt


def msg_box(title, description):
    messagebox.showinfo(title, description)


def recognize(img, known_face_encodings):
    """
    Recognizes a face in an image given a list of known face encodings.
    Returns the index of the first match or None.
    """
    # Find all face encodings in the current frame
    face_locations = face_recognition.face_locations(img)
    face_encodings = face_recognition.face_encodings(img, face_locations)

    results = []
    for face_encoding, face_location in zip(face_encodings, face_locations):
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
        name = "Unknown"

        # Use the known face with the smallest distance to the new face
        face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
        if len(face_distances) > 0:
            import numpy as np
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                results.append((best_match_index, face_location))
            else:
                results.append((None, face_location))
        else:
            results.append((None, face_location))
            
    return results

def load_db(db_path):
    known_face_encodings = []
    known_face_names = []

    if not os.path.exists(db_path):
        os.mkdir(db_path)

    for filename in os.listdir(db_path):
        if filename.endswith(".jpg") or filename.endswith(".png"):
            path = os.path.join(db_path, filename)
            image = face_recognition.load_image_file(path)
            encodings = face_recognition.face_encodings(image)
            if len(encodings) > 0:
                known_face_encodings.append(encodings[0])
                known_face_names.append(os.path.splitext(filename)[0])
    
    return known_face_encodings, known_face_names

def log_attendance(name, log_path):
    with open(log_path, 'a') as f:
        f.write('{},{}\n'.format(name, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
