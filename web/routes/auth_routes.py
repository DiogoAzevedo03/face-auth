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

from utils.discord import send_discord_notification
from datetime import datetime

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
import pickle

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

    # Decode base64 image
    image_data = data['image'].split(',')[1]
    image_bytes = base64.b64decode(image_data)
    image = Image.open(BytesIO(image_bytes)).convert('RGB')
    frame = np.array(image)

    # Detect faces
    faces = recognizer.detect_faces(frame)
    suggestions = []

    if faces:
        (x, y, w, h) = faces[0]

        # Validate coordinates
        if x >= 0 and y >= 0 and w > 0 and h > 0 and x + w <= frame.shape[1] and y + h <= frame.shape[0]:
            face_crop = frame[y:y+h, x:x+w]

            # Double-check validity
            if face_crop.size > 0:
                embedding = recognizer.get_embedding(face_crop)
                name, dist = recognizer.recognize_face(embedding, recognizer.known_embeddings)

                if name != "Unknown":
                    session['temp_embedding'] = embedding.tolist() 
                    users = load_users()
                    for email, user in users.items():
                        if user.get('folder') == name:
                            session['user'] = email
                            session['login_time'] = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
                            session['role'] = user.get('role')

                            # Suggest similar users
                            all_distances = []
                            for folder_name, embeddings_list in recognizer.known_embeddings.items():
                                for known_emb in embeddings_list:
                                    dist = np.linalg.norm(embedding - known_emb)
                                    all_distances.append((folder_name, dist))

                            all_distances.sort(key=lambda x: x[1])
                            seen = set()
                            for folder_name, _ in all_distances:
                                if folder_name not in seen:
                                    suggestions.append(folder_name)
                                    seen.add(folder_name)
                                    if len(suggestions) == 3:
                                        break

                            return jsonify({
                                "success": True,
                                "message": "User recognized successfully.",
                                "data": {
                                    "user": name,
                                    "redirect": "/admin/dashboard" if user.get('role') == 'admin' else "/user",
                                    "suggestions": suggestions
                                }
                            })

                # Fallback: generate suggestions if embedding exists
                all_distances = []
                for folder_name, embeddings_list in recognizer.known_embeddings.items():
                    for known_emb in embeddings_list:
                        dist = np.linalg.norm(embedding - known_emb)
                        all_distances.append((folder_name, dist))

                all_distances.sort(key=lambda x: x[1])
                seen = set()
                for folder_name, _ in all_distances:
                    if folder_name not in seen:
                        suggestions.append(folder_name)
                        seen.add(folder_name)
                        if len(suggestions) == 3:
                            break

    send_discord_notification("🔴 Tentativa de login falhada. Rosto não reconhecido.")

    # Return fallback response
    return jsonify({
        "success": False,
        "message": "User not recognized.",
        "data": {
            "suggestions": suggestions
        }
    })

@auth_bp.route('/confirm-face-login', methods=['POST'])
def confirm_face_login():
    if 'user' not in session or 'temp_embedding' not in session:
        print("[DEBUG] Session expired or no temporary embedding.")
        return jsonify({"success": False, "message": "Session expired."}), 403

    email = session['user']
    hora_login = datetime.now().strftime('%d/%m/%Y às %H:%M')
    send_discord_notification(f"🟢 {email} fez login com sucesso via FaceAuth em {hora_login}")
    new_embedding = np.array(session['temp_embedding'])
    users = load_users()
    folder = users[email]['folder']

    existing_embeddings = recognizer.known_embeddings.get(folder, [])
    should_save = False

    for emb in existing_embeddings:
        dist = np.linalg.norm(new_embedding - emb)
        print(f"[DEBUG] Distance to existing embedding: {dist:.3f}")
        if dist < 0.5:
            print("[DEBUG] Embedding already known. Will not be saved.")
            return jsonify({"success": True, "message": "Embedding already exists. No need to save."})
        elif 0.5 < dist < 1.2:
            should_save = True

    if not should_save:
        print("[DEBUG] Embedding outside allowed range. Not saved.")
        return jsonify({"success": False, "message": "Embedding too different. Not saved."})

    user_dir = os.path.join('..', 'embeddings', folder)
    os.makedirs(user_dir, exist_ok=True)

    existing_files = [f for f in os.listdir(user_dir) if f.endswith(".pkl")]
    next_index = len(existing_files)
    filename = os.path.join(user_dir, f"{folder}_{next_index:02d}.pkl")

    with open(filename, "wb") as f:
        pickle.dump(new_embedding, f)

    print(f"[DEBUG] New embedding saved in{filename}")

    recognizer.known_embeddings = recognizer.load_known_embeddings()

    return jsonify({"success": True, "message": "New embedding saved to improve recognition accuracy."})

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
            hora_login = datetime.now().strftime('%d/%m/%Y às %H:%M')
            send_discord_notification(f"🟢 {email} foi selecionado manualmente após sugestão em {hora_login}")
            return redirect('/admin/dashboard' if user.get('role') == 'admin' else '/user')

    # Se não encontrar, volta para o login facial
    return redirect(url_for('auth.face_login_page'))
