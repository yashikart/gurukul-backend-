
from fastapi import APIRouter
from app.core.memory_store import conversation_store

router = APIRouter()

@router.get("/health")
async def health():
    return {"status": "ok"}
