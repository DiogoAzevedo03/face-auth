# ============================================
# Real-Time Face Recognition Script
# Author: Diogo Azevedo e Letícia Loureiro
# Date: 2025-04-03
# Description:
# Captura imagens da câmara, extrai o embedding facial
# e compara com os embeddings guardados (.pkl) para
# identificar o utilizador.
# ============================================

import cv2
import os
import numpy as np
import pickle
from picamera2 import Picamera2
from time import sleep
import tflite_runtime.interpreter as tflite  # <-- ALTERADO AQUI 🔥

# Carregar modelo TFLite
interpreter = tflite.Interpreter(model_path="models/mobilefacenet.tflite")
interpreter.allocate_tensors()

input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

# Diretório com embeddings de utilizadores registados
EMBEDDINGS_DIR = "embeddings/"
THRESHOLD = 1.0  # Limiar de decisão para considerar a mesma pessoa

def preprocess_image(image):
    """Pré-processa imagem para o modelo (redimensiona e normaliza)"""
    if image.shape[2] == 4:
        image = cv2.cvtColor(image, cv2.COLOR_RGBA2RGB)  # <-- CONVERTER AQUI
    resized = cv2.resize(image, (112, 112))
    normalized = resized.astype('float32') / 255.0
    return np.expand_dims(normalized, axis=0)


def get_embedding(image):
    """Extrai embedding facial usando o modelo TFLite"""
    input_data = preprocess_image(image)
    interpreter.set_tensor(input_details[0]['index'], input_data)
    interpreter.invoke()
    embedding = interpreter.get_tensor(output_details[0]['index'])[0]
    return embedding

def load_known_embeddings():
    """Carrega todos os embeddings guardados"""
    known = {}
    for file in os.listdir(EMBEDDINGS_DIR):
        if file.endswith(".pkl"):
            path = os.path.join(EMBEDDINGS_DIR, file)
            with open(path, "rb") as f:
                known[file.replace(".pkl", "")] = pickle.load(f)
    return known

def recognize_face(embedding, known_embeddings):
    """Compara embedding com os existentes e retorna o nome (ou desconhecido)"""
    for name, known_emb in known_embeddings.items():
        distance = np.linalg.norm(embedding - known_emb)
        if distance < THRESHOLD:
            return name, distance
    return "Desconhecido", None

def main():
    print("🎥 A iniciar reconhecimento facial em tempo real...")
    picam2 = Picamera2()
    picam2.start()
    sleep(2)  # Esperar pela câmara

    known_embeddings = load_known_embeddings()

    while True:
        frame = picam2.capture_array()
        face_embedding = get_embedding(frame)
        name, dist = recognize_face(face_embedding, known_embeddings)

        if name != "Desconhecido":
            print(f"✅ {name} reconhecido (distância: {dist:.4f})")
        else:
            print("❌ Rosto não reconhecido.")

        # Esperar para não sobrecarregar o sistema
        sleep(2)

try:
    main()
except KeyboardInterrupt:
    print("\n🛑 Reconhecimento terminado pelo utilizador.")
