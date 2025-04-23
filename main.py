import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/.well-known", StaticFiles(directory=".well-known"), name="well-known")

@app.get("/openapi.yaml", include_in_schema=False)
async def get_openapi_yaml():
    return FileResponse("openapi.yaml", media_type="text/yaml")

@app.get("/icon.png", include_in_schema=False)
async def get_icon_png():
    return FileResponse("icon.png", media_type="image/png")

try:
    with open("arquivos_formatados.txt", "r", encoding="utf-8") as f:
        ARQUIVOS = [line.strip() for line in f if line.strip()]
except Exception as e:
    ARQUIVOS = []

BASE_REPO_RAW = "https://raw.githubusercontent.com/PirateIzzy/WzComparerR2/master/"

@app.get("/status")
async def status():
    return {"status": "🧠 MemoriaAPI está online!"}

@app.get("/buscarNaMemoria")
async def buscar_na_memoria(termo: str):
    if not termo:
        raise HTTPException(status_code=400, detail="Parâmetro 'termo' é obrigatório.")
    termo_lower = termo.lower()
    for arq in ARQUIVOS:
        url = BASE_REPO_RAW + arq.replace(" ", "%20")
        try:
            response = requests.get(url)
        except Exception as e:
            continue
        if response.status_code != 200:
            continue
        content = response.text
        index = content.lower().find(termo_lower)
        if index != -1:
            snippet_lines = content[index:].splitlines()[:40]
            trecho = "\n".join(snippet_lines)
            return {
    "repositorio": "PirateIzzy",   # <-- Adicione este campo
    "arquivo": arq,
    "url": url,
    "trecho": trecho
}
    return JSONResponse(status_code=404, content={"erro": "Não encontrado"})
