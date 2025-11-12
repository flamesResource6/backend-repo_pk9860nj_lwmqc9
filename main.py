import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from schemas import MenuItem, Review, Order

app = FastAPI(title="Flame & Wrap Co. API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Flame & Wrap Co. backend running"}


@app.get("/api/hello")
def hello():
    return {"message": "Hello from the backend API!"}


@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        from database import db

        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"

            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"

    except ImportError:
        response["database"] = "❌ Database module not found (run enable-database first)"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    import os
    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response


@app.get("/schema")
def get_schema():
    """Expose app schemas for tooling/inspection."""
    return {
        "menuitem": MenuItem.model_json_schema(),
        "review": Review.model_json_schema(),
        "order": Order.model_json_schema(),
    }


# -------- App Endpoints --------

@app.get("/api/menu", response_model=List[MenuItem])
def get_menu():
    """Return signature menu items. Uses DB if configured, else returns curated defaults."""
    defaults: List[MenuItem] = [
        MenuItem(
            name="City Classic Shawarma",
            description="Fire-grilled chicken, garlic sauce, pickles, city herbs.",
            price=11.95,
            category="wraps",
            image="https://images.unsplash.com/photo-1604908554039-955f8a19a34b?q=80&w=1200&auto=format&fit=crop",
            media="https://cdn.coverr.co/videos/coverr-grilling-meat-2869/1080p.mp4",
            rating=4.9,
            ratings_count=542,
        ),
        MenuItem(
            name="Ember Beef Skewers",
            description="Charred edges, tender center, pomegranate glaze.",
            price=14.5,
            category="skewers",
            image="https://images.unsplash.com/photo-1616712134411-6a2dd1d8ef2e?q=80&w=1200&auto=format&fit=crop",
            media="https://cdn.coverr.co/videos/coverr-fire-grilling-4037/1080p.mp4",
            rating=4.8,
            ratings_count=311,
        ),
        MenuItem(
            name="Loaded City Fries",
            description="Garlic drizzle, chili crunch, parsley rain.",
            price=8.75,
            category="fries",
            image="https://images.unsplash.com/photo-1546549039-49d3c2d6d3d2?q=80&w=1200&auto=format&fit=crop",
            media="https://cdn.coverr.co/videos/coverr-close-up-of-french-fries-1550/1080p.mp4",
            rating=4.7,
            ratings_count=228,
        ),
    ]

    try:
        from database import db
        if db is None:
            return defaults
        docs = list(db["menuitem"].find({}, {"_id": 0}))
        if not docs:
            # Seed defaults if collection empty
            db["menuitem"].insert_many([d.model_dump() for d in defaults])
            return defaults
        # Validate via Pydantic
        return [MenuItem(**doc) for doc in docs]
    except Exception:
        return defaults


@app.get("/api/reviews", response_model=List[Review])
def get_reviews():
    defaults: List[Review] = [
        Review(name="Layla", rating=5, quote="The garlic drizzle is unreal. City vibes in a wrap!", platform="Google"),
        Review(name="Marco", rating=5, quote="Beef skewers with that ember glaze… perfection.", platform="Yelp"),
        Review(name="Anaya", rating=4, quote="Loaded fries that belong in a music video.", platform="Google"),
    ]
    try:
        from database import db
        if db is None:
            return defaults
        docs = list(db["review"].find({}, {"_id": 0}))
        if not docs:
            db["review"].insert_many([d.model_dump() for d in defaults])
            return defaults
        return [Review(**doc) for doc in docs]
    except Exception:
        return defaults


class OrderResponse(BaseModel):
    id: Optional[str] = None
    message: str


@app.post("/api/orders", response_model=OrderResponse)
def create_order(order: Order):
    try:
        from database import create_document
        order_id = create_document("order", order)
        return {"id": order_id, "message": "Order received. We'll start the grill!"}
    except Exception:
        # Accept order even without DB for demo purposes
        return {"id": None, "message": "Order received (demo mode). We'll start the grill!"}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
