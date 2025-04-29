# ============================================
# Password Migration Script for User Database
# File: users_migration.py
# Author: Diogo Azevedo
# Date: 2025-04-29
#
# Description:
# This utility script scans the user database (users.json) and
# encrypts any plaintext passwords using bcrypt hashing.
#
# It is intended to be run once to securely migrate legacy user data.
# ============================================

import json
import os
import bcrypt

# Path to the JSON file that stores user data
USERS_DB = os.path.join(os.path.dirname(__file__), 'users.json')

def load_users():
    """
    Loads all users from the local JSON file.

    Returns:
        dict: Dictionary containing user data (email as key).
    """
    if os.path.exists(USERS_DB):
        with open(USERS_DB, 'r') as f:
            return json.load(f)
    return {}

def save_users(users):
    """
    Saves the provided dictionary of users to the JSON file.

    Args:
        users (dict): Dictionary with updated user data.
    """
    with open(USERS_DB, 'w') as f:
        json.dump(users, f, indent=4)

def migrate_plain_passwords():
    """
    Checks each user in the database and encrypts plaintext passwords using bcrypt.
    If a password is already hashed (starts with "$2b$"), it is skipped.
    This function ensures secure storage of all passwords.
    """
    users = load_users()
    updated = False

    for email, info in users.items():
        pwd = info['password']

        # Skip users whose passwords are already hashed
        if not pwd.startswith("$2b$"):
            print(f"Encrypting password for {email}")
            hashed = bcrypt.hashpw(pwd.encode(), bcrypt.gensalt()).decode()
            info['password'] = hashed
            updated = True

    if updated:
        save_users(users)
        print("Passwords updated successfully!")
    else:
        print("No plain text passwords found.")

# Entry point of the script — only runs when executed directly
if __name__ == "__main__":
    migrate_plain_passwords()
