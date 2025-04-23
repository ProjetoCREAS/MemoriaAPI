import os
import requests
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

from fastapi.staticfiles import StaticFiles

# Serve arquivos do plugin e da spec
app.mount("/.well-known", StaticFiles(directory=".well-known"), name="plugin-manifest")
app.mount("/", StaticFiles(directory=".", html=True), name="root-files")

# 🧩 CORS para acesso via ChatGPT Plugin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔧 Montagem de arquivos estáticos
app.mount("/.well-known", StaticFiles(directory=".well-known"), name="plugin-manifest")
app.mount("/", StaticFiles(directory=".", html=True), name="static-root")

# 🌐 Repositórios públicos
REPOSITORIOS = [
    {"nome": "HikariCalyx", "raw_base": "https://raw.githubusercontent.com/HikariCalyx/WzComparerR2-JMS/main/"},
    {"nome": "PirateIzzy", "raw_base": "https://raw.githubusercontent.com/PirateIzzy/WzComparerR2/main/"},
    {"nome": "Kagamia", "raw_base": "https://raw.githubusercontent.com/Kagamia/WzComparerR2/main/"},
    {"nome": "KENNYSOFT", "raw_base": "https://raw.githubusercontent.com/KENNYSOFT/WzComparerR2/main/"}
]

ARQUIVOS = []
if os.path.exists("arquivos_formatados.txt"):
    with open("arquivos_formatados.txt", encoding="utf-8") as f:
        ARQUIVOS = [linha.strip().strip(',').strip('"') for linha in f if linha.strip().startswith('"')]

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
                print(f"🔍 Buscando em: {url}")
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
