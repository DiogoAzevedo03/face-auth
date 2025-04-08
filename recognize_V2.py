# ============================================
# Real-Time Face Recognition Script (V2)
# Authors: Diogo Azevedo and Letícia Loureiro
# Date: 2025-04-03
# Description:
# Live preview with real-time recognition using PiCamera2,
# displaying the recognized person's name and a rectangle around the face.
# ============================================

import cv2
import os
import numpy as np
import pickle
from picamera2 import Picamera2
from time import sleep
import tflite_runtime.interpreter as tflite

# === Configuration ===

# Load TFLite face embedding model
interpreter = tflite.Interpreter(model_path="models/mobilefacenet.tflite")
interpreter.allocate_tensors()

input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

# Embeddings directory and recognition threshold
EMBEDDINGS_DIR = "embeddings/"
THRESHOLD = 0.8  # More strict than V1

# === Functions ===

def preprocess_image(image):
    if image.shape[2] == 4:
        image = cv2.cvtColor(image, cv2.COLOR_RGBA2RGB)
    resized = cv2.resize(image, (112, 112))
    normalized = resized.astype('float32') / 255.0
    return np.expand_dims(normalized, axis=0)

def get_embedding(image):
    input_data = preprocess_image(image)
    interpreter.set_tensor(input_details[0]['index'], input_data)
    interpreter.invoke()
    return interpreter.get_tensor(output_details[0]['index'])[0]

def load_known_embeddings():
    known = {}
    for file in os.listdir(EMBEDDINGS_DIR):
        if file.endswith(".pkl"):
            name = file.split("_")[0]
            path = os.path.join(EMBEDDINGS_DIR, file)
            with open(path, "rb") as f:
                embedding = pickle.load(f)
                if name not in known:
                    known[name] = []
                known[name].append(embedding)
    return known

def recognize_face(embedding, known_embeddings):
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
    print("🎥 Starting Face Recognition V2...")
    picam2 = Picamera2()
    picam2.configure(picam2.create_preview_configuration(main={"size": (640, 480)}))
    picam2.start()
    sleep(2)

    known_embeddings = load_known_embeddings()

    while True:
        frame = picam2.capture_array()

        # For simplicity, use entire frame as "face"
        face_embedding = get_embedding(frame)
        name, dist = recognize_face(face_embedding, known_embeddings)

        # Draw rectangle and name
        display_frame = frame.copy()
        color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)
        cv2.rectangle(display_frame, (50, 50), (590, 430), color, 2)
        label = f"{name} ({dist:.2f})" if dist else "Unknown"
        cv2.putText(display_frame, label, (60, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

        # Show the live frame
        cv2.imshow("Face Recognition - V2", display_frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cv2.destroyAllWindows()
    picam2.close()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Recognition stopped by user.")
