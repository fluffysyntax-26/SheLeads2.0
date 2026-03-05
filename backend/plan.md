This is a very smart pivot. In a hackathon, you want to nail the core logic (extracting data and matching schemes) before adding the fancy audio layers.

Running Ollama on your friend’s machine while your backend runs on yours is a classic, highly effective hackathon setup (especially if their laptop has a better GPU!).

Here is the exact step-by-step guide on how to expose your friend's Ollama server, the updated folder structure, and the FastAPI code to extract perfect JSON.

---

### Step 1: Setting up Ollama on your Friend's System

By default, Ollama only listens to `localhost` (the laptop it is running on). You need to open it up so your backend can talk to it over the network.

**If you and your friend are on the SAME Wi-Fi network:**

1. **On your friend's laptop**, they need to set an environment variable to allow outside connections.
* **Mac/Linux:** Open terminal and run: `export OLLAMA_HOST="0.0.0.0"`
* **Windows (Command Prompt):** Run: `set OLLAMA_HOST=0.0.0.0`
* **Windows (PowerShell):** Run: `$env:OLLAMA_HOST="0.0.0.0"`


2. While that terminal is still open, they need to start the server by typing: `ollama serve`
3. Find your friend's local IP address (usually starts with `192.168.x.x`).
4. **Your connection URL** will be: `http://<FRIEND_IP>:11434`

**If you and your friend are on DIFFERENT Wi-Fi networks (Remote):**

1. Ask your friend to download and install [Ngrok](https://ngrok.com/).
2. Your friend starts their Ollama server normally (`ollama serve`).
3. In a new terminal, your friend runs: `ngrok http 11434`
4. Ngrok will give them a public URL that looks like `https://a1b2c3d4.ngrok-free.app`.
5. **Your connection URL** will be that Ngrok link.

---

### Step 2: The Streamlined Folder Structure

We will strip out the Sarvam stuff for now and focus purely on the text-to-JSON extraction pipeline.

```text
ai_caseworker_backend/
├── main.py                  # FastAPI server
├── requirements.txt         # pip install fastapi uvicorn ollama pydantic
├── app/
│   ├── api/
│   │   └── chat.py          # The endpoint receiving user text
│   ├── services/
│   │   └── ollama_service.py # The logic connecting to your friend's PC
│   └── models/
│       └── schemas.py       # Pydantic models for input/output

```

---

### Step 3: The Code Implementation

Here is how you actually build this. We will use Ollama's native `format='json'` feature, which forces the LLM to output clean, valid JSON instead of conversational text.

#### 1. `app/models/schemas.py`

This defines what the frontend will send to your backend.

```python
from pydantic import BaseModel

class UserInput(BaseModel):
    user_id: str
    message: str

class ExtractedInfo(BaseModel):
    age: int | None = None
    gender: str | None = None
    occupation: str | None = None
    state: str | None = None
    income: int | None = None

```

#### 2. `app/services/ollama_service.py`

This is the brain. It connects to your friend's computer and forces the LLM to extract the demographics.

```python
from ollama import Client
import json

# Replace this with your friend's IP or Ngrok URL
OLLAMA_HOST_URL = "http://192.168.1.100:11434" 
MODEL_NAME = "llama3" # or 'mistral', whatever your friend has pulled

# Initialize the client pointing to your friend's PC
client = Client(host=OLLAMA_HOST_URL)

def extract_demographics(user_text: str) -> dict:
    prompt = f"""
    You are an intelligent data extraction assistant. 
    Extract the following demographic information from the user's text: age, gender, occupation, state, and income.
    If a piece of information is not mentioned, set its value to null.
    
    User's text: "{user_text}"
    
    Return ONLY a valid JSON object.
    """

    try:
        # We pass format='json' to guarantee the LLM doesn't reply with "Here is your JSON:"
        response = client.chat(
            model=MODEL_NAME,
            messages=[{'role': 'user', 'content': prompt}],
            format='json'
        )
        
        # Parse the string response into a Python dictionary
        json_data = json.loads(response['message']['content'])
        return json_data
        
    except Exception as e:
        print(f"Error connecting to Ollama: {e}")
        return {}

```

#### 3. `app/api/chat.py`

This is the route your frontend will call.

```python
from fastapi import APIRouter
from app.models.schemas import UserInput
from app.services.ollama_service import extract_demographics

router = APIRouter()

@router.post("/process_message")
async def process_message(data: UserInput):
    print(f"Received message from {data.user_id}: {data.message}")
    
    # 1. Send the text to your friend's Ollama server
    extracted_json = extract_demographics(data.message)
    
    # 2. In the future, this is where you will update the user's MongoDB profile
    # update_user_profile(data.user_id, extracted_json)
    
    # 3. Return the extracted data to the frontend so you can see it working
    return {
        "status": "success",
        "extracted_data": extracted_json,
        "next_step": "Ready to query MongoDB Vector Search with this data!"
    }

```

#### 4. `main.py`

The entry point to run your server.

```python
from fastapi import FastAPI
from app.api import chat

app = FastAPI(title="AI Caseworker API")

# Include the router we just made
app.include_router(chat.router, prefix="/api")

@app.get("/")
def health_check():
    return {"status": "Backend is running!"}

# Run this using: uvicorn main:app --reload

```

### The Developer POV Workflow

1. Your friend starts their Ollama server on `0.0.0.0` or Ngrok.
2. You run `uvicorn main:app --reload` on your laptop.
3. You open Postman (or your frontend) and send a POST request to `http://localhost:8000/api/process_message` with this body:
```json
{
  "user_id": "clerk_123",
  "message": "Hi, I'm a 24-year-old woman living in Karnataka working as a farmer."
}

```


4. Your FastAPI server catches it, builds the strict extraction prompt, and fires it over the network to your friend's laptop.
5. Your friend's GPU processes the text, generates a clean JSON object, and sends it back.
6. Your API returns:
```json
{
  "status": "success",
  "extracted_data": {
    "age": 24,
    "gender": "woman",
    "occupation": "farmer",
    "state": "Karnataka",
    "income": null
  },
  "next_step": "Ready to query MongoDB Vector Search with this data!"
}

```



By using the native `format='json'` parameter in the Ollama client, you completely eliminate the risk of the LLM ruining your code by adding conversational text around the JSON block.

Does this setup make sense for you and your friend?