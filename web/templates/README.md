# FaceAuth - HTML Templates

## Overview

This directory contains all the **Jinja2 HTML templates** rendered by Flask routes in the FaceAuth system.

These templates define the structure, layout, and logic for the user interface of the platform.

---

## Files

### `index.html`
- Landing page of the application.
- Presents a welcome message and a button to start face recognition login.

### `login.html`
- Manual login interface for users.
- Allows users to enter email and password to authenticate as a fallback to face recognition.

### `face_login.html`
- Interface for logging in with a webcam.
- Uses JavaScript to capture a live image from the camera and send it to the backend for face recognition.

### `dashboard.html`
- Admin dashboard.
- Displays a list of registered users with the ability to add or remove users.

### `generate.html`
- Admin interface for creating a new user and capturing their face embeddings.
- Streams webcam video and overlays bounding boxes for real-time face detection.

### `user.html`
- Dashboard for authenticated normal users.
- Displays basic session information (email, login time) and logout options.

---

## Notes

- All templates use **Jinja2 syntax** for dynamic content rendering, such as `{{ session['user'] }}` or `{% for user in users %}`.
- Static assets like CSS are included using:
  
  ```html
  <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
  ```
Navigation between routes is done via Flask's url_for to ensure consistent URL generation.

## Usage
Templates are rendered from Flask routes like this:

  ```bash
return render_template("login.html")
```
They receive variables from the backend (e.g., users, session, or error) and use them to conditionally display information.