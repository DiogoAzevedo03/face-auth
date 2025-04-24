# ============================================
# FaceAuth Web Application Backend
# File: app.py
# Authors: Diogo Azevedo and Letícia Loureiro
# Date: 2025-04-23
#
# Description:
# This Flask application powers the FaceAuth web platform.
# It handles:
# - Manual and facial login
# - User management (create, remove)
# - Session management
# - Real-time face recognition
# - Embedding generation and storage
# ============================================

# === Python imports ===
import sys
sys.path.append('..')  # Add parent directory to sys.path to allow module imports

import os
import json
import base64
import pickle
from datetime import datetime
from io import BytesIO

# === Third-party dependencies ===
import numpy as np
import cv2
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from PIL import Image

# === Custom face recognition modules ===
from recognize_m import FaceRecognizer
from generate_multiple_embeddings_m import EmbeddingGenerator

# === Flask app setup ===
app = Flask(__name__)
app.secret_key = 'faceauth-secret-key'  # Used to secure session cookies

# === Path to the JSON file that stores registered users ===
USERS_DB = os.path.join(os.path.dirname(__file__), 'users.json')

# === Initialize facial recognition and embedding systems ===
recognizer = FaceRecognizer()
embedder = EmbeddingGenerator()

# === Helper function: Load all users from JSON ===
def load_users():
    if os.path.exists(USERS_DB):
        with open(USERS_DB, 'r') as f:
            return json.load(f)
    return {}

# === Helper function: Save updated user dictionary to JSON ===
def save_users(users):
    with open(USERS_DB, 'w') as f:
        json.dump(users, f, indent=4)

# === Web Routes ===

# Homepage (Landing page)
@app.route('/')
def index():
    return render_template('index.html')

# Manual Login route (GET = show form, POST = process login)
@app.route('/login', methods=['GET', 'POST'])
def manual_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        users = load_users()

        # Verify credentials
        if email in users and users[email]['password'] == password:
            session['user'] = email
            session['login_time'] = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            session['role'] = users[email]['role']
            # Redirect based on user role
            return redirect(url_for('admin_dashboard' if users[email]['role'] == 'admin' else 'user_page'))
        else:
            return render_template('login.html', error='Invalid credentials.')

    return render_template('login.html')

# Admin dashboard route (user listing + actions)
@app.route('/admin/dashboard')
def admin_dashboard():
    if 'user' not in session:
        return redirect(url_for('admin_login'))  # Protection if not logged in
    users = load_users()
    return render_template('dashboard.html', users=users)

# Logout for admin
@app.route('/admin/logout')
def admin_logout():
    session.pop('user', None)
    return redirect(url_for('admin_login'))

# Generic logout for all users
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# Route to add user via form (used in embedding generation)
@app.route('/admin/add', methods=['POST'])
def admin_add():
    email = request.form['email']
    password = request.form['password']
    role = request.form['role']

    users = load_users()
    if email in users:
        return 'User already exists!'

    users[email] = {
        'password': password,
        'role': role
    }
    save_users(users)
    return redirect(url_for('admin_dashboard'))

# Remove a user + delete their embeddings folder
@app.route('/admin/remove', methods=['POST'])
def admin_remove():
    import shutil

    email = request.form['email']
    users = load_users()

    if email in users:
        folder = users[email].get("folder")
        users.pop(email)
        save_users(users)

        # Remove corresponding embedding folder (if exists)
        if folder:
            folder_path = os.path.join('..', 'embeddings', folder)
            if os.path.exists(folder_path):
                shutil.rmtree(folder_path)

    return redirect(url_for('admin_dashboard'))

# User-specific landing page
@app.route('/user')
def user_page():
    if 'user' not in session:
        return redirect(url_for('face_login_page'))
    return render_template('user.html')

# Face login interface route (GET)
@app.route('/face-login')
def face_login_page():
    return render_template('face_login.html')

# Process facial login (POST)
@app.route('/face-login', methods=['POST'])
def face_login():
    data = request.get_json()
    image_data = data['image'].split(',')[1]
    image_bytes = base64.b64decode(image_data)
    image = Image.open(BytesIO(image_bytes)).convert('RGB')
    frame = np.array(image)

    # Detect face in image
    faces = recognizer.detect_faces(frame)
    if faces:
        (x, y, w, h) = faces[0]
        face_crop = frame[y:y+h, x:x+w]
        embedding = recognizer.get_embedding(face_crop)

        # Match with known embeddings
        name, dist = recognizer.recognize_face(embedding, recognizer.known_embeddings)

        if name != "Unknown":
            users = load_users()
            for email, user in users.items():
                if user.get('folder') == name:
                    session['user'] = email
                    session['login_time'] = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
                    session['role'] = user.get('role')
                    return jsonify({"success": True, "user": name, "redirect": "/admin/dashboard" if user.get('role') == 'admin' else "/user"})

    return jsonify({"success": False})

# Route to display form for adding user and capturing embeddings
@app.route('/admin/generate')
def admin_generate():
    if 'user' not in session or session.get('role') != 'admin':
        return redirect(url_for('index'))
    return render_template('generate.html')

# Endpoint to create user and associate embedding folder
@app.route('/admin/create-user', methods=['POST'])
def create_user():
    data = request.get_json()
    users = load_users()
    email = data['email']
    folder = data['folder']
    folder_path = os.path.join('..', 'embeddings', folder)

    if email in users:
        return "Email already exists", 400
    if os.path.exists(folder_path):
        return "Folder name already exists", 400

    users[email] = {
        "password": data['password'],
        "role": data['role'],
        "folder": folder
    }
    save_users(users)
    return "User created", 200

# Save embedding to disk (via AJAX from frontend)
@app.route('/admin/save-embedding', methods=['POST'])
def save_embedding():
    data = request.get_json()
    folder = data['folder']
    index = data['index']
    draw_only = data.get('drawOnly', False)

    image_data = data['image'].split(',')[1]
    image_bytes = base64.b64decode(image_data)
    image = Image.open(BytesIO(image_bytes)).convert('RGB')
    frame = np.array(image)

    # Detect face in frame
    faces = embedder.detect_faces(frame)
    if not faces:
        return "No face detected", 400

    (x, y, w, h) = faces[0]
    face_crop = frame[y:y+h, x:x+w]
    if face_crop.size == 0:
        return "Invalid face crop", 400

    # If request is just to preview detection (no save)
    if draw_only:
        return jsonify({"x": int(x), "y": int(y), "w": int(w), "h": int(h)})

    # Generate and save embedding
    embedding = embedder.get_embedding(face_crop)
    path = os.path.join('..', 'embeddings', folder)
    os.makedirs(path, exist_ok=True)
    with open(os.path.join(path, f"{folder}_{index:02d}.pkl"), "wb") as f:
        pickle.dump(embedding, f)

    return "Saved successfully", 200

# === Start Flask app ===
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
