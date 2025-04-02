# ============================================
# Register User Script with Picamera2
# Author: Letícia Loureiro & Diogo Azevedo
# Date: 2025-04-02
# Description:
# This script captures a face using Picamera2,
# generates an embedding using MobileFaceNet (TFLite model),
# and saves the result as a .pkl file for future recognition.
# ============================================

import os
import cv2
import time
import numpy as np
import pickle
from picamera2 import Picamera2
import tflite_runtime.interpreter as tflite

# === CONFIG ===
MODEL_PATH = "models/mobilefacenet.tflite"
SAVE_PATH = "embeddings/"
os.makedirs(SAVE_PATH, exist_ok=True)

# === LOAD MODEL ===
interpreter = tflite.Interpreter(model_path=MODEL_PATH)
interpreter.allocate_tensors()
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

def get_embedding(face_img):
    face_img = cv2.resize(face_img, (112, 112))
    face_img = cv2.cvtColor(face_img, cv2.COLOR_BGR2RGB)
    face_img = face_img.astype("float32") / 255.0
    face_img = np.expand_dims(face_img, axis=0)
    interpreter.set_tensor(input_details[0]['index'], face_img)
    interpreter.invoke()
    embedding = interpreter.get_tensor(output_details[0]['index'])
    return embedding[0]

# === INIT CAMERA ===
picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"size": (640, 480)}))
picam2.start()
time.sleep(2)

print("[INFO] Camera running. Focus the camera window and press:")
print("       's' to save embedding")
print("       'q' to quit")

# === LIVE LOOP ===
while True:
    frame = picam2.capture_array("main")
    cv2.imshow("Live Camera - Press 's' to Save, 'q' to Quit", frame)

    key = cv2.waitKey(1) & 0xFF

    if key == ord('s'):
        cv2.destroyWindow("Live Camera - Press 's' to Save, 'q' to Quit")
        username = input("Enter username to save embedding: ").strip().lower()
        embedding = get_embedding(frame)
        filename = os.path.join(SAVE_PATH, f"{username}.pkl")
        with open(filename, "wb") as f:
            pickle.dump(embedding, f)
        print(f"[SUCCESS] Embedding saved as: {filename}")
        break

    elif key == ord('q'):
        print("[INFO] Exiting without saving.")
        break

# === CLEANUP ===
cv2.destroyAllWindows()
picam2.close()

