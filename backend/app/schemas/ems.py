from pydantic import BaseModel
from typing import Optional, List, Dict

# --- EduMentor Models ---
class EduMentorRequest(BaseModel):
    subject: str
    topic: str
    include_wikipedia: Optional[bool] = False
    use_knowledge_store: Optional[bool] = False
    use_orchestration: Optional[bool] = False
    provider: Optional[str] = "auto"

class EduMentorResponse(BaseModel):
    subject: str
    topic: str
    lesson_content: str
    wikipedia_sources: Optional[List[Dict]] = None
    knowledge_store_used: bool
    orchestration_used: bool
    provider: str
    created_at: str
    success: bool

# --- Financial Agent Models ---
class ExpenseCategory(BaseModel):
    name: str
    amount: float

class FinancialProfileRequest(BaseModel):
    name: str
    monthly_income: float
    monthly_expenses: float
    expense_categories: List[ExpenseCategory]
    financial_goal: str
    financial_type: str  # Conservative, Moderate, Aggressive
    risk_level: str  # Low, Moderate, High

class FinancialAdviceResponse(BaseModel):
    name: str
    monthly_income: float
    monthly_expenses: float
    monthly_savings: float
    expense_breakdown: List[Dict]
    financial_advice: str
    recommendations: List[str]
    goal_analysis: Dict
    provider: str
    created_at: str

# --- Wellness Bot Models ---
class WellnessSupportRequest(BaseModel):
    emotional_wellness_score: int
    financial_wellness_score: int
    current_mood_score: int
    stress_level: int
    concerns: Optional[str] = None

class WellnessSupportResponse(BaseModel):
    emotional_support: str
    motivational_message: str
    life_importance: str
    study_importance: str
    goal_importance: str
    positive_affirmations: List[str]
    recommendations: List[str]
    overall_assessment: str
    provider: str
    created_at: str
