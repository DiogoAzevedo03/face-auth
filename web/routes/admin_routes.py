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

# === Password hashing and file system handling ===
import bcrypt  # Secure password hashing
import os      # File path operations
import shutil  # Directory removal
from datetime import datetime  # Not currently used here, but available if needed

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

    # Render the dashboard page, passing all user data
    return render_template('dashboard.html', users=users)

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

    # Redirect back to dashboard to see new user
    return redirect(url_for('admin.dashboard'))

# === Remove Existing User ===
@admin_bp.route('/admin/remove', methods=['POST'])
def admin_remove():
    # Get user email from the form
    email = request.form['email']

    # Load current users
    users = load_users()

    # Check if the user exists
    if email in users:
        # If the user has an associated embedding folder, remove it too
        folder = users[email].get("folder")

        # Remove user from the list
        users.pop(email)
        save_users(users)

        # If a folder was defined and exists, delete it recursively
        if folder:
            folder_path = os.path.join('..', 'embeddings', folder)
            if os.path.exists(folder_path):
                shutil.rmtree(folder_path)

    # Redirect back to dashboard after deletion
    return redirect(url_for('admin.dashboard'))
