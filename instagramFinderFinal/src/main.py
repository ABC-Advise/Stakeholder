from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import platform
import psutil

# Importar routers da API
from src.api.v1.endpoints import profiles as profiles_v1
from src.routes.profile_finder_routes import router as profile_finder_router

# Carrega as variáveis de ambiente
load_dotenv()

# Configuração do CORS
BACKEND_CORS_ORIGINS = os.getenv(
    "BACKEND_CORS_ORIGINS",
    "http://localhost:3000,http://localhost:8000,https://frontend-stakeholder-production.up.railway.app"
).split(",")

app = FastAPI(
    title="Instagram Profile Finder API",
    description="API para buscar e validar perfis do Instagram.",
    version="0.1.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in BACKEND_CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos os métodos
    allow_headers=["*"],  # Permite todos os headers
    expose_headers=["*"],  # Expõe todos os headers
    max_age=3600,  # Cache das configurações CORS por 1 hora
)

@app.get("/health", tags=["Health"])
async def health_check():
    """Verifica a saúde da API e retorna informações do sistema."""
    return {
        "status": "ok",
        "version": "0.1.0",
        "environment": os.getenv("ENVIRONMENT", "development"),
        "system": {
            "platform": platform.system(),
            "python_version": platform.python_version(),
            "memory_usage": f"{psutil.Process().memory_info().rss / 1024 / 1024:.2f} MB",
            "cpu_percent": psutil.cpu_percent()
        }
    }

@app.get("/")
async def root():
    return {
        "message": "Bem-vindo à API do Instagram Finder",
        "docs_url": "/docs",
        "health_check": "/health"
    }

# Incluir routers da API
app.include_router(profiles_v1.router, prefix="/api/v1", tags=["Profiles V1"])
app.include_router(profile_finder_router, prefix="/api/v1", tags=["Profile Finder"])

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port) 