"""
Teste de Funcionamento da Câmara com Picamera2

Autor: Diogo Azevedo
Data: 2025-03-20
Descrição:
Este script testa se a câmara está funcional utilizando a biblioteca Picamera2.
Abre uma janela com a imagem captada em tempo real durante 60 segundos.
"""

from picamera2 import Picamera2, Preview  # Importa a classe da câmara e o tipo de visualização
from time import sleep  # Importa função para pausar a execução

# Inicializa a câmara
picam2 = Picamera2()

# Inicia a pré-visualização com interface gráfica (QT)
picam2.start_preview(Preview.QTGL)

# Inicia a captura da câmara
picam2.start()

# Aguarda 60 segundos enquanto a câmara está ativa
sleep(60)

# Fecha a câmara e termina a visualização
picam2.close()
