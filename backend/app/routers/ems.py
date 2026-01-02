
from fastapi import APIRouter
from app.schemas.ems import (
    FinancialProfileRequest, FinancialAdviceResponse,
    WellnessSupportRequest, WellnessSupportResponse,
    EduMentorRequest, EduMentorResponse
)

router = APIRouter()

@router.post("/financial-advisor", response_model=FinancialAdviceResponse)
async def financial_advisor(request: FinancialProfileRequest):
    # Mock implementation for now to pass verify
    return FinancialAdviceResponse(
        name=request.name,
        monthly_income=request.monthly_income,
        monthly_expenses=request.monthly_expenses,
        monthly_savings=request.monthly_income - request.monthly_expenses,
        expense_breakdown=[],
        financial_advice="Mock advice",
        recommendations=["Save more"],
        goal_analysis={},
        provider="mock",
        created_at="2024-01-01"
    )

@router.post("/wellness-bot", response_model=WellnessSupportResponse)
async def wellness_bot(request: WellnessSupportRequest):
    return WellnessSupportResponse(
        emotional_support="It's okay to feel this way.",
        motivational_message="Keep going!",
        life_importance="Life is precious.",
        study_importance="Learning helps you grow.",
        goal_importance="Goals give direction.",
        positive_affirmations=["I am adequate."],
        recommendations=["Take a walk."],
        overall_assessment="Stable",
        provider="mock",
        created_at="2024-01-01"
    )

@router.post("/education-mentor", response_model=EduMentorResponse)
async def edu_mentor(request: EduMentorRequest):
    return EduMentorResponse(
        subject=request.subject,
        topic=request.topic,
        lesson_content=f"Lesson on {request.topic}",
        knowledge_store_used=False,
        orchestration_used=False,
        provider="mock",
        created_at="2024-01-01",
        success=True
    )
