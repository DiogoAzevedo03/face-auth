# ============================================
# Admin Routes - FaceAuth Web Application
# File: admin_routes.py
# Authors: Diogo Azevedo and Letícia Loureiro
# Date: 2025-04-28
#
# Description:
# This file defines the admin-specific routes for the FaceAuth platform.
# Admins can:
# - Access the dashboard
# - Add new users
# - Remove users
# - Logout of their session
# ============================================

# === Flask and Python standard imports ===
from flask import Blueprint, render_template, request, redirect, url_for, session

# === Internal helper functions to read/write users from JSON file ===
from utils.user_db import load_users, save_users
from web.routes.auth_routes import recognizer

# === Password hashing and file system handling ===
import bcrypt  # Secure password hashing
import os      # File path operations
import shutil  # Directory removal
from datetime import datetime  # Not currently used here, but available if needed
from utils.email_notify import send_email_notification


# === Define a Blueprint for admin-related routes ===
admin_bp = Blueprint('admin', __name__)

# === Admin Dashboard Page ===
@admin_bp.route('/admin/dashboard')
def dashboard():
    # Redirect to login if not authenticated
    if 'user' not in session:
        return redirect(url_for('auth.manual_login'))

    # Load users from JSON database
    users = load_users()
    user_email = session.get('user')
    user_folder = users[user_email]['folder']
    
    # Render the dashboard page, passing all user data
    return render_template("dashboard.html", users=users, user_folder=user_folder)

# === Admin Logout ===
@admin_bp.route('/admin/logout')
def admin_logout():
    # Remove the user from the session (logout)
    session.pop('user', None)

    # Redirect to manual login page (this could be changed to index if needed)
    return redirect(url_for('auth.manual_login'))

# === Add New User (from Admin Dashboard Form) ===
@admin_bp.route('/admin/add', methods=['POST'])
def admin_add():
    # Extract form data submitted by the admin
    email = request.form['email']
    password = request.form['password']
    role = request.form['role']

    # Load current users from storage
    users = load_users()

    # Check if email is already registered
    if email in users:
        return 'User already exists!'

    # Hash the new user's password securely
    hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    # Save new user to the dictionary
    users[email] = {
        'password': hashed_pw,
        'role': role
    }

    # Save updated users list to JSON
    save_users(users)

    send_email_notification(
        subject="Novo Utilizador Criado",
        body_text=f"O utilizador {email} foi registado com o papel: {role}.",
        body_html=f"""
        <h2 style="color:#2c3e50;">Novo Utilizador Criado </h2>
        <p>Foi registado um novo utilizador no sistema.</p>
        <ul>
        <li><strong>Email:</strong> {email}</li>
        <li><strong>Papel:</strong> {role}</li>
        <li><strong>Data:</strong> {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</li>
        </ul>
        """
    )


    print(f"[DEBUG] A enviar email para notificar criação do utilizador: {email}")


    # Redirect back to dashboard to see new user
    return redirect(url_for('admin.dashboard'))

# === Remove Existing User ===
@admin_bp.route('/admin/remove', methods=['POST'])
def admin_remove():
    folder = request.form.get('folder')
    print("[DEBUG] Pedido de remoção para folder:", folder)

    users = load_users()

    user_to_delete = None
    for email, info in users.items():
        print(f"[DEBUG] A verificar utilizador: {email} -> {info.get('folder')}")
        if info.get("folder") == folder:
            user_to_delete = email
            break

    if user_to_delete:
        print(f"[INFO] Removendo utilizador: {user_to_delete}")
        users.pop(user_to_delete)
        save_users(users)

        send_email_notification(
            subject="Utilizador Removido",
            body_text=f"O utilizador {user_to_delete} foi removido do sistema.",
            body_html=f"""
            <h2 style="color:#e74c3c;">Utilizador Removido </h2>
            <p>Um utilizador foi eliminado do sistema.</p>
            <ul>
            <li><strong>Email:</strong> {user_to_delete}</li>
            <li><strong>Data:</strong> {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</li>
            </ul>
            """
        )


        folder_path = os.path.join('..', 'embeddings', folder)
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)
            print(f"[INFO] Pasta de embeddings {folder_path} removida")

                # Reload embeddings in the global face recognizer
        recognizer.known_embeddings = recognizer.load_known_embeddings()
        print("[DEBUG] Embeddings recarregados após remoção do utilizador")
    else:
        print("[WARN] Nenhum utilizador encontrado com o folder fornecido")

    return redirect(url_for('admin.dashboard'))