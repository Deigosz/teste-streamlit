import os
import json
import time

FICHAS_FILE = "fichas.json"
BASE_PATH = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_PATH, "db")
os.makedirs(DB_PATH, exist_ok=True)

def carregar_fichas():
    caminho = os.path.join(DB_PATH, FICHAS_FILE)
    if os.path.exists(caminho):
        with open(caminho, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"sheets": []}

def salvar_fichas(fichas):
    caminho = os.path.join(DB_PATH, FICHAS_FILE)
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(fichas, f, ensure_ascii=False, indent=2)

def criar_ficha(nome_ficha):
    timestamp = time.time()
    return {
        "id": f"sheet_{int(timestamp)}",
        "name": nome_ficha,
        "createdAt": timestamp
    }

def listar_fichas():
    fichas = carregar_fichas()
    return [sheet["name"] for sheet in fichas["sheets"]]

# --- Teste correto ---

# fichas_data = carregar_fichas()
# ficha = criar_ficha("teste")
# fichas_data["sheets"].append(ficha)
# salvar_fichas(fichas_data)

# print(listar_fichas())
