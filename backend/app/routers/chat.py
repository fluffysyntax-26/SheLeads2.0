from fastapi import APIRouter, Depends
from app.auth.clerk import get_current_user
from app.models.schemas import UserInput, ChatResponse, ExtractedInfo, SchemeResult
from app.services.ollama_service import extract_user_info, chat_with_context
from app.services.vector_service import search_schemes

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(
    data: UserInput,
    user_id: str = Depends(get_current_user),
):
    user_profile = extract_user_info(data.message)

    search_query = f"""
    Age: {user_profile.get("age")}
    Gender: {user_profile.get("gender")}
    Occupation: {user_profile.get("occupation")}
    State: {user_profile.get("state")}
    Income: {user_profile.get("income")}
    Query: {data.message}
    """

    schemes = search_schemes(search_query, n_results=5)

    context = "\n\n".join([s["text"] for s in schemes])

    response = chat_with_context(
        prompt=data.message, context=context, user_profile=user_profile
    )

    return ChatResponse(
        status="success",
        user_profile=ExtractedInfo(**user_profile),
        schemes=[SchemeResult(**s) for s in schemes],
        response=response,
    )
