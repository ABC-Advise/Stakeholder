from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Importar routers da API
from src.api.v1.endpoints import profiles as profiles_v1
from src.routes.profile_finder_routes import router as profile_finder_router

# Carrega as variáveis de ambiente
load_dotenv()

app = FastAPI(
    title="Instagram Profile Finder API",
    description="API para buscar e validar perfis do Instagram.",
    version="0.1.0"
)

# Configurar CORS (Cross-Origin Resource Sharing)
# Permite que seu front-end (mesmo em outro domínio/porta) acesse a API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, restrinja para o domínio do seu front-end
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

@app.get("/health", tags=["Health"])
async def health_check():
    """Verifica a saúde da API."""
    return {"status": "ok"}

@app.get("/")
async def root():
    return {"message": "Bem-vindo à API do Instagram Finder"}

# Incluir routers da API
app.include_router(profiles_v1.router, prefix="/api/v1", tags=["Profiles V1"])
app.include_router(profile_finder_router, prefix="/api/v1", tags=["Profile Finder"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 