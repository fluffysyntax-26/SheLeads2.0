import json
import os
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter
from app.config import QDRANT_PATH
from app.services.ollama_service import get_embedding

os.makedirs(QDRANT_PATH, exist_ok=True)
client = QdrantClient(path=QDRANT_PATH)
COLLECTION_NAME = "schemes"


def load_schemes_from_json(filepath: str) -> list[dict]:
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    schemes = []
    for item in data:
        fields = item.get("fields", {})
        scheme_id = item.get("id", "")

        text = f"""
Scheme: {fields.get("schemeName", "")}
Category: {", ".join(fields.get("schemeCategory", []))}
For: {fields.get("schemeFor", "")}
Level: {fields.get("level", "")}
Ministry: {fields.get("nodalMinistryName", "")}
Description: {fields.get("briefDescription", "")}
Tags: {", ".join(fields.get("tags", []))}
States: {", ".join(fields.get("beneficiaryState", []))}
"""

        metadata = {
            "schemeName": fields.get("schemeName", ""),
            "schemeFor": fields.get("schemeFor", ""),
            "level": fields.get("level", ""),
            "ministry": fields.get("nodalMinistryName", ""),
            "description": fields.get("briefDescription", ""),
            "categories": ", ".join(fields.get("schemeCategory", [])),
            "tags": ", ".join(fields.get("tags", [])),
            "states": ", ".join(fields.get("beneficiaryState", [])),
            "slug": fields.get("slug", ""),
        }

        schemes.append({"id": scheme_id, "text": text.strip(), "metadata": metadata})

    return schemes


def initialize_collection():
    collections = client.get_collections().collections
    collection_names = [c.name for c in collections]

    if COLLECTION_NAME not in collection_names:
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=768, distance=Distance.COSINE),
        )
        print(f"Created collection: {COLLECTION_NAME}")

    return COLLECTION_NAME


def vectorize_schemes(filepath: str = "myscheme_rag_dataset.json"):
    initialize_collection()

    existing = client.count(collection_name=COLLECTION_NAME).count
    if existing > 0:
        print(f"Collection already has {existing} schemes. Skipping vectorization.")
        return {"status": "already_exists", "count": existing}

    print("Loading schemes from JSON...")
    schemes = load_schemes_from_json(filepath)
    print(f"Loaded {len(schemes)} schemes. Generating embeddings...")

    points = []
    for i, scheme in enumerate(schemes):
        if i % 100 == 0:
            print(f"Processing scheme {i}/{len(schemes)}...")

        embedding = get_embedding(scheme["text"])
        
        # Use slug as the ID if available in metadata, otherwise use the provided ID
        slug = scheme["metadata"].get("slug", scheme["id"])

        points.append(
            PointStruct(
                id=i,
                vector=embedding,
                payload={
                    "scheme_id": slug,
                    "text": scheme["text"],
                    **scheme["metadata"],
                },
            )
        )

    client.upsert(collection_name=COLLECTION_NAME, points=points)

    print(f"Successfully vectorized {len(schemes)} schemes.")
    return {"status": "success", "count": len(schemes)}


def search_schemes(query: str, n_results: int = 5) -> list[dict]:
    initialize_collection()

    count = client.count(collection_name=COLLECTION_NAME).count
    if count == 0:
        # Auto-vectorize if empty
        print("Database empty. Auto-triggering vectorization...")
        vectorize_schemes()
        count = client.count(collection_name=COLLECTION_NAME).count
        if count == 0:
             raise ValueError("Failed to vectorize schemes.")

    query_embedding = get_embedding(query)

    results = client.query_points(
        collection_name=COLLECTION_NAME, query=query_embedding, limit=n_results
    )

    if hasattr(results, "result"):
        points = results.result
    elif hasattr(results, "points"):
        points = results.points
    else:
        points = list(results)

    schemes = []
    for point in points:
        if hasattr(point, "payload"):
            payload = point.payload
        else:
            payload = point[1] if isinstance(point, tuple) else {}

        schemes.append(
            {
                "id": payload.get(
                    "scheme_id", str(point.id) if hasattr(point, "id") else ""
                ),
                "text": payload.get("text", ""),
                "metadata": {
                    "schemeName": payload.get("schemeName", ""),
                    "schemeFor": payload.get("schemeFor", ""),
                    "level": payload.get("level", ""),
                    "ministry": payload.get("ministry", ""),
                    "description": payload.get("description", ""),
                    "categories": payload.get("categories", ""),
                    "tags": payload.get("tags", ""),
                    "states": payload.get("states", ""),
                },
            }
        )

    return schemes
