from dotenv import load_dotenv
from os import getenv

load_dotenv()

MONGO_URI = getenv("MONGO_URI", "mongodb://localhost:27017")
CLERK_SECRET_KEY = getenv("CLERK_SECRET_KEY", "")
OLLAMA_HOST = getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = getenv("OLLAMA_MODEL", "llama3:8b")
OLLAMA_EMBED_MODEL = getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text")
QDRANT_PATH = getenv("QDRANT_PATH", "./qdrant_data")
