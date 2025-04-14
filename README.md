# FaceAuth - Face Embedding Generator

 - author branches:
   - diogo
   - leticia 

---

 **Overview**  
This project is part of the FaceAuth system, developed to provide facial recognition authentication on a Raspberry Pi 5.  
It consists of two main scripts:

- **generate_multiple_embeddings.py**:  
  Captures faces from the camera, generates embeddings using a MobileFaceNet model (TensorFlow Lite), and saves them for future recognition.

- **recognize.py**:  
  Detects faces in real time and identifies users by comparing live embeddings with the stored ones.

Face detection is performed using **MediaPipe** for improved precision and performance.

---

 **How to Run**

### 1. Install Required Dependencies

Make sure your Raspberry Pi camera is properly connected and configured.

Then, install the required Python packages:

```bash
pip install -r requirements.txt
```

### 2. Generate Face Embeddings
To capture embeddings for a new user:

```bash
python3 generate_multiple_embeddings.py
```
Follow the instructions in the terminal:

Enter a username.

Choose whether to wipe or append embeddings if the user already exists.

Specify how many embeddings you want to capture.

The system will automatically detect your face and save embeddings to the embeddings/ folder.

### 3. Recognize Faces in Real Time
To start real-time face recognition:

```bash
python3 recognize.py
```
The system will detect faces live:

Recognized users will have their names displayed on the screen.

Unknown faces will be labeled as "Unknown".

Press 'q' at any time to exit.

---

 **Technologies Used**

- **TensorFlow Lite** – for generating 128-dimensional face embeddings (using MobileFaceNet model).
- **MediaPipe** – for accurate and fast face detection.
- **OpenCV** – for image processing and visualization.
- **Picamera2** – for interfacing with the Raspberry Pi Camera.
- **Python 3.11** – development language.


---

 File Structure

|File	                            |Description |
|-----------------------------------|------------|
|generate_multiple_embeddings.py	|Captures faces and generates embeddings, saving them per user.|
|recognize.py	                    |Recognizes faces in real time by comparing live embeddings with stored ones.|
|requirements.txt	                |Lists all required Python packages.|
|models/mobilefacenet.tflite	    |Pre-trained MobileFaceNet model used for embedding generation.|
|embeddings/	                    |Directory where all user embeddings are stored.|
|README.md	                        |This documentation file.|

---

 Why Embeddings Are Needed
Face embeddings are compact numerical representations of faces.
They allow the system to compare and recognize users efficiently without storing raw images, improving speed, security, and privacy.