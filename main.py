#Emprestimo-Facil\main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.api import auth, clientes, emprestimos, usuarios
from app.core.config import settings
from app.db.database import engine, Base
import logging

# Configuração de logging
logging.basicConfig(level=settings.LOGGING_LEVEL)
logger = logging.getLogger(__name__)

# Criação das tabelas do banco de dados
def create_tables():
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Tabelas do banco de dados criadas com sucesso.")
    except Exception as e:
        logger.error(f"Erro ao criar tabelas do banco de dados: {e}")
        raise

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Iniciando a aplicação: {settings.PROJECT_NAME}")
    if settings.is_development:
        logger.info("Estamos em ambiente de desenvolvimento!")
    create_tables()
    yield
    logger.info("Encerrando a aplicação...")

# Inicialização da aplicação
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API para o sistema de Empréstimo Fácil",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Configuração de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclusão dos routers
app.include_router(auth.router, prefix=settings.API_V1_STR + "/auth", tags=["Autenticação"])
app.include_router(usuarios.router, prefix=settings.API_V1_STR + "/usuarios", tags=["Usuários"])
app.include_router(clientes.router, prefix=settings.API_V1_STR + "/clientes", tags=["Clientes"])
app.include_router(emprestimos.router, prefix=settings.API_V1_STR + "/emprestimos", tags=["Empréstimos"])

@app.get("/")
def read_root():
    return {"message": "Bem-vindo ao sistema Empréstimo Fácil!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)