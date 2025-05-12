# ============================================
# Authentication Routes - FaceAuth Web Application
# File: auth_routes.py
# Authors: Diogo Azevedo and Letícia Loureiro
# Date: 2025-04-28
#
# Description:
# This module handles all authentication-related routes for the FaceAuth platform.
# It supports:
# - Manual login using email and password
# - Face recognition login via webcam
# - Logout
# - Redirecting users to their respective dashboard based on their role
# ============================================

# === Flask and utility imports ===
from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify

# === Import custom user DB utilities ===
from utils.user_db import load_users

# === Add project root to sys.path for module accessibility ===
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# === Standard Python imports ===
from datetime import datetime  # Used to store login time in session
import base64                  # For decoding image sent from client
import numpy as np             # For image array handling
from PIL import Image          # For handling and converting image files
from io import BytesIO         # For reading image bytes
import bcrypt                  # For verifying hashed passwords

# === Import facial recognition logic ===
from recognize_m import FaceRecognizer

# === Define authentication Blueprint ===
auth_bp = Blueprint('auth', __name__)

# === Initialize face recognizer once when the module is loaded ===
recognizer = FaceRecognizer()

# === Manual Login Route (GET and POST) ===
@auth_bp.route('/login', methods=['GET', 'POST'])
def manual_login():
    """
    Renders login form (GET) or processes login (POST).
    If the credentials match, logs in the user and sets session.
    Redirects user to either admin or user page based on role.
    """
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        users = load_users()  # Load user data from JSON

        if email in users:
            stored_hash = users[email]['password'].encode()
            if bcrypt.checkpw(password.encode(), stored_hash):
                # Set session with user details
                session['user'] = email
                session['login_time'] = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
                session['role'] = users[email]['role']

                # Redirect based on role
                return redirect(url_for('admin.dashboard' if users[email]['role'] == 'admin' else 'auth.user_page'))

        # If login fails, show error message
        return render_template('login.html', error='Invalid credentials.')

    # Render login page for GET request
    return render_template('login.html')

# === Logout Route ===
@auth_bp.route('/logout')
def logout():
    """
    Clears session data and redirects to homepage (index).
    """
    session.clear()
    return redirect(url_for('index'))

# === Face Login Page (renders face_login.html) ===
@auth_bp.route('/face-login', methods=['GET'])
def face_login_page():
    """
    Displays the face login interface to the user.
    """
    return render_template('face_login.html')

# === Face Login POST Handler ===
@auth_bp.route('/face-login', methods=['POST'])
def face_login():
    """
    Receives an image from the front-end (Base64),
    runs facial recognition, and logs the user in if matched.
    Returns a JSON response indicating success or failure.
    """
    data = request.get_json()
    
    # Decode base64 image sent from browser
    image_data = data['image'].split(',')[1]
    image_bytes = base64.b64decode(image_data)
    image = Image.open(BytesIO(image_bytes)).convert('RGB')
    frame = np.array(image)

    # Detect faces in the image
    faces = recognizer.detect_faces(frame)
    if faces:
        # Crop the first detected face from the frame
        (x, y, w, h) = faces[0]
        face_crop = frame[y:y+h, x:x+w]

        # Generate an embedding for the detected face
        embedding = recognizer.get_embedding(face_crop)

        # Try to recognize the face using known embeddings
        name, dist = recognizer.recognize_face(embedding, recognizer.known_embeddings)

        if name != "Unknown":
            users = load_users()

            # Find the corresponding email by matching folder name
            for email, user in users.items():
                if user.get('folder') == name:
                    # If match is found, create session
                    session['user'] = email
                    session['login_time'] = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
                    session['role'] = user.get('role')
                    
                    # Calcular sugestões mesmo que tenha havido match
                    distances = []
                    for other_name, known_emb in recognizer.known_embeddings.items():
                        dist = np.linalg.norm(embedding - known_emb)
                        distances.append((other_name, dist))

                    # Ordenar pelas menores distâncias
                    distances.sort(key=lambda x: x[1])
                    suggestions = [name for name, _ in distances[:3]]
                    return jsonify({
                        "success": True,
                        "message": "User recognized successfully.",
                        "data": {
                            "user": name,
                            "redirect": "/admin/dashboard" if user.get('role') == 'admin' else "/user",
                            "suggestions": suggestions
                        }
                    })


    # If no match or no face detected, suggest similar users
    suggestions = []

    if 'embedding' in locals():  # Só se tiver gerado embedding
        # Calcula distância de todos os embeddings conhecidos
        distances = []
        for name, known_emb in recognizer.known_embeddings.items():
            dist = np.linalg.norm(embedding - known_emb)
            distances.append((name, dist))

        # Ordena pelas distâncias mais pequenas (mais parecidos)
        distances.sort(key=lambda x: x[1])

        # Pega no top 3 nomes mais parecidos (se existirem)
        suggestions = [name for name, _ in distances[:3]]

    return jsonify({
        "success": False,
        "message": "User not recognized.",
        "data": {
            "suggestions": suggestions
        }
    })

# === Authenticated User Area ===
@auth_bp.route('/user')
def user_page():
    """
    Displays the user page if authenticated.
    Otherwise, redirects to face login.
    """
    if 'user' not in session:
        return redirect(url_for('auth.face_login_page'))
    return render_template('user.html')

# === Manual Select from Suggestions ===
@auth_bp.route('/manual-select')
def manual_select():
    """
    Logs in the user selected manually from the suggestions list.
    This route is called when the user clicks on a suggested identity.
    """
    selected_name = request.args.get('user')  # Nome selecionado pelo botão

    if not selected_name:
        return redirect(url_for('auth.face_login_page'))

    users = load_users()
    
    # Procurar pelo utilizador cujo nome (pasta) corresponde
    for email, user in users.items():
        if user.get('folder') == selected_name:
            session['user'] = email
            session['login_time'] = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            session['role'] = user.get('role')
            return redirect('/admin/dashboard' if user.get('role') == 'admin' else '/user')

    # Se não encontrar, volta para o login facial
    return redirect(url_for('auth.face_login_page'))
