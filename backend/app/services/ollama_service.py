import ollama
from app.config import OLLAMA_HOST, OLLAMA_MODEL, OLLAMA_EMBED_MODEL

client = ollama.Client(host=OLLAMA_HOST)


def get_embedding(text: str) -> list[float]:
    response = client.embeddings(
        model=OLLAMA_EMBED_MODEL,
        prompt=text,
    )
    return response["embedding"]


def chat_with_context(prompt: str, context: str, user_profile: dict = None) -> str:
    profile_info = ""
    if user_profile:
        profile_info = f"""
User Profile:
- Age: {user_profile.get("age", "Not specified")}
- Gender: {user_profile.get("gender", "Not specified")}
- Occupation: {user_profile.get("occupation", "Not specified")}
- State: {user_profile.get("state", "Not specified")}
- Income: {user_profile.get("income", "Not specified")}
"""

    full_prompt = f"""You are a helpful government scheme recommendation assistant. 
Based on the user's profile and the following scheme information, recommend the most relevant schemes to the user.

{profile_info}
Available Schemes (use this context to answer):
{context}

User Question: {prompt}

Provide a helpful response with relevant scheme names and details. Be concise but informative."""

    response = client.chat(
        model=OLLAMA_MODEL,
        messages=[{"role": "user", "content": full_prompt}],
    )
    return response["message"]["content"]


def extract_user_info(user_text: str) -> dict:
    prompt = f"""
Extract the following demographic information from the user's text. 
If a piece of information is not mentioned, set its value to null.

User's text: "{user_text}"

Return ONLY a valid JSON object with these fields: age, gender, occupation, state, income.
"""

    response = client.chat(
        model=OLLAMA_MODEL,
        messages=[{"role": "user", "content": prompt}],
        format={
            "type": "object",
            "properties": {
                "age": {"type": "integer"},
                "gender": {"type": "string"},
                "occupation": {"type": "string"},
                "state": {"type": "string"},
                "income": {"type": "integer"},
            },
        },
    )
    import json

    return json.loads(response["message"]["content"])
