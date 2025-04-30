# FaceAuth - Utility Scripts

## Overview

This folder contains **administrative and utility scripts** used in the FaceAuth system.

These scripts help with:

- Migrating plain text user passwords to secure **bcrypt hashes**.
- Validating and inspecting **face embeddings (.pkl)**.
- Manually comparing embeddings for testing recognition thresholds.

---

## Scripts Available

###  `migrate_passwords.py`
Securely encrypts any **plaintext passwords** found in `users.json` using `bcrypt`.

**When to use it:**  
If you previously stored passwords as plain text, run this script to migrate them safely.

**How to run:**
```bash
python scripts/migrate_passwords.py
```
If any plain passwords are found, they will be replaced with secure bcrypt hashes.

###  check_embedding.py
Checks the integrity of a .pkl embedding file.

It will:

Verify the file exists and loads correctly.

Ensure the vector is 128 or 192 dimensions.

Print the first few values for inspection.

```bash
python scripts/check_embedding.py path/to/embedding.pkl
```

###  compare_embedding.py
Compares two face embeddings and calculates the Euclidean distance between them.

Interpretation:

Distance < 0.8 → Likely the same person

Distance < 1.3 → Possibly the same person

Distance ≥ 1.3 → Different persons or poor quality embedding

```bash
python scripts/compare_embedding.py file1.pkl file2.pkl
```

### Requirements
Install all dependencies using:


```bash
pip install -r requirements.txt
```