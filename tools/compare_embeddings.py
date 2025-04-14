# ============================================
# Compare Embeddings Script (192D)
# Author: Diogo Azevedo e Letícia Loureiro
# Date: 2025-04-03
# Description:
# Compares two .pkl embeddings (NumPy arrays)
# and calculates Euclidean distance.
# Note: This script is an auxiliary tool for manual testing.
# It is not used during real-time recognition, but helps verify the distance between two face embeddings.
# ============================================

import pickle
import numpy as np
import os

def load_embedding(file_path):
    """Loads a .pkl embedding file and validates it"""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"[ERROR] File not found: {file_path}")
    
    with open(file_path, "rb") as f:
        embedding = pickle.load(f)

    if not isinstance(embedding, np.ndarray):
        raise ValueError("Invalid embedding type: expected numpy.ndarray")
    
    if len(embedding) != 192:
        raise ValueError(f"Invalid embedding length: expected 192, got {len(embedding)}")

    return embedding

# === INPUT ===
file1 = input("Enter path to first embedding (e.g., embeddings/leticia.pkl): ").strip()
file2 = input("Enter path to second embedding (e.g., embeddings/leticia1.pkl): ").strip()

try:
    emb1 = load_embedding(file1)
    emb2 = load_embedding(file2)

    # === DISTANCE ===
    distance = np.linalg.norm(emb1 - emb2)
    print(f"\nDistance between embeddings: {distance:.4f}")

    # === INTERPRETATION ===
    if distance < 0.8:
        print("Same person (high similarity)")
    elif distance < 1.3:
        print("Possibly the same person (medium similarity)")
    else:
        print("Different person or bad capture (low similarity)")


except Exception as e:
    print(e)
