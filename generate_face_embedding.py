# ============================================
# Register User Script with Picamera2
# Authors: Letícia Loureiro & Diogo Azevedo
# Date: 2025-04-02
# Description:
# This script captures a face using the Raspberry Pi camera (Picamera2),
# generates a face embedding using the MobileFaceNet model in TFLite format,
# and saves the embedding as a .pkl file in the "embeddings/" folder.
# This data can later be used for real-time facial recognition.
# ============================================

import os                   # For creating folders and working with file paths
import cv2                  # OpenCV: used to display the live camera preview
import time                 # To introduce delays (e.g., camera warm-up)
import numpy as np          # To handle image tensors and array operations
import pickle               # To save/load Python objects (.pkl files)
from picamera2 import Picamera2  # Library to control the Raspberry Pi camera
import tflite_runtime.interpreter as tflite  # Lightweight TFLite interpreter for embedded devices

# === CONFIGURATION ===
MODEL_PATH = "models/mobilefacenet.tflite"   # Path to the pre-trained face embedding model
SAVE_PATH = "embeddings/"                    # Folder to store the user embeddings (.pkl)
os.makedirs(SAVE_PATH, exist_ok=True)        # Create the folder if it doesn't exist

# === LOAD TFLITE MODEL ===
interpreter = tflite.Interpreter(model_path=MODEL_PATH)  # Load TFLite model
interpreter.allocate_tensors()                            # Allocate memory and prepare model
input_details = interpreter.get_input_details()           # Input metadata (shape, index)
output_details = interpreter.get_output_details()         # Output metadata (shape, index)

# === EMBEDDING GENERATOR FUNCTION ===
def get_embedding(face_img):
    """
    Preprocesses a face image and generates an embedding using MobileFaceNet.

    Parameters:
    face_img (np.array): Captured face image from the camera.

    Returns:
    np.array: 1D embedding vector representing the face.
    """
    face_img = cv2.resize(face_img, (112, 112))                 # Resize to expected input size
    face_img = cv2.cvtColor(face_img, cv2.COLOR_BGR2RGB)        # Convert from BGR to RGB
    face_img = face_img.astype("float32") / 255.0               # Normalize pixel values to [0, 1]
    face_img = np.expand_dims(face_img, axis=0)                 # Add batch dimension (1, 112, 112, 3)

    interpreter.set_tensor(input_details[0]['index'], face_img)  # Load input tensor
    interpreter.invoke()                                          # Run inference
    embedding = interpreter.get_tensor(output_details[0]['index'])  # Extract output
    return embedding[0]                                           # Return 1D embedding vector

# === INITIALIZE CAMERA ===
picam2 = Picamera2()  # Create a camera object
# Configure the preview stream (resolution 640x480)
picam2.configure(picam2.create_preview_configuration(main={"size": (640, 480)}))
picam2.start()        # Start the camera
time.sleep(2)         # Give the camera time to adjust and initialize

# === USER INSTRUCTIONS ===
print("[INFO] Camera is running.")
print("[INFO] Focus the camera window and press:")
print("        's' to save embedding")
print("        'q' to quit without saving")

# === MAIN LOOP ===
while True:
    # Capture a frame from the live camera feed
    frame = picam2.capture_array("main")

    # Show the live camera preview window
    cv2.imshow("Live Camera - Press 's' to Save, 'q' to Quit", frame)

    # Check if a key has been pressed
    key = cv2.waitKey(1) & 0xFF

    if key == ord('s'):
        # Close the preview window
        cv2.destroyWindow("Live Camera - Press 's' to Save, 'q' to Quit")

        # Ask the user for their name (to name the file)
        username = input("Enter username to save embedding: ").strip().lower()

        # Generate the embedding from the current frame
        embedding = get_embedding(frame)

        # Save the embedding as a .pkl file
        filename = os.path.join(SAVE_PATH, f"{username}.pkl")
        with open(filename, "wb") as f:
            pickle.dump(embedding, f)

        print(f"[SUCCESS] Embedding saved at: {filename}")
        break  # Exit the loop after saving

    elif key == ord('q'):
        print("[INFO] Exit requested by user. No embedding saved.")
        break  # Exit the loop without saving

# === CLEAN UP ===
cv2.destroyAllWindows()  # Close any OpenCV windows
picam2.close()           # Release the camera
