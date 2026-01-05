from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import uuid

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    provider: str = "auto"
    use_rag: bool = True

@router.get("/health")
async def health():
    return {"status": "ok"}

@router.post("")  # Mounts at /api/v1/chat
async def chat_endpoint(request: ChatRequest):
    """
    Simple Chat Endpoint
    """
    conversation_id = request.conversation_id or str(uuid.uuid4())
    
    try:
        from groq import Groq
        import os
        
        client = Groq(api_key=settings.GROQ_API_KEY)
        
        completion = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {"role": "system", "content": "You are Gurukul, an AI coding tutor and educational guide."},
                {"role": "user", "content": request.message}
            ],
            temperature=0.7,
            max_tokens=1024,
            top_p=1,
            stream=False,
            stop=None,
        )
        
        response_text = completion.choices[0].message.content
        
    except Exception as e:
        print(f"Groq Error: {e}")
        response_text = f"I'm sorry, I'm having trouble connecting to my brain right now. (Error: {str(e)})"
    
    return {
        "response": response_text,
        "conversation_id": conversation_id
    }

@router.get("/history/{conversation_id}")
async def get_chat_history(conversation_id: str):
    # Mock history
    return {
        "messages": [
            {"role": "user", "content": "Previous message (Mock)"},
            {"role": "assistant", "content": "Previous response (Mock)"}
        ]
    }

@router.delete("/history/{conversation_id}")
async def delete_chat_history(conversation_id: str):
    # Mock delete
    return {"status": "deleted"}

class KnowledgeRequest(BaseModel):
    text: str
    metadata: Optional[dict] = {}

@router.post("/knowledge")
async def add_knowledge(request: KnowledgeRequest):
    # Mock RAG ingestion
    print(f"[RAG] Learning: {request.text[:50]}...")
    return {"status": "learned", "chunks": 1}
