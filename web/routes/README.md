# FaceAuth - Route Handlers

## Overview

This folder contains all **Flask Blueprint route definitions** for the FaceAuth system.  
Each file is responsible for handling a specific group of routes and rendering the appropriate views or JSON responses.

---

## Files in this directory

### `auth_routes.py`
Handles user authentication:

- `/login`: Manual login via email and password.
- `/logout`: Logs out the current session.
- `/face-login` (GET): Loads the facial login camera interface.
- `/face-login` (POST): Accepts image input and attempts to recognize the user.
- `/user`: Displays a protected user-only page after successful login.

 Uses `FaceRecognizer` to validate faces against pre-generated embeddings.

---

###  `admin_routes.py`
Manages administrator-specific actions:

- `/admin/dashboard`: Displays a list of all users in the system.
- `/admin/add`: Allows admin to manually add new users.
- `/admin/remove`: Allows admin to remove users and their embedding data.
- `/admin/logout`: Logs out the admin session.

---

###  `face_routes.py`
Handles routes related to face **registration and embedding creation**:

- `/admin/generate`: Loads the admin interface to register a new user with webcam.
- `/admin/create-user`: Receives a JSON payload to create a new user entry in `users.json`.
- `/admin/save-embedding`: Accepts webcam frames, extracts face crops, and saves face embeddings in `.pkl` format.

 Uses `EmbeddingGenerator` to generate and store face vectors.

---

##  Notes

- All route files use **Flask Blueprints** for modular organization.
- Authentication is stored in Flask sessions.
- Passwords are securely hashed using **bcrypt**.
- Embeddings are stored under the `embeddings/` directory.

---

##  Related Folders

- `web/templates/` → Contains the HTML templates used by these routes.
- `web/static/` → CSS and frontend assets.
- `utils/` → Includes helper modules like `user_db.py`.

---
