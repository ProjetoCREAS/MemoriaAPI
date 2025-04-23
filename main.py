import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# Allow CORS for any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for the ChatGPT plugin (ai-plugin.json in .well-known, openapi.yaml and icon.png in root)
app.mount("/.well-known", StaticFiles(directory=".well-known"), name="well-known")

@app.get("/openapi.yaml", include_in_schema=False)
async def get_openapi_yaml():
    return FileResponse("openapi.yaml", media_type="text/yaml")

@app.get("/icon.png", include_in_schema=False)
async def get_icon_png():
    return FileResponse("icon.png", media_type="image/png")

# Load list of files from arquivos_formatados.txt
try:
    with open("arquivos_formatados.txt", "r", encoding="utf-8") as f:
        ARQUIVOS = [line.strip() for line in f if line.strip()]
except Exception as e:
    ARQUIVOS = []
    # Optionally log the error if needed
    # print(f"Erro ao carregar arquivos_formatados.txt: {e}")

# Base URL for raw files in the GitHub repository
BASE_REPO_RAW = "https://raw.githubusercontent.com/PirateIzzy/WzComparerR2/main/"

@app.get("/status")
async def status():
    return {"status": "🧠 MemoriaAPI está online!"}

@app.get("/buscarNaMemoria")
async def buscar_na_memoria(termo: str):
    # Validate query parameter
    if not termo:
        raise HTTPException(status_code=400, detail="Parâmetro 'termo' é obrigatório.")

    termo_lower = termo.lower()
    for arq in ARQUIVOS:
        url = BASE_REPO_RAW + arq.replace(" ", "%20")
        try:
            response = requests.get(url)
        except Exception as e:
            # If a request fails, skip to the next file
            continue

        if response.status_code != 200:
            # Skip files that cannot be retrieved
            continue

        content = response.text
        index = content.lower().find(termo_lower)
        if index != -1:
            # Term found in this file
            # Capture a snippet of up to 40 lines starting from the occurrence
            snippet_lines = content[index:].splitlines()[:40]
            trecho = "\n".join(snippet_lines)
            return {"arquivo": arq, "trecho": trecho}

    # If the term was not found in any file, return 404
    return JSONResponse(status_code=404, content={"erro": "Não encontrado"})
