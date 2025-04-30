# ============================================
# User Database Utility Functions
# File: user_db.py
# Authors: Diogo Azevedo and Letícia Loureiro
# Date: 2025-04-28
#
# Description:
# This module provides helper functions for reading from and writing to
# the local user database stored in JSON format (`users.json`).
#
# It is used by authentication and administration routes to:
# - Load all registered users
# - Persist new users or updates
# ============================================

import json
import os

# Absolute path to the users.json file (one level up from this script)
USERS_DB = os.path.join(os.path.dirname(__file__), '..', 'users.json')

def load_users():
    """
    Loads all user data from the local JSON file (users.json).

    Returns:
        dict: A dictionary where each key is an email and value is a user object
              containing password hash, role and folder name.
              Returns an empty dict if the file does not exist.
    """
    if os.path.exists(USERS_DB):
        with open(USERS_DB, 'r') as f:
            return json.load(f)
    return {}

def save_users(users):
    """
    Saves the provided user dictionary to the local JSON file (users.json).

    Args:
        users (dict): A dictionary of users to be stored, where the key is the email
                      and the value contains user details (password, role, folder).
    """
    with open(USERS_DB, 'w') as f:
        json.dump(users, f, indent=4)
