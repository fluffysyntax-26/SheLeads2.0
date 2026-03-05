from fastapi import APIRouter
from app.models.schemas import VectorizeResponse
from app.services.vector_service import vectorize_schemes

router = APIRouter()


@router.post("/admin/vectorize", response_model=VectorizeResponse)
async def vectorize():
    result = vectorize_schemes()
    return VectorizeResponse(**result)
