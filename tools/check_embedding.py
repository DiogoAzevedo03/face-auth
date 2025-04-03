# ============================================
# Check Embedding Script
# Author: Letícia Loureiro e Diogo Azevedo
# Date: 2025-04-03
# Description:
# This script loads a face embedding (.pkl file) and verifies:
# - If it exists
# - If it has the correct length (192 or 128)
# - If it contains valid float values
# ============================================

import pickle
import os
import numpy as np  # Para verificar tipos numpy.float32

def check_embedding(file_path):
    """Checks if the embedding exists, has valid floats, and prints preview"""
    if not os.path.exists(file_path):
        print(f"[ERROR] File not found: {file_path}")
        return

    with open(file_path, "rb") as f:
        embedding = pickle.load(f)

    print(f"\n📁 File loaded: {file_path}")
    print(f"📦 Embedding type: {type(embedding)}")
    print(f"🔢 Embedding length: {len(embedding) if hasattr(embedding, '__len__') else 'N/A'}")
    print(f"🧪 Sample content: {embedding[:5] if hasattr(embedding, '__getitem__') else embedding}")

    # Aceitar 128 ou 192 dimensões
    if len(embedding) not in [128, 192]:
        print("❌ Invalid embedding length. Expected 128 or 192.")
        return

    # Verificar se todos os valores são float ou numpy float
    if not all(isinstance(val, (float, np.floating)) for val in embedding[:10]):
        print("❌ Embedding does not contain valid float values.")
        return

    print("✅ Embedding is valid.")
    print("📊 First 10 values preview:")
    print(embedding[:10])

# === INPUT ===
file_path = input("Enter path to the embedding file (e.g., embeddings/leticia.pkl): ").strip()
check_embedding(file_path)


