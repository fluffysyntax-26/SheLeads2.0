from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.routers import chat, admin
from app.db.mongo import close_database
from app.config import OLLAMA_HOST
from app.services.ollama_service import client as ollama_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"Server starting... Ollama host: {OLLAMA_HOST}")
    try:
        ollama_client.list()
        print("Connected to Ollama successfully!")
    except Exception as e:
        print(f"Warning: Could not connect to Ollama: {e}")
    yield
    await close_database()
    print("Server shutting down...")


app = FastAPI(
    title="SheLeads Backend API",
    description="Backend for SheLeads PPT with Clerk Auth and Ollama RAG",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(chat.router, prefix="/api")
app.include_router(admin.router, prefix="/api")


@app.get("/")
async def root():
    return {"status": "running", "message": "SheLeads Backend API"}


@app.get("/health")
async def health():
    return {"status": "healthy"}
