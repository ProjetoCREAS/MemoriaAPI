import os
import requests
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# 🔓 CORS para ChatGPT Plugin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🌐 Forks públicos a consultar
REPOSITORIOS = [
    {"nome": "HikariCalyx", "raw_base": "https://raw.githubusercontent.com/HikariCalyx/WzComparerR2-JMS/main/"},
    {"nome": "PirateIzzy", "raw_base": "https://raw.githubusercontent.com/PirateIzzy/WzComparerR2/main/"},
    {"nome": "Kagamia", "raw_base": "https://raw.githubusercontent.com/Kagamia/WzComparerR2/main/"},
    {"nome": "KENNYSOFT", "raw_base": "https://raw.githubusercontent.com/KENNYSOFT/WzComparerR2/main/"}
]

# 📄 Carrega a lista de arquivos do txt, se existir
ARQUIVOS = []
if os.path.exists("arquivos_formatados.txt"):
    with open("arquivos_formatados.txt", encoding="utf-8") as f:
        ARQUIVOS = [linha.strip().strip(',').strip('"') for linha in f if linha.strip().startswith('"')]

# 🧠 Status básico
@app.get("/status")
async def status():
    return {"status": "🧠 MemoriaAPI está online!"}

# 🔍 Endpoint de busca principal
@app.get("/buscarNaMemoria")
async def buscar_na_memoria(termo: str):
    for repo in REPOSITORIOS:
        for arq in ARQUIVOS:
            url = repo["raw_base"] + arq.replace(" ", "%20")
            try:
                r = requests.get(url, timeout=5)
                if r.status_code == 200 and termo in r.text:
                    i = r.text.find(termo)
                    trecho = "\n".join(r.text[i:].splitlines()[:40])
                    return {
                        "repositorio": repo["nome"],
                        "arquivo": arq,
                        "url": url,
                        "trecho": trecho
                    }
            except requests.RequestException:
                continue
    return JSONResponse(status_code=404, content={"erro": "Nenhum código correspondente foi encontrado."})
