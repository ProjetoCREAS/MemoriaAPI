import requests
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# Servindo arquivos estáticos
app.mount("/.well-known", StaticFiles(directory=".well-known"), name="well-known")
app.mount("/", StaticFiles(directory=".", html=True), name="static-root")

REPOSITORIOS = [
    {"nome": "HikariCalyx", "raw_base": "https://raw.githubusercontent.com/HikariCalyx/WzComparerR2-JMS/main/"},
    {"nome": "PirateIzzy", "raw_base": "https://raw.githubusercontent.com/PirateIzzy/WzComparerR2/main/"},
    {"nome": "Kagamia", "raw_base": "https://raw.githubusercontent.com/Kagamia/WzComparerR2/main/"},
    {"nome": "KENNYSOFT", "raw_base": "https://raw.githubusercontent.com/KENNYSOFT/WzComparerR2/main/"}
]

with open("arquivos_formatados.txt", encoding="utf-8") as f:
    ARQUIVOS = [linha.strip().strip(',').strip('"') for linha in f if linha.strip().startswith('"')]

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
