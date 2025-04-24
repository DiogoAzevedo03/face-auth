# FaceAuth - Test Scripts

## Overview

This folder contains scripts to test the Raspberry Pi camera and capture face embeddings for facial recognition.

## How to run

1. Install dependencies (once):
    ```bash
    pip install -r requirements.txt
    ```

2. Test if the camera is working:
    ```bash
    python3 tests/test_camera.py
    ```


> 📷 Note: You need to run this directly on the Raspberry Pi with a connected camera.

## Purpose of each script

- `test_camera.py`  
  Checks if the camera is working by displaying a live video feed for 60 seconds.