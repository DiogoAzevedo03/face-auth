# ============================================
# Real-Time Face Detection and Recognition
# File: recognize_m.py
# Authors: Diogo Azevedo and Letícia Loureiro
# Date: 2025-04-15
#
# Description:
# This script defines the FaceRecognizer class, which is responsible for:
# - Loading pre-generated face embeddings from the 'embeddings/' directory.
# - Using the MobileFaceNet TFLite model to generate embeddings from input images.
# - Detecting faces in real-time using MediaPipe.
# - Comparing the embeddings of detected faces with known embeddings to identify users.
#
# Usage:
# This file is intended to be imported and used within other scripts,
# such as the main GUI file (main_menu_2.py).
# ============================================

import cv2  # OpenCV for image processing
import numpy as np  # NumPy for array operations
import os  # OS module to interact with the filesystem
import pickle  # For loading saved face embeddings
from picamera2 import Picamera2  # Library for accessing the Raspberry Pi camera
import tflite_runtime.interpreter as tflite  # TensorFlow Lite runtime for running lightweight models
import mediapipe as mp  # MediaPipe for face detection
from time import sleep  # To introduce delays if needed

# === Class responsible for recognizing faces ===
class FaceRecognizer:
    def __init__(self, model_path="models/mobilefacenet.tflite", embeddings_dir="embeddings", threshold=0.8):
        """
        Initializes the face recognition system.
        - Loads the TFLite model for embedding generation.
        - Initializes MediaPipe face detection.
        - Loads known embeddings from disk.
        """
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'face-auth'))
        self.embeddings_dir = os.path.join(project_root, 'embeddings')
        print("FIXED: embeddings_dir =", self.embeddings_dir)

        self.threshold = threshold  # Threshold for distance comparison (lower = more strict)
        self.interpreter = tflite.Interpreter(model_path="../models/mobilefacenet.tflite")
        self.interpreter.allocate_tensors()  # Prepare the model for inference
        self.input_details = self.interpreter.get_input_details()  # Get input tensor details
        self.output_details = self.interpreter.get_output_details()  # Get output tensor details
        self.face_detection = mp.solutions.face_detection.FaceDetection(
            model_selection=0, min_detection_confidence=0.5
        )  # Load MediaPipe face detector
        print("DEBUG: embeddings_dir =", self.embeddings_dir)
        self.known_embeddings = self.load_known_embeddings()  # Load embeddings from disk

    def load_known_embeddings(self):
        """
        Loads all embeddings previously saved to disk.
        Returns a dictionary where keys are usernames and values are lists of embeddings.
        """
        known = {}
        for user_folder in os.listdir(self.embeddings_dir):
            user_path = os.path.join(self.embeddings_dir, user_folder)
            if os.path.isdir(user_path):  # Ensure it's a directory
                for file in os.listdir(user_path):
                    if file.endswith(".pkl"):  # Only load .pkl files
                        path = os.path.join(user_path, file)
                        with open(path, "rb") as f:
                            embedding = pickle.load(f)  # Load the embedding
                            if user_folder not in known:
                                known[user_folder] = []  # Initialize list for user
                            known[user_folder].append(embedding)  # Add embedding to the user
        return known  # Return dictionary of all known embeddings

    def preprocess_image(self, image):
        """
        Prepares an image for input to the model:
        - Converts RGBA to RGB if needed
        - Resizes to 112x112
        - Normalizes pixel values to [0, 1]
        - Expands dimensions to match model input
        """
        if image.shape[2] == 4:
            image = cv2.cvtColor(image, cv2.COLOR_RGBA2RGB)  # Convert RGBA to RGB
        resized = cv2.resize(image, (112, 112))  # Resize to expected input size
        normalized = resized.astype('float32') / 255.0  # Normalize pixel values
        return np.expand_dims(normalized, axis=0)  # Add batch dimension (1, 112, 112, 3)

    def get_embedding(self, image):
        """
        Runs the image through the TFLite model and returns the resulting embedding vector.
        """
        input_data = self.preprocess_image(image)  # Preprocess input
        self.interpreter.set_tensor(self.input_details[0]['index'], input_data)  # Set input tensor
        self.interpreter.invoke()  # Run inference
        return self.interpreter.get_tensor(self.output_details[0]['index'])[0]  # Return the embedding (shape: [192])

    def recognize_face(self, embedding, known_embeddings):
        """
        Compares the input embedding with known embeddings.
        Returns:
        - The name of the closest match (if distance < threshold)
        - The distance to that match
        Otherwise returns ("Unknown", None)
        """
        best_match = "Unknown"
        best_distance = float('inf')  # Start with a very large distance

        # This should use `known_embeddings`, not `self.known_embeddings`
        for name, embeddings in self.known_embeddings.items():
            for known_emb in embeddings:
                distance = np.linalg.norm(embedding - known_emb)  # Euclidean distance
                if distance < best_distance:
                    best_distance = distance
                    best_match = name

        # Return best match only if it's below the threshold
        return (best_match, best_distance) if best_distance < self.threshold else ("Unknown", None)

    def detect_faces(self, frame):
        """
        Detects faces in a given frame using MediaPipe.
        Returns a list of bounding boxes (x, y, width, height).
        """
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Convert image to RGB
        results = self.face_detection.process(rgb_frame)  # Run face detection
        faces = []

        if results.detections:
            for detection in results.detections:
                bboxC = detection.location_data.relative_bounding_box
                ih, iw, _ = frame.shape  # Get image dimensions
                x = int(bboxC.xmin * iw)
                y = int(bboxC.ymin * ih)
                w = int(bboxC.width * iw)
                h = int(bboxC.height * ih)
                faces.append((x, y, w, h))  # Append bounding box

        return faces  # List of bounding boxes of detected faces
