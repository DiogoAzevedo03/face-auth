# ============================================
# FaceAuth Web Application Backend
# File: app.py
# Authors: Diogo Azevedo and Letícia Loureiro
# Date: 2025-04-28
#
# Description:
# This is the main entry point for the FaceAuth web application.
# It initializes the Flask server, loads environment variables,
# registers route blueprints, and starts the server.
# ============================================

# === Standard Library Imports ===
import sys
import os
from flask import Flask, render_template  # Flask framework for web handling
from dotenv import load_dotenv  # Used to load environment variables from a .env file

# Add the parent directory to sys.path so Python can import modules outside /web
sys.path.append('..')

# === Load environment variables (e.g., SECRET_KEY) ===
load_dotenv()

# === Initialize Flask application ===
app = Flask(__name__)

# Secret key is used to manage session cookies securely
app.secret_key = os.getenv("SECRET_KEY")

# === Register route Blueprints ===
# These files define separate route groups for modularity
from web.routes.auth_routes import auth_bp       # Routes for login/logout
from web.routes.admin_routes import admin_bp     # Routes for admin dashboard and user control
from web.routes.face_routes import face_bp       # Routes for facial recognition and embedding management

# Ensure root directory is available in import path (safety net)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# === Core face recognition modules ===
# Used internally by the routes to detect and compare face embeddings
from recognize_m import FaceRecognizer
from generate_multiple_embeddings_m import EmbeddingGenerator

# === Register blueprints to attach their routes to the Flask app ===
app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(face_bp)

# === Route: Homepage ===
@app.route('/')
def index():
    # Render the landing page when accessing '/'
    return render_template('index.html')

# === Run Flask development server ===
if __name__ == '__main__':
    # Makes the server accessible via the network (Raspberry Pi friendly)
    app.run(host='0.0.0.0', port=5000, debug=True)
