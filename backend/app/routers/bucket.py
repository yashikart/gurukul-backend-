from fastapi import APIRouter, Request
import json

router = APIRouter()

@router.post("/bucket/prana/ingest")
async def ingest_prana_packets(request: Request):
    data = await request.json()
    # Process packets here
    return {"status": "success", "received": len(data.get("packets", []))}