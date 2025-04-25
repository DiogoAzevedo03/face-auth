
# FaceAuth - Facial Recognition Authentication System

##  Overview

FaceAuth is a facial recognition-based authentication system designed to work seamlessly on a **Raspberry Pi 5** using **TensorFlow Lite** and **MediaPipe**.  
It supports real-time face detection, embedding generation, and user recognition for secure logins via a web-based interface.

This project is organized into modules for:
- Capturing and embedding faces
- Real-time face recognition
- Web-based login interface (Flask)

---

## Project Structure

```
face-auth/
│
├── embeddings/                  # Where all face embeddings are saved (.pkl)
├── models/
│   └── mobilefacenet.tflite    # Pre-trained TFLite face embedding model
├── tests/                      # Scripts for camera and embedding tests
│   ├── generate_multiple_embeddings.py
│   ├── recognize.py
│   └── test_camera.py
├── tools/                      # Tools to compare and inspect embeddings
│   ├── check_embedding.py
│   └── compare_embeddings.py
├── web/                        # Flask web interface (login, dashboard, etc.)
│   ├── static/                 # CSS styling
│   ├── templates/              # HTML pages (Jinja2 templates)
│   ├── app.py                  # Flask backend
│   ├── users.json              # Stores users, roles and passwords
│   └── README.md               # Web app documentation
├── recognize_m.py             # FaceRecognizer class (used by Flask backend)
├── generate_multiple_embeddings_m.py # EmbeddingGenerator class (used by Flask backend)
├── requirements.txt           # Required Python packages
└── README.md                  # This file
```

---

## Key Functionalities

- Face detection using **MediaPipe**
- Embedding extraction using **MobileFaceNet (TFLite)**
- User authentication via:
  - Manual login (email + password)
  - Facial recognition
- Embeddings stored as `.pkl` in structured folders
- Web login interface with role-based dashboards

---

## Installation

1. Clone the repository:
```bash
git clone https://github.com/DiogoAzevedo03/face-auth.git
cd face-auth
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

> Ensure that your **Raspberry Pi Camera** is enabled and connected.

---

## Running the Web App

Navigate into the web folder and start the Flask app:
```bash
cd web
python3 app.py
```
App will be accessible via: `http://0.0.0.0:5000`

---

## Test Scripts

For testing on Raspberry Pi:

- **Test Camera:**
```bash
python3 tests/test_camera.py
```

- **Capture Embeddings:**
```bash
python3 tests/generate_multiple_embeddings.py
```

- **Real-time Recognition:**
```bash
python3 tests/recognize.py
```

---

## Modules Description

### `generate_multiple_embeddings_m.py`
- Captures camera input and detects faces
- Generates face embeddings
- Saves embeddings in `embeddings/<user>/` folder
- Used internally by the web app (admin user creation)

### `recognize_m.py`
- Loads embeddings from disk
- Detects live faces and compares to known users
- Returns matched identity or "Unknown"
- Used by Flask backend to handle face login

---

## Dependencies

Listed in `requirements.txt`:
- opencv-python
- mediapipe
- numpy
- tflite-runtime
- picamera2
- Pillow

Install with:
```bash
pip install -r requirements.txt
```

---

## Notes

- Passwords in `users.json` are stored in plaintext (for demo use only)
- Not optimized for production — no HTTPS or secure user handling
- Recommended: run on **Raspberry Pi OS** with Python 3.9+

---

## Authors

- Diogo Azevedo  
- Letícia Loureiro  
- Instituto Politécnico de Viana do Castelo 
