# FaceAuth - Face Embedding Generator

 - author branches:
   - diogo
   - leticia 
   
## Overview
This project is part of the FaceAuth system, which aims to provide facial recognition authentication. The primary function of this component is to capture a face using the Raspberry Pi camera (via Picamera2) and generate a 128-dimensional embedding using a pre-trained MobileFaceNet model in TensorFlow Lite format. These embeddings serve as unique representations of faces and are used later for comparing and recognizing users.

## How to Run
1. Ensure that the camera is connected and the Raspberry Pi is running the desktop environment.
2. Install the required dependencies by running:
    ```bash
    pip install -r requirements.txt
    ```
3. Execute the embedding generator script:
    ```bash
    python3 generate_face_embedding.py
    ```
   The script will display a live camera feed. Press 's' to capture the frame, then enter the username. The corresponding face embedding will be saved as a `.pkl` file in the `embeddings/` directory.

## Why is it needed?
The generated face embeddings are a key component of the FaceAuth system. They allow the system to uniquely represent each user's face as a numerical vector. These embeddings are used to perform face comparisons and recognition, enabling secure and efficient authentication.

## Requirements
The project relies on several Python libraries, which are listed in the `requirements.txt` file.
