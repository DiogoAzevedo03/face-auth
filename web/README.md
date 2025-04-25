# FaceAuth Web - Facial Recognition Authentication System

## Overview
FaceAuth Web is a lightweight, web-based authentication platform built with Flask that leverages facial recognition for secure login. It provides an administrative dashboard, user management, face embedding capture, and real-time login via camera using TensorFlow Lite and MediaPipe.

---

## Features
- **Manual and Facial Login**
- **User Creation with Role Assignment** (admin / normal)
- **Real-time Face Detection and Embedding Capture**
- **TFLite Face Embedding Model (MobileFaceNet)**
- **JSON-based User Database**
- **Embedding Storage using Pickle**
- **Automatic Embedding Cleanup on User Removal**

---



---

## Installation
### 1. Requirements
- Python 3.9+
- Raspberry Pi OS / Linux preferred (uses `picamera2`)

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

> For Raspberry Pi, use `picamera2` via `sudo apt install python3-picamera2`

### 3. Model Setup
Place the `mobilefacenet.tflite` model inside the `models/` directory.

---

## Running the App
```bash
cd web
python3 app.py
```
App will run on `http://0.0.0.0:5000`

---

## How It Works
### Authentication Flow
1. **Face Login:** Captures webcam frame → Detects face → Generates embedding → Compares with known embeddings → Logs in
2. **Manual Login:** Form-based login with email/password stored in `users.json`

### Embedding Capture (Admin Only)
- Admin creates a new user via the dashboard.
- System captures face images, detects faces, and generates embeddings via `MobileFaceNet`.
- Embeddings are saved as `.pkl` in the user’s folder inside `embeddings/`.

---

## Security Notes
- Passwords are stored in plaintext in `users.json`.
- No HTTPS or production server config — meant for prototype/demo.

---

## Credits
**Developed by:** Diogo Azevedo & Letícia Loureiro  
**Instituto Politécnico de Viana do Castelo**  
**Project:** FaceAuth - Facial Recognition Authentication System