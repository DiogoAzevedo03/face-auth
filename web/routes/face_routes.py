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
    folder = data['folder']
    draw_only = data.get('drawOnly', False)

    # Decode base64 image into NumPy array
    image_data = data['image'].split(',')[1]
    image_bytes = base64.b64decode(image_data)
    image = Image.open(BytesIO(image_bytes)).convert('RGB')
    frame = np.array(image)

    # Detect faces in image
    faces = embedder.detect_faces(frame)
    if not faces:
        return "No face detected", 400

    (x, y, w, h) = faces[0]
    face_crop = frame[y:y+h, x:x+w]
    if face_crop.size == 0:
        return "Invalid face crop", 400

    if draw_only:
        return jsonify({
            "success": True,
            "message": "Face detected. Returning bounding box.",
            "data": {
                "x": int(x),
                "y": int(y),
                "w": int(w),
                "h": int(h)
            }
        })

    # Get face embedding
    embedding = embedder.get_embedding(face_crop)

    # Create path if not exists
    path = os.path.join('..', 'embeddings', folder)
    os.makedirs(path, exist_ok=True)

    # Find next available index to avoid overwriting
    existing_files = [f for f in os.listdir(path) if f.endswith('.pkl') and f.startswith(folder + "_")]
    indices = []
    for fname in existing_files:
        try:
            number = int(fname.replace(folder + "_", "").replace(".pkl", ""))
            indices.append(number)
        except:
            continue
    next_index = max(indices) + 1 if indices else 0

    save_path = os.path.join(path, f"{folder}_{next_index:02d}.pkl")
    with open(save_path, "wb") as f:
        pickle.dump(embedding, f)

    print(f"[DEBUG] Saved embedding: {save_path}")
    return "Saved successfully", 200


from flask import request, render_template

@face_bp.route('/admin/capture-more', methods=['GET'])
def capture_more_embeddings():
    folder = request.args.get('folder')
    if not folder:
        return "folder not provided", 400
    return render_template('capture_more_embeddings.html', folder=folder)

@face_bp.route('/admin/capture-more/process', methods=['POST'])
def capture_embeddings_process():
    folder = request.form.get('folder')
    num_embeddings = int(request.form.get('num_embeddings', 5))
    
    return f"Capture {num_embeddings} embeddings for {folder}"
