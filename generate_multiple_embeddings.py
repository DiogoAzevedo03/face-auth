# ============================================
# Generate Multiple Embeddings Script
# Authors: Letícia Loureiro & Diogo Azevedo
# Date: 2025-04-03
# Description:
# This script captures 20 face embeddings automatically (1 per second)
# and saves them as individual .pkl files.
# ============================================

import os
import cv2
import time
import numpy as np
import pickle
from picamera2 import Picamera2
import tflite_runtime.interpreter as tflite

# === CONFIGURATION ===
MODEL_PATH = "models/mobilefacenet.tflite"
SAVE_PATH = "embeddings/"
NUM_EMBEDDINGS = 20            # How many embeddings to capture
CAPTURE_INTERVAL = 1           # Seconds between captures
os.makedirs(SAVE_PATH, exist_ok=True)

# === LOAD TFLITE MODEL ===
interpreter = tflite.Interpreter(model_path=MODEL_PATH)
interpreter.allocate_tensors()
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

def get_embedding(face_img):
    """Preprocess and generate face embedding"""
    face_img = cv2.resize(face_img, (112, 112))
    face_img = cv2.cvtColor(face_img, cv2.COLOR_BGR2RGB)
    face_img = face_img.astype("float32") / 255.0
    face_img = np.expand_dims(face_img, axis=0)
    
    interpreter.set_tensor(input_details[0]['index'], face_img)
    interpreter.invoke()
    embedding = interpreter.get_tensor(output_details[0]['index'])
    return embedding[0]

# === START CAMERA ===
picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"size": (640, 480)}))
picam2.start()
time.sleep(2)  # Camera warm-up

# === ASK FOR USERNAME ===
username = input("Enter username to save embeddings (e.g., diogo, leticia): ").strip().lower()

print(f"[INFO] Starting capture for {username}. Move slightly between captures!")

# === CAPTURE LOOP ===
for i in range(1, NUM_EMBEDDINGS + 1):
    frame = picam2.capture_array("main")
    embedding = get_embedding(frame)

    filename = os.path.join(SAVE_PATH, f"{username}_{i:02d}.pkl")
    with open(filename, "wb") as f:
        pickle.dump(embedding, f)

    print(f"[SUCCESS] Saved {filename}")
    time.sleep(CAPTURE_INTERVAL)

print(f"✅ All {NUM_EMBEDDINGS} embeddings saved for {username}!")
picam2.close()
