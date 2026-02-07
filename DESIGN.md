# Technical Design Document - Attendance System

## 🎯 Project Overview
The goal was to create a robust, desktop-based attendance system that uses biometric data (facial recognition) instead of traditional methods. Focus was placed on **User Experience (UX)** and **Performance**.

## 🏗️ System Architecture

### 1. Face Recognition Pipeline
The system uses a tiered approach to balance accuracy and performance:
- **Detection**: Uses the HOG (Histogram of Oriented Gradients) model for fast face localization.
- **Encoding**: Generates a 128-dimension vector representing the unique features of a face.
- **Matching**: Uses Euclidean distance to compare live encodings against the local database with a strict tolerance threshold (0.6).

### 2. Optimization Techniques
To ensure a smooth UI experience (prevents the GUI from freezing), we implemented:
- **Frame Skipping**: Heavy recognition logic runs every 45 frames (approx. every 1.5 seconds) while the UI continues to refresh the video feed at 30 FPS.
- **Image Resizing**: recognition is performed on a downscaled version (1/5th) of the frame to reduce CPU load significantly.

## 🛠️ Engineering Trade-offs

### File-based Storage vs. Database
- **Decision**: Used local JPEG storage in a `db/` folder.
- **Rationale**: For a resume project, this simplifies deployment and allows recruiters to easily "see" the data. It also allows the `face_recognition` library to load images directly for on-the-fly encoding.
- **Future Work**: Migrating to a vector database (like Pinecone or ChromaDB) would be the next step for scaling to thousands of users.

### Python/Tkinter vs. Modern Web App
- **Decision**: Python desktop app.
- **Rationale**: Direct hardware access to the webcam and local filesystem is much more efficient in a native environment compared to a browser-based WASM approach for real-time intensive tasks.

## 🎨 UI Design Philosophy
The UI follows a **Modern Developer Aesthetic**:
- **Palette**: Dark backgrounds (`#0D1117`) with high-contrast accent colors (`#58A6FF` for primary actions).
- **Feedback**: Immediate visual feedback through a status indicator (Orange → Busy, Green → Ready, Red → Error).
- **Micro-interactions**: Subtle hover state changes on buttons and tooltips for better discoverability.

## 🛡️ Privacy & Security
- All face encodings are processed locally.
- No data is sent to external APIs or cloud providers.
- Real-time logging ensures an audit trail of all entry attempts.
