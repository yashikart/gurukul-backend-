from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict
import uuid
import logging
from collections import defaultdict

from app.core.config import settings
from app.services.knowledge_base_helper import get_knowledge_base_context, enhance_prompt_with_context

logger = logging.getLogger(__name__)
router = APIRouter()

# In-memory chat history storage (per session - resets on server restart)
# For production, this should be stored in PostgreSQL
_chat_history: Dict[str, List[dict]] = defaultdict(list)

# Initialize vector store service (lazy loading) - kept for backward compatibility
_vector_store_instance = None

def get_vector_store():
    """Get or create vector store instance (backward compatibility)"""
    from app.services.knowledge_base_helper import get_vector_store as _get_vector_store
    return _get_vector_store()

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
    Chat Endpoint with RAG (Retrieval Augmented Generation) support
    Uses Knowledge Base + Groq with automatic fallback to Groq-only if KB fails
    """
    conversation_id = request.conversation_id or str(uuid.uuid4())
    
    # Step 1: Try to get context from knowledge base
    kb_result = get_knowledge_base_context(
        query=request.message,
        top_k=3,
        use_knowledge_base=request.use_rag
    )
    
    # Step 2: Build system message with or without context
    base_system_message = "You are Gurukul, an AI coding tutor and educational guide."
    
    if kb_result["knowledge_base_used"] and kb_result["context"]:
        # Best case: Use both Knowledge Base + Groq
        system_message = enhance_prompt_with_context(
            base_prompt=base_system_message,
            query=request.message,
            context=kb_result["context"],
            include_context_instruction=True
        )
        user_message = request.message
        logger.info(f"Using Knowledge Base + Groq: {len(kb_result['context'])} chars context")
    else:
        # Fallback: Use Groq only (KB failed or disabled)
        system_message = base_system_message
        user_message = request.message
        if kb_result["error"]:
            logger.warning(f"Knowledge Base unavailable, using Groq only: {kb_result['error']}")
        else:
            logger.info("Knowledge Base disabled or empty, using Groq only")
    
    # Step 3: Always call Groq (with or without context)
    try:
        from groq import Groq
        
        client = Groq(api_key=settings.GROQ_API_KEY)
        
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ],
            temperature=0.7,
            max_tokens=1024,
            top_p=1,
            stream=False,
            stop=None,
        )
        
        response_text = completion.choices[0].message.content
        groq_used = True
        groq_error = None
        
    except Exception as e:
        logger.error(f"Groq Error: {e}")
        response_text = f"I'm sorry, I'm having trouble connecting to my brain right now. (Error: {str(e)})"
        groq_used = False
        groq_error = str(e)
    
    # Save messages to chat history
    _chat_history[conversation_id].append({"role": "user", "content": request.message})
    _chat_history[conversation_id].append({"role": "assistant", "content": response_text})
    
    return {
        "response": response_text,
        "conversation_id": conversation_id,
        "knowledge_base_used": kb_result["knowledge_base_used"],
        "groq_used": groq_used,
        "context_length": len(kb_result["context"]) if kb_result["context"] else 0,
        "fallback_used": not kb_result["knowledge_base_used"] and request.use_rag,
        "kb_error": kb_result["error"] if not kb_result["knowledge_base_used"] else None,
        "groq_error": groq_error
    }

@router.get("/history/{conversation_id}")
async def get_chat_history(conversation_id: str):
    """Return actual chat history for conversation"""
    messages = _chat_history.get(conversation_id, [])
    
    if not messages:
        # Return empty list if no history found (don't return mock data)
        return {"messages": [], "found": False}
    
    return {"messages": messages, "found": True}

@router.delete("/history/{conversation_id}")
async def delete_chat_history(conversation_id: str):
    """Delete chat history for conversation"""
    if conversation_id in _chat_history:
        del _chat_history[conversation_id]
        return {"status": "deleted", "found": True}
    return {"status": "deleted", "found": False}

class KnowledgeRequest(BaseModel):
    text: str
    metadata: Optional[dict] = {}

@router.post("/knowledge")
async def add_knowledge(request: KnowledgeRequest):
    """
    Add knowledge to vector store for RAG
    Replaces the old in-memory dictionary storage
    """
    if not request.text or len(request.text.strip()) < 10:
        raise HTTPException(status_code=400, detail="Text must be at least 10 characters")
    
    try:
        vector_store = get_vector_store()
        if not vector_store:
            raise HTTPException(
                status_code=503, 
                detail="Vector store not available. Check backend configuration."
            )
        
        result = vector_store.add_knowledge(
            text=request.text,
            metadata=request.metadata or {}
        )
        
        logger.info(f"Knowledge added: {result['chunks_added']} chunks")
        
        return {
            "status": "learned",
            "chunks_added": result["chunks_added"],
            "total_chunks": result["total_chunks"],
            "backend": settings.VECTOR_STORE_BACKEND
        }
    
    except Exception as e:
        logger.error(f"Failed to add knowledge: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to add knowledge: {str(e)}")
