# Face Recognition Attendance System 

A real time facial recognition attendance system designed for face detection and recognition, suitable for small to medium-scale attendance tracking.


## Key Features
- **Real-time Recognition**: Processes webcam feeds at high FPS with optimized recognition cycles.
- **Local Persistence**: Stores user face data and attendance logs locally (no cloud required).
- **Features**: Recent activity log, tooltips, and real-time status updates.

## Tech Stack
- **Python 3.10+**
- **OpenCV**: Camera feed processing and image handling.
- **face_recognition (dlib)**: deep learning model for face encoding.
- **Tkinter (PIL/Pillow)**: Custom-styled GUI.
- **NumPy**: Efficient numerical operations for face distance calculations.

## Quick Start

### 1. Prerequisites
- **Visual Studio Build Tools**: Required for `dlib` compilation (C++ CMake).
- **Webcam**: A functional webcam for live detection.

### 2. Setup Environment
We recommend using a virtual environment.

```bash
# Create venv
python -m venv venv

# Activate venv (Windows)
.\venv\Scripts\activate

# Activate venv (macOS/Linux)
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Application
```bash
python src/main.py
```

## Usage Guide
1. **Registration**: Click **➕ NEW USER**, enter a name, capture a photo, and save.
2. **Attendance**: Simply stand in front of the camera and click **🔐 CLOCK IN**.
3. **Logs**: View recent activity directly in the interface or check `log.txt` in the root directory.

## Project Structure
```text
├── db/              # Stores registered user face images (.jpg)
├── src/             # Core application source code
│   ├── main.py      # Entry point and UI logic
│   └── util.py      # Vision utilities and UI components
├── requirements.txt # Project dependencies
└── log.txt          # Attendance records (generated)
```

