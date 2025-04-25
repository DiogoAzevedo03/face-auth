import json
import os
import bcrypt

USERS_DB = os.path.join(os.path.dirname(__file__), 'users.json')

def load_users():
    if os.path.exists(USERS_DB):
        with open(USERS_DB, 'r') as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USERS_DB, 'w') as f:
        json.dump(users, f, indent=4)

def migrate_plain_passwords():
    users = load_users()
    updated = False

    for email, info in users.items():
        pwd = info['password']
        # Verifica se a password parece já encriptada (bcrypt começa com $2b$)
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

if __name__ == "__main__":
    migrate_plain_passwords()
