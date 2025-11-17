import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from database import create_document
from schemas import Inquiry

app = FastAPI(title="Thai Massage Budapest API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Thai Massage Budapest Backend Running"}

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
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = db.name if hasattr(db, 'name') else "Unknown"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️ Connected but Error: {str(e)[:80]}"
        else:
            response["database"] = "⚠️ Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:80]}"
    return response

# Public services list for the website
class Service(BaseModel):
    slug: str
    name: str
    duration_min: int
    price_huf: int
    description: str

SERVICES: List[Service] = [
    Service(slug="traditional-thai", name="Traditional Thai Massage", duration_min=60, price_huf=18000,
            description="Full-body treatment combining acupressure, assisted yoga stretches, and rhythmic pressure."),
    Service(slug="aroma-oil", name="Aroma Oil Massage", duration_min=60, price_huf=20000,
            description="Relaxing oil-based massage with aromatic essential oils."),
    Service(slug="foot-reflexology", name="Foot Reflexology", duration_min=45, price_huf=12000,
            description="Targeted pressure-point massage focusing on the feet to relieve tension."),
    Service(slug="back-shoulder", name="Back & Shoulder Massage", duration_min=30, price_huf=9000,
            description="Focused relief for back, neck, and shoulders."),
]

@app.get("/api/services", response_model=List[Service])
def get_services():
    return SERVICES

# Contact form endpoint (persists to DB)
@app.post("/api/inquiry")
def create_inquiry(inquiry: Inquiry):
    try:
        doc_id = create_document("inquiry", inquiry)
        return {"status": "ok", "id": doc_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
