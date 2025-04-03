# 🧰 FaceAuth - Tools

## 📄 Overview

Esta pasta contém scripts utilitários para **validar** e **comparar** ficheiros de embeddings faciais (`.pkl`) usados no projeto **FaceAuth**.

Estes scripts são úteis para garantir que:
- Os embeddings gerados estão no formato correto.
- A comparação entre rostos funciona conforme esperado.

---

## ▶️ Como executar

### 1. Instalar dependências

Certifica-te que tens os requisitos instalados:

pip install numpy

### 2. Verificar um embedding

Executa o seguinte comando para verificar se um embedding .pkl é válido:

python tools/check_embedding.py

### 3. Comparar dois embeddings
Executa o seguinte comando para calcular a distância entre dois ficheiros .pkl:

python tools/compare_embedding.py

📂 Nota: Os ficheiros .pkl devem conter embeddings gerados por generate_face_embedding.py, com 128 ou 192 dimensões.

## 🎯 Objetivo de cada script
### check_embedding.py
✔️ Verifica se um ficheiro .pkl:

Existe no caminho fornecido.

Tem o número correto de dimensões (128 ou 192).

Contém apenas valores do tipo float ou numpy.float32.

Mostra os primeiros valores para visualização.

✅ Ideal para garantir que um embedding está pronto para ser usado no reconhecimento facial.

### compare_embedding.py
📊 Compara dois ficheiros .pkl e calcula a distância euclidiana entre eles:

Distância < 0.8 → ✅ Mesma pessoa (alta similaridade)

Distância < 1.3 → 🟡 Provavelmente a mesma pessoa

Distância ≥ 1.3 → ❌ Pessoas diferentes ou má captura

🔍 Muito útil para verificar manualmente se duas capturas representam a mesma pessoa.