"""
Camera Functionality Test with Picamera2

Author: Diogo Azevedo & Leticia Loureiro
Date: 2025-03-20
Description:
This script tests whether the camera is working using the Picamera2 library.
It opens a window with a real-time image for 60 seconds.
"""

from picamera2 import Picamera2, Preview  # Import the camera class and preview type
from time import sleep  # Import function to pause execution

# Initialize the camera
picam2 = Picamera2()

# Start the preview with graphical interface (QT)
picam2.start_preview(Preview.QTGL)

# Start the camera capture
picam2.start()

# Wait 60 seconds while the camera is active
sleep(60)

# Close the camera and stop the preview
picam2.close()