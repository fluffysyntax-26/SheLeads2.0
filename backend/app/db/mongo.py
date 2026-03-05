from motor.motor_asyncio import AsyncIOMotorClient
from app.config import MONGO_URI

_client = None
_db = None


async def get_database():
    global _client, _db
    if _client is None:
        _client = AsyncIOMotorClient(MONGO_URI)
        _db = _client["sheleads"]
    return _db


async def close_database():
    global _client
    if _client:
        _client.close()
        _client = None
