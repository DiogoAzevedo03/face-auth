# ============================================
# Face Embedding Generator
# File: generate_multiple_embeddings_m.py
# Authors: Diogo Azevedo and Letícia Loureiro
# Date: 2025-04-15
#
# Description:
# This script defines the EmbeddingGenerator class, which:
# - Detects faces using MediaPipe.
# - Preprocesses face images.
# - Generates facial embeddings using a TFLite model (MobileFaceNet).
# - Saves embeddings as .pkl files for later recognition.
#
# Embeddings are saved in the 'embeddings/<username>' directory.
# Used in conjunction with recognize_m.py for real-time face recognition.
#
# ============================================

import cv2  # OpenCV for image and video processing
import numpy as np  # NumPy for numerical operations
import os  # OS functions for directory and file management
import pickle  # To save and load embeddings
import tflite_runtime.interpreter as tflite  # Lightweight TFLite interpreter for inference
import mediapipe as mp  # MediaPipe for face detection

# === Class responsible for generating face embeddings from images ===
class EmbeddingGenerator:
    def __init__(self, model_path=os.path.join(os.path.dirname(__file__), 'models/mobilefacenet.tflite'), save_base_path="embeddings/"):
        """
        Constructor method for the EmbeddingGenerator class.
        - Loads the MobileFaceNet TFLite model.
        - Sets up MediaPipe for face detection.
        - Ensures the base directory for saving embeddings exists.
        """
        self.save_base_path = save_base_path  # Directory where embeddings will be saved
        os.makedirs(save_base_path, exist_ok=True)  # Create the directory if it doesn't exist

        # Load the TensorFlow Lite model for face embeddings
        self.interpreter = tflite.Interpreter(model_path=model_path)
        self.interpreter.allocate_tensors()  # Allocate memory for inference
        self.input_details = self.interpreter.get_input_details()  # Input tensor details
        self.output_details = self.interpreter.get_output_details()  # Output tensor details

        # Initialize MediaPipe face detector with a confidence threshold
        self.face_detection = mp.solutions.face_detection.FaceDetection(
            model_selection=0, min_detection_confidence=0.5
        )

    def preprocess_face(self, face_img):
        """
        Prepares a face image for embedding generation.
        Steps:
        - Resize to 112x112 (model input size).
        - Convert BGR to RGB.
        - Normalize pixel values to [0, 1].
        - Add batch dimension.
        Returns a NumPy array ready for model input.
        """
        face_img = cv2.resize(face_img, (112, 112))  # Resize to expected input size
        face_img = cv2.cvtColor(face_img, cv2.COLOR_BGR2RGB)  # Convert to RGB format
        face_img = face_img.astype("float32") / 255.0  # Normalize pixel values
        return np.expand_dims(face_img, axis=0)  # Add batch dimension

    def get_embedding(self, face_img):
        """
        Generates an embedding from a single face image.
        - Preprocesses the image.
        - Runs it through the TFLite model.
        - Returns the embedding vector.
        """
        input_data = self.preprocess_face(face_img)  # Prepare the image
        self.interpreter.set_tensor(self.input_details[0]['index'], input_data)  # Set input
        self.interpreter.invoke()  # Run the model
        embedding = self.interpreter.get_tensor(self.output_details[0]['index'])[0]  # Extract output
        return embedding  # Return the embedding vector (typically length 192)

    def detect_faces(self, frame):
        """
        Detects faces in a given video frame using MediaPipe.
        Returns a list of bounding boxes: (x, y, width, height).
        """
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Convert to RGB for MediaPipe
        results = self.face_detection.process(rgb_frame)  # Perform face detection
        faces = []

        if results.detections:
            for detection in results.detections:
                bboxC = detection.location_data.relative_bounding_box
                ih, iw, _ = frame.shape  # Get image height and width
                x = int(bboxC.xmin * iw)
                y = int(bboxC.ymin * ih)
                w = int(bboxC.width * iw)
                h = int(bboxC.height * ih)

                # Ensure the bounding box stays within image boundaries
                x, y = max(0, x), max(0, y)
                w, h = min(w, iw - x), min(h, ih - y)

                faces.append((x, y, w, h))  # Append bounding box to list

        return faces  # Return list of detected faces

    def save_embedding(self, embedding, username, counter):
        """
        Saves a face embedding to a .pkl file in the user's directory.
        - 'username' defines the folder.
        - 'counter' ensures multiple embeddings can be saved per user.
        Returns the filename for reference.
        """
        user_dir = os.path.join(self.save_base_path, username)  # Path to user folder
        os.makedirs(user_dir, exist_ok=True)  # Create user folder if not existing

        # Filename pattern: embeddings/username/username_00.pkl
        filename = os.path.join(user_dir, f"{username}_{counter:02d}.pkl")

        with open(filename, "wb") as f:
            pickle.dump(embedding, f)  # Save embedding as a binary file

        return filename  # Return the full path to the saved file
