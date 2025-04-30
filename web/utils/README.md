# FaceAuth - Utilities

## Overview

This folder contains **utility modules** used across the FaceAuth system.  
Its purpose is to provide reusable helper functions that support core features like authentication and user management.

---

## Files

### `user_db.py`

Handles persistent user data storage in a local JSON file (`users.json`).

#### Responsibilities:

- **Load users** from `users.json`
- **Save users** to `users.json`
- Used by both authentication and admin logic

#### Functions:

- `load_users()`
  - Returns a dictionary of all users from `users.json`
  - Returns an empty dict if the file does not exist

- `save_users(users: dict)`
  - Stores a dictionary of users to `users.json`
  - Each user contains:
    - `password` (bcrypt hash)
    - `role` (e.g., `admin`, `normal`)
    - `folder` (used for facial embeddings)

#### Example Usage:

```python
from utils.user_db import load_users, save_users

users = load_users()
users["admin@example.com"] = {
    "password": "$2b$12$...",
    "role": "admin",
    "folder": "admin_folder"
}
save_users(users)
```
### File: users.json
The actual user database stored locally on disk.
Automatically managed by user_db.py and updated when new users are registered or removed.