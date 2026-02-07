import tkinter as tk
from tkinter import ttk
import cv2
import util
import os
from PIL import Image, ImageTk
import face_recognition
import datetime
import numpy as np

class App:
    def __init__(self):
        self.mainWindow = tk.Tk()
        self.mainWindow.title("Attendance System")
        self.mainWindow.geometry("1500x850+50+20")
        self.mainWindow.configure(bg='#0D1117')

        # Database and Paths
        self.db_dir = './db'
        self.log_path = './log.txt'
        
        # State Variables
        self.known_face_encodings = []
        self.known_face_names = []
        self.most_recent_capture_arr = None
        self.temp_capture = None
        self.frame_count = 0
        self.cached_faces = []
        self.status_text = "Initializing..."
        self.status_color = "#FFA657"  # Orange for initializing
        
        # UI Elements
        self.webcam_label = None
        self.webcam_container = None
        self.log_listbox = None
        self.login_button = None
        self.register_button = None
        self.registerWindow = None
        self.reg_webcam_label = None
        self.reg_webcam_container = None
        self.name_entry = None
        self.snapshot_label = None
        self.snapshot_frame = None
        self.status_indicator = None
        self.status_label = None
        
        if not os.path.exists(self.db_dir):
            os.mkdir(self.db_dir)

        # Load Known Faces
        self.known_face_encodings, self.known_face_names = util.load_db(self.db_dir)

        # UI Layout
        self._setup_ui()
        
        # Webcam Setup
        self.cap = cv2.VideoCapture(0)
        self._update_status("Camera Ready", "#238636")  # Green
        self.process_webcam()

    def _setup_ui(self):
        # Header with gradient effect
        header_frame = tk.Frame(self.mainWindow, bg='#161B22', height=80)
        header_frame.pack(fill='x', side='top')
        
        title_frame = tk.Frame(header_frame, bg='#161B22')
        title_frame.pack(expand=True)
        
        tk.Label(title_frame, text="⚡", font=("Segoe UI Emoji", 28), bg='#161B22', fg='#58A6FF').pack(side='left', padx=10)
        tk.Label(title_frame, text="ATTENDANCE SYSTEM", font=("Segoe UI", 24, "bold"), fg="#E6EDF3", bg='#161B22').pack(side='left')
        tk.Label(title_frame, text="PRO", font=("Segoe UI", 24, "bold"), fg="#58A6FF", bg='#161B22').pack(side='left', padx=5)
        
        # Status indicator
        status_frame = tk.Frame(title_frame, bg='#161B22')
        status_frame.pack(side='right', padx=20)
        self.status_indicator = tk.Label(status_frame, text="●", font=("Segoe UI", 16), bg='#161B22', fg=self.status_color)
        self.status_indicator.pack(side='left', padx=5)
        self.status_label = tk.Label(status_frame, text=self.status_text, font=("Segoe UI", 10), bg='#161B22', fg='#8B949E')
        self.status_label.pack(side='left')

        # Main Container
        main_container = tk.Frame(self.mainWindow, bg='#0D1117')
        main_container.pack(fill='both', expand=True, padx=25, pady=20)

        # Left: Webcam Feed
        left_panel = tk.Frame(main_container, bg='#0D1117')
        left_panel.pack(side='left', fill='both', expand=True, padx=(0, 15))
        
        tk.Label(left_panel, text="LIVE FEED", font=("Segoe UI", 11, "bold"), bg='#0D1117', fg='#7D8590').pack(anchor='w', pady=(0, 8))
        
        self.webcam_container = tk.Frame(left_panel, bg='#161B22', bd=0, highlightthickness=2, highlightbackground='#30363D')
        self.webcam_container.pack(fill='both', expand=True)
        
        self.webcam_label = tk.Label(self.webcam_container, bg='#000000')
        self.webcam_label.pack(fill='both', expand=True, padx=3, pady=3)

        # Right: Control Panel
        right_panel = tk.Frame(main_container, bg='#161B22', width=420, highlightthickness=2, highlightbackground='#30363D')
        right_panel.pack(side='right', fill='y')
        right_panel.pack_propagate(False)

        # Control Section
        control_frame = tk.Frame(right_panel, bg='#161B22')
        control_frame.pack(fill='x', padx=25, pady=25)
        
        tk.Label(control_frame, text="CONTROLS", font=("Segoe UI", 12, "bold"), bg='#161B22', fg='#7D8590').pack(anchor='w', pady=(0, 15))
        
        self.login_button = util.get_button(control_frame, '🔐 CLOCK IN', '#238636', self.login)
        self.login_button.pack(fill='x', pady=6, ipady=8)
        util.ToolTip(self.login_button, "Record attendance for recognized user")
        
        self.register_button = util.get_button(control_frame, '➕ NEW USER', '#1F6FEB', self.register)
        self.register_button.pack(fill='x', pady=6, ipady=8)
        util.ToolTip(self.register_button, "Register a new user in the system")

        # Separator
        tk.Frame(right_panel, height=1, bg='#30363D').pack(fill='x', padx=25, pady=15)

        # Activity Log
        log_frame = tk.Frame(right_panel, bg='#161B22')
        log_frame.pack(fill='both', expand=True, padx=25, pady=(0, 25))
        
        tk.Label(log_frame, text="RECENT ACTIVITY", font=("Segoe UI", 12, "bold"), bg='#161B22', fg='#7D8590').pack(anchor='w', pady=(0, 10))
        
        log_container = tk.Frame(log_frame, bg='#0D1117', highlightthickness=1, highlightbackground='#30363D')
        log_container.pack(fill='both', expand=True)
        
        # Scrollbar for log
        scrollbar = tk.Scrollbar(log_container, bg='#161B22', troughcolor='#0D1117', activebackground='#58A6FF')
        scrollbar.pack(side='right', fill='y')
        
        self.log_listbox = tk.Listbox(
            log_container, 
            font=("Consolas", 9), 
            relief='flat', 
            bg='#0D1117', 
            fg='#8B949E',
            selectbackground='#1F6FEB',
            selectforeground='#FFFFFF',
            highlightthickness=0,
            borderwidth=0,
            yscrollcommand=scrollbar.set
        )
        self.log_listbox.pack(side='left', fill='both', expand=True, padx=8, pady=8)
        scrollbar.config(command=self.log_listbox.yview)
        self._update_log_history()

    def _update_log_history(self):
        self.log_listbox.delete(0, tk.END)
        if os.path.exists(self.log_path):
            with open(self.log_path, 'r') as f:
                lines = f.readlines()
                start_index = max(0, len(lines) - 25)
                recent_lines = lines[start_index:]
                recent_lines.reverse()
                for line in recent_lines:
                    if line.strip():
                        parts = line.strip().split(',')
                        if len(parts) >= 2:
                            name = parts[0]
                            timestamp = parts[1]
                            # Parse timestamp
                            try:
                                dt = datetime.datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S.%f')
                                time_str = dt.strftime('%I:%M %p')
                                date_str = dt.strftime('%b %d')
                                formatted = f"  ✓ {name:<15} {date_str} at {time_str}"
                            except:
                                formatted = f"  ✓ {name} - {timestamp}"
                            self.log_listbox.insert(tk.END, formatted)

    def _update_status(self, text, color):
        """Update the status indicator"""
        self.status_text = text
        self.status_color = color
        if hasattr(self, 'status_indicator'):
            self.status_indicator.config(fg=color)
            self.status_label.config(text=text)

    def process_webcam(self):
        ret, frame = self.cap.read()
        if not ret:
            self.mainWindow.after(30, self.process_webcam)
            return

        self.most_recent_capture_arr = frame.copy()
        
        # Performance: Only run recognition every 15 frames (reduced CPU usage)
        if self.frame_count % 45 == 0:
            small_frame = cv2.resize(frame, (0, 0), fx=0.2, fy=0.2)
            rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
            
            face_locations = face_recognition.face_locations(rgb_small_frame, model='hog')
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

            self.cached_faces = []
            for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                name = "Unknown"
                if len(self.known_face_encodings) > 0:
                    matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding, tolerance=0.6)
                    face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
                    best_match_index = np.argmin(face_distances)
                    if matches[best_match_index]:
                        name = self.known_face_names[best_match_index]
                self.cached_faces.append((top*5, right*5, bottom*5, left*5, name))

        # Draw overlay
        for (top, right, bottom, left, name) in self.cached_faces:
            color = (88, 166, 255) if name != "Unknown" else (255, 100, 100)  # Blue/Red
            cv2.rectangle(frame, (left, top), (right, bottom), color, 3)
            
            # Name tag background
            cv2.rectangle(frame, (left, bottom + 2), (right, bottom + 32), color, cv2.FILLED)
            cv2.putText(frame, name, (left + 8, bottom + 22), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        self.frame_count += 1
        img_ = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img_)
        imgtk = ImageTk.PhotoImage(image=img_pil)
        self.webcam_label.imgtk = imgtk
        self.webcam_label.configure(image=imgtk)

        self.mainWindow.after(30, self.process_webcam)

    def login(self):
        if self.most_recent_capture_arr is None: return
        
        self._update_status("Processing...", "#FFA657")  # Orange
        frame = self.most_recent_capture_arr
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        if not face_encodings:
            util.msg_box('⚠️ Alert', "No face detected. Please position yourself in front of the camera.")
            return

        name = "Unknown"
        match_found = False
        
        for face_encoding in face_encodings:
            if len(self.known_face_encodings) > 0:
                matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding, tolerance=0.6)
                face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    name = self.known_face_names[best_match_index]
                    match_found = True
                    break

        if match_found:
            self._update_status("Success!", "#238636")  # Green
            util.msg_box('✅ Success', f'Welcome back, {name}!\nClock-in recorded.')
            util.log_attendance(name, self.log_path)
            self._update_log_history()
            self.mainWindow.after(2000, lambda: self._update_status("Camera Ready", "#238636"))
        else:
            self._update_status("Not Recognized", "#DA3633")  # Red
            util.msg_box('❌ Error', "Identity verification failed.\nUser not recognized.")
            self.mainWindow.after(2000, lambda: self._update_status("Camera Ready", "#238636"))

    def register(self):
        self.registerWindow = tk.Toplevel(self.mainWindow)
        self.registerWindow.title("User Registration")
        self.registerWindow.geometry("1100x850+200+50")
        self.registerWindow.configure(bg='#0D1117')

        # Header
        header = tk.Frame(self.registerWindow, bg='#161B22', height=70)
        header.pack(fill='x')
        tk.Label(header, text="NEW USER REGISTRATION", font=("Segoe UI", 18, "bold"), bg='#161B22', fg='#E6EDF3').pack(pady=20)

        container = tk.Frame(self.registerWindow, bg='#0D1117')
        container.pack(fill='both', expand=True, padx=25, pady=20)

        # Left: Live Preview
        left_side = tk.Frame(container, bg='#0D1117')
        left_side.pack(side='left', fill='both', expand=True, padx=(0, 15))
        
        tk.Label(left_side, text="LIVE CAMERA", font=("Segoe UI", 11, "bold"), bg='#0D1117', fg='#7D8590').pack(anchor='w', pady=(0, 8))
        
        self.reg_webcam_container = tk.Frame(left_side, bg='#161B22', highlightthickness=2, highlightbackground='#30363D')
        self.reg_webcam_container.pack(fill='both', expand=True)
        self.reg_webcam_label = tk.Label(self.reg_webcam_container, bg='#000000')
        self.reg_webcam_label.pack(fill='both', expand=True, padx=3, pady=3)

        # Right: Form
        right_side = tk.Frame(container, bg='#161B22', width=380, highlightthickness=2, highlightbackground='#30363D')
        right_side.pack(side='right', fill='y')
        right_side.pack_propagate(False)

        form_container = tk.Frame(right_side, bg='#161B22')
        form_container.pack(fill='both', expand=True, padx=25, pady=25)

        # Name Input
        tk.Label(form_container, text="FULL NAME", font=("Segoe UI", 10, "bold"), bg='#161B22', fg='#7D8590').pack(anchor='w', pady=(0, 5))
        self.name_entry = tk.Entry(form_container, font=("Segoe UI", 14), bd=0, relief='flat', bg='#0D1117', fg='#E6EDF3', insertbackground='#58A6FF')
        self.name_entry.pack(fill='x', ipady=10, pady=(0, 20))

        # Snapshot Preview
        tk.Label(form_container, text="SNAPSHOT PREVIEW", font=("Segoe UI", 10, "bold"), bg='#161B22', fg='#7D8590').pack(anchor='w', pady=(10, 5))
        self.snapshot_frame = tk.Frame(form_container, bg='#0D1117', width=330, height=248, highlightthickness=2, highlightbackground='#30363D')
        self.snapshot_frame.pack(pady=(0, 20))
        self.snapshot_frame.pack_propagate(False)
        self.snapshot_label = tk.Label(self.snapshot_frame, bg='#000000', text='No snapshot', fg='#7D8590', font=("Segoe UI", 10))
        self.snapshot_label.pack(fill='both', expand=True)
        
        # Buttons
        util.get_button(form_container, '📸 CAPTURE', '#1F6FEB', self._take_snapshot).pack(fill='x', pady=6, ipady=10)
        util.get_button(form_container, '💾 SAVE USER', '#238636', self.accept).pack(fill='x', pady=6, ipady=10)
        util.get_button(form_container, '❌ CANCEL', '#DA3633', self.deny).pack(fill='x', pady=6, ipady=10)

        self.update_reg_preview()

    def update_reg_preview(self):
        if not hasattr(self, 'registerWindow') or not self.registerWindow.winfo_exists():
            return

        if self.most_recent_capture_arr is not None:
            img = cv2.cvtColor(self.most_recent_capture_arr, cv2.COLOR_BGR2RGB)
            img_pil = Image.fromarray(img)
            img_pil.thumbnail((700, 525))
            imgtk = ImageTk.PhotoImage(image=img_pil)
            self.reg_webcam_label.imgtk = imgtk
            self.reg_webcam_label.configure(image=imgtk)
        
        self.registerWindow.after(30, self.update_reg_preview)

    def _take_snapshot(self):
        if self.most_recent_capture_arr is None: return
        self.temp_capture = self.most_recent_capture_arr.copy()
        img = cv2.cvtColor(self.temp_capture, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img)
        img_pil.thumbnail((330, 248))
        imgtk = ImageTk.PhotoImage(image=img_pil)
        self.snapshot_label.imgtk = imgtk
        self.snapshot_label.configure(image=imgtk, text='')

    def accept(self):
        name = self.name_entry.get().strip()
        if not name:
            util.msg_box('⚠️ Error', 'Please enter a name.')
            return
        
        if self.temp_capture is None:
            util.msg_box('⚠️ Error', 'Please capture a photo first.')
            return

        save_path = os.path.join(self.db_dir, f'{name}.jpg')
        cv2.imwrite(save_path, self.temp_capture)

        # Reload DB
        self.known_face_encodings, self.known_face_names = util.load_db(self.db_dir)

        util.msg_box('✅ Complete', f'User {name} has been successfully registered!')
        self.registerWindow.destroy()
        self.temp_capture = None

    def deny(self):
        self.registerWindow.destroy()
        self.temp_capture = None

    def start(self):
        self.mainWindow.mainloop()

if __name__ == "__main__":
    app = App()
    app.start()
