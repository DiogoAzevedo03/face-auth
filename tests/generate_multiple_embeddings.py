# ============================================
# Automatic Face Embedding Generator v3
# Authors: Diogo Azevedo & Letícia Loureiro
# Date: 2025-04-04
# Description:
# Captures live camera feed, detects faces,
# extracts embeddings from faces only,
# and saves them organized by user folder.
# Allows Wipe or Append mode.
# ============================================

import cv2
import os
import numpy as np
import pickle
from picamera2 import Picamera2
import time
import shutil
import tflite_runtime.interpreter as tflite
import mediapipe as mp


# === CONFIGURATION ===
MODEL_PATH = "models/mobilefacenet.tflite"
SAVE_BASE_PATH = "embeddings/"
CAPTURE_INTERVAL = 1  # seconds

os.makedirs(SAVE_BASE_PATH, exist_ok=True)

# === LOAD MODELS ===
interpreter = tflite.Interpreter(model_path=MODEL_PATH)
interpreter.allocate_tensors()
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

# Inicializar MediaPipe Face Detection
mp_face_detection = mp.solutions.face_detection
face_detection = mp_face_detection.FaceDetection(model_selection=0,min_detection_confidence=0.5)


# === HELPER FUNCTIONS ===

def preprocess_face(face_img):
    """Preprocesses the face image for the MobileFaceNet model."""
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
    print("Starting automatic face embedding generator...")

    # Initialize camera
    picam2 = Picamera2()
    picam2.start()
    time.sleep(2)

    username = input("Enter username: ").strip().lower()
    user_dir = os.path.join(SAVE_BASE_PATH, username)

    # Ask for Wipe or Append
    if os.path.exists(user_dir):
        choice = input(f"User '{username}' already exists. [W]ipe or [A]ppend? ").strip().lower()
        if choice == "w":
            print("Wiping existing embeddings...")
            shutil.rmtree(user_dir)
            os.makedirs(user_dir)
            counter = 0
        else:
            print("Appending to existing embeddings...")
            existing_files = [f for f in os.listdir(user_dir) if f.endswith(".pkl")]
            counter = len(existing_files)
    else:
        os.makedirs(user_dir)
        counter = 0

    # Novo: perguntar quantos novos embeddings quer gerar
    num_to_generate = int(input("How many new embeddings do you want to capture? "))

    last_capture_time = 0

    print("Get ready! The system will start capturing automatically...")

    end_counter = counter + num_to_generate  # Nova meta

    while counter < end_counter:
        frame = picam2.capture_array()

        frame = cv2.flip(frame, 1)  # Mirror the frame for natural preview

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Detect faces with MediaPipe
        results = face_detection.process(rgb_frame)

        faces = []

        if results.detections:
            for detection in results.detections:
                bboxC = detection.location_data.relative_bounding_box
                ih, iw, _ = frame.shape
                x = int(bboxC.xmin * iw)
                y = int(bboxC.ymin * ih)
                w = int(bboxC.width * iw)
                h = int(bboxC.height * ih)
                faces.append((x, y, w, h))


        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

        cv2.putText(frame, f"Captured: {counter}/{end_counter}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

        cv2.imshow("Live Camera - Face Detection", frame)

        if len(faces) > 0 and time.time() - last_capture_time > CAPTURE_INTERVAL:
            (x, y, w, h) = faces[0]
            # Proteger limites da imagem
            ih, iw, _ = frame.shape
            x = max(0, x)
            y = max(0, y)
            w = min(w, iw - x)
            h = min(h, ih - y)

            face_crop = frame[y:y+h, x:x+w]

            if face_crop.size == 0:
                print("Invalid face crop detected, skipping...")
                continue

            embedding = get_embedding(face_crop)

            filename = os.path.join(user_dir, f"{username}_{counter:02d}.pkl")
            with open(filename, "wb") as f:
                pickle.dump(embedding, f)

            print(f"Saved embedding: {filename}")
            counter += 1
            last_capture_time = time.time()

        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("User requested exit.")
            break

    print("Finished capturing embeddings!")
    cv2.destroyAllWindows()
    picam2.close()


# === PROTECT EXECUTION ===

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nProgram interrupted by user.")
        cv2.destroyAllWindows()
