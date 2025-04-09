# ============================================
# Automatic Face Embedding Generator v2
# Authors: Diogo Azevedo & Letícia Loureiro
# Date: 2025-04-03
# Description:
# Captures live camera feed, detects faces,
# extracts embeddings from faces only,
# and automatically saves 20 embeddings per user.
# ============================================

import cv2
import os
import numpy as np
import pickle
from picamera2 import Picamera2
import time
import tflite_runtime.interpreter as tflite

# === CONFIGURATION ===
MODEL_PATH = "models/mobilefacenet.tflite"
CASCADE_PATH = "cascades/haarcascade_frontalface_default.xml"
SAVE_PATH = "embeddings/"
NUM_EMBEDDINGS = 60  # Number of embeddings to capture per user
CAPTURE_INTERVAL = 1  # Seconds between each capture

os.makedirs(SAVE_PATH, exist_ok=True)  # Create embeddings folder if it doesn't exist

# === LOAD MODELS ===
interpreter = tflite.Interpreter(model_path=MODEL_PATH)
interpreter.allocate_tensors()
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

face_cascade = cv2.CascadeClassifier(CASCADE_PATH)

# === HELPER FUNCTIONS ===

def preprocess_face(face_img):
    """Preprocesses face image for the MobileFaceNet model."""
    face_img = cv2.resize(face_img, (112, 112))
    face_img = cv2.cvtColor(face_img, cv2.COLOR_BGR2RGB)
    face_img = face_img.astype("float32") / 255.0
    face_img = np.expand_dims(face_img, axis=0)
    return face_img

def get_embedding(face_img):
    """Extracts the face embedding using the TFLite model."""
    input_data = preprocess_face(face_img)
    interpreter.set_tensor(input_details[0]['index'], input_data)
    interpreter.invoke()
    embedding = interpreter.get_tensor(output_details[0]['index'])[0]
    return embedding

# === MAIN FUNCTION ===

def main():
    print("🚀 Starting automatic face embedding generator...")

    # Initialize camera
    picam2 = Picamera2()
    picam2.start()
    time.sleep(2)  # Allow the camera to stabilize

    username = input("Enter username: ").strip().lower()
    counter = 40 # Captured embeddings counter
    last_capture_time = 0

    print("📸 Get ready! The system will start capturing automatically...")

    while counter < NUM_EMBEDDINGS:
        frame = picam2.capture_array()

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # Haar needs grayscale
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

        # Draw rectangles around detected faces
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

        cv2.putText(frame, f"Captured: {counter}/{NUM_EMBEDDINGS}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

        cv2.imshow("Live Camera - Face Detection", frame)

        # Capture embeddings if at least one face is detected
        if len(faces) > 0 and time.time() - last_capture_time > CAPTURE_INTERVAL:
            (x, y, w, h) = faces[0]  # Use the first detected face
            face_crop = frame[y:y+h, x:x+w]
            embedding = get_embedding(face_crop)

            filename = os.path.join(SAVE_PATH, f"{username}_{counter:02d}.pkl")
            with open(filename, "wb") as f:
                pickle.dump(embedding, f)

            print(f"✅ Saved embedding: {filename}")
            counter += 1
            last_capture_time = time.time()

        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("🛑 User requested exit.")
            break

    print("🎯 Finished capturing embeddings!")
    cv2.destroyAllWindows()
    picam2.close()

# === EXECUTION PROTECTION ===

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Program interrupted by user.")
        cv2.destroyAllWindows()
