
from fastapi import APIRouter, HTTPException
from app.schemas.summary import (
    SubjectExplorerRequest, SubjectExplorerResponse
)
from app.services.llm import call_groq_api, call_ollama_api
from app.services.youtube import get_youtube_recommendations

router = APIRouter()

@router.post("/explore", response_model=SubjectExplorerResponse)
async def subject_explorer(request: SubjectExplorerRequest):
    """
    Explore a subject/topic to get comprehensive notes and resources.
    """
    print(f"\n[API] Received /subject-explorer request: {request.subject} - {request.topic}")
    
    # 1. Generate Notes using LLM
    try:
        if request.provider == "groq":
            notes = await call_groq_api(request.subject, request.topic)
        elif request.provider == "ollama":
            notes = await call_ollama_api(request.subject, request.topic)
        else:
            # Default to Groq
            notes = await call_groq_api(request.subject, request.topic)
    except Exception as e:
        print(f"[API] LLM Error: {str(e)}")
        # Fallback notes
        notes = f"# Error Generating Notes\n\nCould not generate notes for {request.topic}. Please try again."

    # 2. Get YouTube Recommendations
    youtube_videos = []
    try:
        youtube_videos = await get_youtube_recommendations(request.subject, request.topic)
    except Exception as e:
        print(f"[API] YouTube Error: {str(e)}")
        
    return SubjectExplorerResponse(
        subject=request.subject,
        topic=request.topic,
        notes=notes,
        provider=request.provider,
        youtube_recommendations=youtube_videos,
        success=True
    )
