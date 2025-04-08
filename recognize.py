# ============================================
# Real-Time Face Recognition Script
# Authors: Diogo Azevedo and Letícia Loureiro
# Date: 2025-04-03
# Description:
# Captures images from the camera, extracts face embeddings,
# and compares them with stored embeddings (.pkl) to identify the user.
# ============================================

import cv2                  # OpenCV for image processing
import os                   # File system operations
import numpy as np          # Numerical operations (vectors, matrices)
import pickle               # Save/load Python objects (.pkl files)
from picamera2 import Picamera2  # Library to control Raspberry Pi camera
from time import sleep      # To introduce small execution delays
import tflite_runtime.interpreter as tflite  # Lightweight TFLite interpreter for embedded devices

# === General Configuration ===

# Load the TFLite face embedding model
interpreter = tflite.Interpreter(model_path="models/mobilefacenet.tflite")
interpreter.allocate_tensors()  # Allocate memory for tensors

# Get input and output tensor details
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

# Directory containing registered user embeddings
EMBEDDINGS_DIR = "embeddings/"

# Distance threshold to consider two faces as the same person
THRESHOLD = 1.0

# === Helper Functions ===

def preprocess_image(image):
    """
    Preprocesses the captured image:
    - Resize to 112x112 (expected by the model)
    - Convert RGBA to RGB if necessary
    - Normalize pixel values to [0, 1]
    """
    if image.shape[2] == 4:
        image = cv2.cvtColor(image, cv2.COLOR_RGBA2RGB)  # Convert images with 4 channels (RGBA)
    resized = cv2.resize(image, (112, 112))
    normalized = resized.astype('float32') / 255.0
    return np.expand_dims(normalized, axis=0)  # Add batch dimension

def get_embedding(image):
    """
    Extracts the facial embedding from the captured image using the TFLite model.
    """
    input_data = preprocess_image(image)
    interpreter.set_tensor(input_details[0]['index'], input_data)
    interpreter.invoke()
    embedding = interpreter.get_tensor(output_details[0]['index'])[0]
    return embedding  # 1D feature vector (embedding)

def load_known_embeddings():
    """
    Loads all saved embeddings from the embeddings folder and
    groups them by user.
    Each user can have multiple embeddings associated.
    """
    known = {}
    for file in os.listdir(EMBEDDINGS_DIR):
        if file.endswith(".pkl"):
            name = file.split("_")[0]  # Extract the user name (before "_")
            path = os.path.join(EMBEDDINGS_DIR, file)
            with open(path, "rb") as f:
                embedding = pickle.load(f)
                if name not in known:
                    known[name] = []
                known[name].append(embedding)
    return known

def recognize_face(embedding, known_embeddings):
    """
    Compares the extracted embedding with all known embeddings.
    Returns the user name with the smallest distance, if within the threshold.
    """
    best_match = "Unknown"
    best_distance = float('inf')

    for name, embeddings in known_embeddings.items():
        for known_emb in embeddings:
            distance = np.linalg.norm(embedding - known_emb)  # Euclidean distance
            if distance < best_distance:
                best_distance = distance
                best_match = name

    if best_distance < THRESHOLD:
        return best_match, best_distance
    else:
        return "Unknown", None

# === Main Function ===

def main():
    print("🎥 Starting real-time face recognition...")

    # Initialize camera
    picam2 = Picamera2()
    picam2.start()
    sleep(2)  # Wait 2 seconds for the camera to stabilize

    # Load all known embeddings
    known_embeddings = load_known_embeddings()

    # Main loop: capture frames and recognize faces
    while True:
        frame = picam2.capture_array()  # Capture a frame from the camera
        face_embedding = get_embedding(frame)  # Extract the embedding
        name, dist = recognize_face(face_embedding, known_embeddings)  # Recognize the face

        if name != "Unknown":
            print(f"✅ {name} recognized (distance: {dist:.4f})")
        else:
            print("❌ Face not recognized.")

        sleep(2)  # Small delay to avoid system overload

# === Protection to Stop the Program ===

try:
    main()
except KeyboardInterrupt:
    print("\n🛑 Recognition stopped by user.")
