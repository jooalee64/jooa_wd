from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(title="RoomDesigner API", version="1.0.0")

class FurnitureItemSchema(BaseModel):
    id: str
    name: str
    category: str
    style: str
    price: float
    image_url: str
    embedding_vector: List[float]

# Mock Database Repository
CATALOG_DB = [
    {
        "id": "item_01",
        "name": "Kalon Oak Lounge Chair",
        "category": "Seating",
        "style": "Japandi",
        "price": 450.0,
        "image_url": "https://cdn.example.com/chair.jpg",
        "embedding_vector": [0.12, 0.85, 0.43]
    }
]

@app.get("/api/v1/catalog", response_model=List[FurnitureItemSchema])
async def get_catalog(style: Optional[str] = None, max_price: Optional[float] = None):
    results = CATALOG_DB
    if style:
        results = [i for i in results if i["style"].lower() == style.lower()]
    if max_price:
        results = [i for i in results if i["price"] <= max_price]
    return results