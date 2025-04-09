# ============================================
# Real-Time Face Detection and Recognition
# Authors: Diogo Azevedo and Letícia Loureiro
# Date: 2025-04-03
# Description:
# Detects faces in real-time and recognizes users.
# ============================================

import cv2
import os
import numpy as np
import pickle
from picamera2 import Picamera2
from time import sleep
import tflite_runtime.interpreter as tflite

# === Configuration ===

EMBEDDINGS_DIR = "embeddings/"
THRESHOLD = 0.8  # Lowered for better precision
CASCADE_PATH = "cascades/haarcascade_frontalface_default.xml"  # Path to Haar Cascade

# Load Haar Cascade for face detection
face_cascade = cv2.CascadeClassifier(CASCADE_PATH)

# Load TFLite face embedding model
interpreter = tflite.Interpreter(model_path="models/mobilefacenet.tflite")
interpreter.allocate_tensors()

input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

# === Helper Functions ===

def preprocess_image(image):
    """Preprocess the face image: resize and normalize."""
    if image.shape[2] == 4:
        image = cv2.cvtColor(image, cv2.COLOR_RGBA2RGB)
    resized = cv2.resize(image, (112, 112))
    normalized = resized.astype('float32') / 255.0
    return np.expand_dims(normalized, axis=0)

def get_embedding(image):
    """Extract face embedding from preprocessed image."""
    input_data = preprocess_image(image)
    interpreter.set_tensor(input_details[0]['index'], input_data)
    interpreter.invoke()
    embedding = interpreter.get_tensor(output_details[0]['index'])[0]
    return embedding

def load_known_embeddings():
    """Load all saved embeddings grouped by user (supporting subfolders)."""
    known = {}
    for user_folder in os.listdir(EMBEDDINGS_DIR):
        user_path = os.path.join(EMBEDDINGS_DIR, user_folder)
        if os.path.isdir(user_path):
            for file in os.listdir(user_path):
                if file.endswith(".pkl"):
                    path = os.path.join(user_path, file)
                    with open(path, "rb") as f:
                        embedding = pickle.load(f)
                        if user_folder not in known:
                            known[user_folder] = []
                        known[user_folder].append(embedding)
    return known


def recognize_face(embedding, known_embeddings):
    """Compare face embedding with known users and return best match."""
    best_match = "Unknown"
    best_distance = float('inf')

    for name, embeddings in known_embeddings.items():
        for known_emb in embeddings:
            distance = np.linalg.norm(embedding - known_emb)
            if distance < best_distance:
                best_distance = distance
                best_match = name

    if best_distance < THRESHOLD:
        return best_match, best_distance
    else:
        return "Unknown", None

# === Main ===

def main():
    print("🎥 Starting real-time face detection and recognition...")

    # Initialize camera
    picam2 = Picamera2()
    picam2.start()
    sleep(2)

    known_embeddings = load_known_embeddings()

    while True:
        frame = picam2.capture_array()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detect faces
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(60, 60))

        for (x, y, w, h) in faces:
            # Extract the face ROI
            face = frame[y:y+h, x:x+w]

            # Recognize the face
            face_embedding = get_embedding(face)
            name, dist = recognize_face(face_embedding, known_embeddings)

            # Draw rectangle around face
            color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)
            cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)

            # Put name text above the rectangle
            text = f"{name} ({dist:.2f})" if name != "Unknown" else "Unknown"
            cv2.putText(frame, text, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

        # Show the frame
        cv2.imshow("Face Recognition", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()
    picam2.close()

# === Protect Execution ===

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Recognition stopped by user.")
