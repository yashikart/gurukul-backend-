from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Any
from app.services.llm import call_groq_api, call_ollama_api
from app.core.config import settings

router = APIRouter()

# --- Schemas ---

class EduMentorRequest(BaseModel):
    subject: str
    topic: str
    include_wikipedia: bool = False
    use_knowledge_store: bool = False
    use_orchestration: bool = False

class ExpenseCategory(BaseModel):
    name: str
    amount: float

class FinancialRequest(BaseModel):
    name: str
    monthly_income: float
    monthly_expenses: float
    expense_categories: List[ExpenseCategory]
    financial_goal: str
    financial_type: str
    risk_level: str

class WellnessRequest(BaseModel):
    emotional_wellness_score: int
    financial_wellness_score: int
    current_mood_score: int
    stress_level: int
    concerns: Optional[str] = None

# --- Endpoints ---

@router.post("/edumentor/generate")
async def generate_lesson(request: EduMentorRequest):
    """Generate a lesson using the available LLM"""
    try:
        # Prefer Groq if available, else Ollama
        if settings.GROQ_API_KEY:
            content = await call_groq_api(request.subject, request.topic)
        else:
            content = await call_ollama_api(request.subject, request.topic)
            
        return {"lesson_content": content}
    except Exception as e:
        # Fallback Mock for Demo stability if LLM fails
        print(f"LLM Generation Failed: {e}")
        return {
            "lesson_content": f"# {request.topic}\n\n## Introduction\nWelcome to this lesson on {request.topic} in {request.subject}. (Generated via Fallback Mode due to LLM error: {str(e)})"
        }

@router.post("/financial/advice")
async def generate_financial_advice(request: FinancialRequest):
    """Generate financial advice based on profile"""
    # Construct Prompt
    prompt = f"""
    Act as a financial advisor. Analyze the following profile:
    Name: {request.name}
    Monthly Income: {request.monthly_income}
    Total Expenses: {request.monthly_expenses}
    Goal: {request.financial_goal}
    Risk Profile: {request.risk_level}
    
    Expense Breakdown:
    {', '.join([f"{e.name}: {e.amount}" for e in request.expense_categories])}
    
    Provide:
    1. Financial Health Check
    2. Savings Potential analysis
    3. Actionable steps to reach the goal
    """
    
    try:
        # Use Groq/Ollama logic (Simplified reuse of LLM service or direct call)
        # For speed in this fix, we'll reuse the logic inline or call a generic helper if it existed.
        # Since call_groq_api is specific to "Teaching", we should make a generic one.
        # But for now, let's use a simple mock if we can't easily extend llm.py without viewing it again.
        # wait, I can just use the same call_groq_api pattern but I need to change the prompt.
        # The llm.py file harcoded the prompt in `create_teaching_prompt`. 
        # I should probably update llm.py to be more generic, but to avoid breaking changes, 
        # I will implement a basic generic caller here or just mock it for "Simulator" purposes if standard LLM is not flexible.
        
        # ACTUALLY: Best approach is to return a structured mock response that LOOKS like LLM for reliability,
        # OR try to use the LLM if I can.
        # Let's add a generic `generate_text` to llm.py? No, I can't edit llm.py easily in this turn without reading it again.
        # I'll implement a local helper here.
        pass
    except Exception:
        pass

    # Deterministic calculation used in both primary and fallback paths
    monthly_savings = request.monthly_income - request.monthly_expenses
    
    # Real LLM Call
    try:
        from app.services.llm import generate_text
        
        system_prompt = "Act as a professional financial advisor. Provide a clear, strategic financial plan based on the user's data."
        
        generated_advice = await generate_text(system_prompt, prompt, temperature=0.6)

        # Echo back core numeric fields so frontend can display Income / Expenses / Savings
        return {
            "financial_advice": generated_advice,
            "monthly_savings": monthly_savings,
            "monthly_income": request.monthly_income,
            "monthly_expenses": request.monthly_expenses,
        }
    except Exception as e:
        print(f"Financial LLM Failed: {e}")
        # Fallback: still return all numeric fields for UI consistency
        return {
             "financial_advice": f"Could not generate AI advice ({str(e)}). \n\nCalculated Savings: {monthly_savings}",
             "monthly_savings": monthly_savings,
             "monthly_income": request.monthly_income,
             "monthly_expenses": request.monthly_expenses,
        }

@router.post("/wellness/support")
async def generate_wellness_support(request: WellnessRequest):
    """Generate wellness advice"""
    assessment = f"""
    # Wellness Assessment
    
    - **Emotional Score**: {request.emotional_wellness_score}/10
    - **Stress Level**: {request.stress_level}/10
    
    ## Personalized Tips
    1. **Mindfulness**: Practice daily breathing exercises.
    2. **Activity**: Take a short walk when stress feels high ({request.stress_level}/10).
    3. **Reflection**: Journal your thoughts regarding "{request.concerns or 'your daily life'}".
    """
    
    # Real LLM Call
    try:
        from app.services.llm import generate_text
        
        system_prompt = "Act as an empathetic and knowledgeable wellness coach. Analyze the user's wellness assessment and provide personalized, actionable advice."
        user_prompt = assessment
        
        generated_assessment = await generate_text(system_prompt, user_prompt, temperature=0.7)
        
        return {
            "overall_assessment": generated_assessment
        }
    except Exception as e:
        print(f"Wellness LLM Failed: {e}")
        # Fallback
        return {
            "overall_assessment": assessment + f"\n\n*(AI Generation failed: {str(e)}. Showing raw data.)*"
        }
