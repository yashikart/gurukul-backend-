
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.routers.auth import get_current_user
from app.models.all_models import User, Summary as DBSummary
from typing import Optional
from app.schemas.summary import (
    PDFSummarizerResponse, DOCSummarizerResponse,
    SummarizerRequest, SummarizerResponse
)
from app.core.config import settings

# Import specific summarizers
try:
    from app.services.doc_summarizer import DOCSummarizer
    DOC_SUMMARIZER_SUPPORT = True
except ImportError:
    DOC_SUMMARIZER_SUPPORT = False

from app.services.pdf_summarizer import PDFSummarizer, extract_pages_from_pdf

router = APIRouter()

@router.post("/summarize-pdf", response_model=PDFSummarizerResponse)
async def summarize_pdf(
    file: UploadFile = File(...),
    summary_type: str = Form("detailed"),
    improve_grammar: bool = Form(False),
    save_summary: bool = Form(False),
    summary_title: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Summarize an uploaded PDF file using local transformer model.
    """
    print(f"\n[API] Received /summarize-pdf request for file: {file.filename}")

    if not settings.PDF_SUMMARIZER_SUPPORT and False: # Force True for now as config has False by default but user had it working?
         # logic in original main.py seemed to check import. 
         pass
    
    # 1. Extract Text
    try:
        pages = await extract_pages_from_pdf(file)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to extract text from PDF: {str(e)}")
        
    if not pages:
        raise HTTPException(status_code=400, detail="No text could be extracted from this PDF.")

    # 2. Initialize Summarizer
    try:
        # We instantiate per request or globally? Original main.py instantiated it inside?
        # "summarizer = PDFSummarizer()"
        summarizer = PDFSummarizer()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initialize summarizer model: {str(e)}")

    # 3. Generate Summary
    try:
        result = summarizer.summarize_all_pages(pages, summary_type=summary_type, improve_grammar=improve_grammar)
        
        # Add success flag if not present
        if "success" not in result:
            result["success"] = True
            
        if save_summary:
            print(f"[Summarizer] Saving summary to DB for user {current_user.email}")
            new_summary = DBSummary(
                user_id=current_user.id,
                title=summary_title or f"PDF Summary - {file.filename}",
                content=result.get("overall_summary", ""), # Assuming this is the field
                source=file.filename,
                source_type="pdf"
            )
            db.add(new_summary)
            db.commit()
            
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Summarization failed: {str(e)}")
