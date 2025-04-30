# ============================================
# Facial Embedding Routes - FaceAuth Web Application
# File: face_routes.py
# Authors: Diogo Azevedo and Letícia Loureiro
# Date: 2025-04-28
#
# Description:
# This module defines all the routes for:
# - User creation by the admin
# - Capturing and saving facial embeddings
# - Face detection visualization for bounding box preview
# ============================================

# === Flask and standard libraries ===
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, session
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from datetime import datetime

# === Custom Modules ===
from generate_multiple_embeddings_m import EmbeddingGenerator
from utils.user_db import load_users, save_users

# === Data processing and security ===
import base64
import numpy as np
import pickle
from PIL import Image
from io import BytesIO
import bcrypt

# === Define Blueprint for face-related routes ===
face_bp = Blueprint('face', __name__)

# === Initialize embedding generator globally (loads model once) ===
embedder = EmbeddingGenerator()

# === Admin view to access the user registration page ===
@face_bp.route('/admin/generate')
def admin_generate():
    """
    Displays the form and video stream for the admin to create a user
    and capture facial embeddings.

    Only accessible to authenticated admins.
    """
    if 'user' not in session or session.get('role') != 'admin':
        return redirect(url_for('auth.manual_login'))
    return render_template('generate.html')

# === Create a new user in the JSON database ===
@face_bp.route('/admin/create-user', methods=['POST'])
def create_user():
    """
    Creates a new user account (email, password, role, folder name).
    Returns error if the email or folder already exists.
    """
    data = request.get_json()
    users = load_users()
    email = data['email']
    folder = data['folder']
    folder_path = os.path.join('..', 'embeddings', folder)

    # Check if email already exists
    if email in users:
        return "Email already exists", 400

    # Check if folder with same name exists
    if os.path.exists(folder_path):
        return "Folder name already exists", 400

    # Hash and store the password securely
    hashed_pw = bcrypt.hashpw(data['password'].encode(), bcrypt.gensalt()).decode()

    # Register user in database
    users[email] = {
        "password": hashed_pw,
        "role": data['role'],
        "folder": folder
    }

    save_users(users)
    return "User created", 200

# === Save facial embedding after image capture ===
@face_bp.route('/admin/save-embedding', methods=['POST'])
def save_embedding():
    """
    Receives a base64 image, detects a face, and saves the embedding.
    Supports:
      - 'drawOnly' mode: returns bounding box for preview
      - 'save' mode: stores the embedding on disk

    Returns status and bounding box coordinates if applicable.
    """
    data = request.get_json()
    folder = data['folder']       # Folder to store embedding
    index = data['index']         # Index used in filename (e.g. folder_00.pkl)
    draw_only = data.get('drawOnly', False)  # Preview-only mode flag

    # Decode base64 image into NumPy array
    image_data = data['image'].split(',')[1]
    image_bytes = base64.b64decode(image_data)
    image = Image.open(BytesIO(image_bytes)).convert('RGB')
    frame = np.array(image)

    # Detect faces in image
    faces = embedder.detect_faces(frame)
    if not faces:
        return "No face detected", 400

    # Take first face detected and crop it
    (x, y, w, h) = faces[0]
    face_crop = frame[y:y+h, x:x+w]
    if face_crop.size == 0:
        return "Invalid face crop", 400

    # If in preview mode, just return coordinates of bounding box
    if draw_only:
        return jsonify({"x": int(x), "y": int(y), "w": int(w), "h": int(h)})

    # Get face embedding from model
    embedding = embedder.get_embedding(face_crop)

    # Prepare storage path and save .pkl file
    path = os.path.join('..', 'embeddings', folder)
    os.makedirs(path, exist_ok=True)
    with open(os.path.join(path, f"{folder}_{index:02d}.pkl"), "wb") as f:
        pickle.dump(embedding, f)

    return "Saved successfully", 200

