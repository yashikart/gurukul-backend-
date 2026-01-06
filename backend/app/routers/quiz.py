from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, List
from app.routers.auth import get_current_user
from app.models.all_models import User
from app.core.config import settings
import uuid
from datetime import datetime

router = APIRouter()

# In-memory storage for quizzes (in production, use database)
quiz_store = {}

class QuizGenerateRequest(BaseModel):
    subject: str
    topic: str
    difficulty: str = "medium"
    provider: str = "auto"
    num_questions: int = 10

class QuizSubmitRequest(BaseModel):
    quiz_id: str
    answers: Dict[str, str]  # {question_id: "A" | "B" | "C" | "D"}

@router.post("/generate")
async def generate_quiz(request: QuizGenerateRequest, current_user: User = Depends(get_current_user)):
    """Generate a quiz using Groq AI"""
    try:
        from groq import Groq
        
        client = Groq(api_key=settings.GROQ_API_KEY)
        
        # Create a prompt for quiz generation
        prompt = f"""Generate exactly {request.num_questions} multiple-choice quiz questions (MCQs) about {request.subject} - {request.topic}.

Requirements:
- Difficulty level: {request.difficulty}
- Each question must have exactly 4 options (A, B, C, D)
- Only one option should be correct
- Questions should test understanding of key concepts
- Format your response as JSON with this structure:
{{
  "questions": [
    {{
      "question": "Question text here?",
      "options": {{"A": "Option A text", "B": "Option B text", "C": "Option C text", "D": "Option D text"}},
      "correct_answer": "A",
      "explanation": "Brief explanation of why this is correct"
    }}
  ]
}}

Generate {request.num_questions} questions now:"""

        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a quiz generator. Return ONLY valid JSON, no markdown formatting."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=3000,
        )
        
        response_text = completion.choices[0].message.content.strip()
        
        # Remove markdown code blocks if present
        if response_text.startswith("```"):
            lines = response_text.split("\n")
            response_text = "\n".join(lines[1:-1]) if len(lines) > 2 else response_text
            response_text = response_text.replace("```json", "").replace("```", "").strip()
        
        import json
        quiz_data = json.loads(response_text)
        
        # Generate quiz ID and process questions
        quiz_id = str(uuid.uuid4())
        processed_questions = []
        
        for i, q in enumerate(quiz_data.get("questions", [])[:request.num_questions], 1):
            question_id = str(uuid.uuid4())
            processed_questions.append({
                "question_id": question_id,
                "question_number": i,
                "question": q["question"],
                "options": q["options"],
                "correct_answer": q["correct_answer"],
                "explanation": q.get("explanation", "")
            })
        
        # Store quiz for later validation
        quiz_store[quiz_id] = {
            "subject": request.subject,
            "topic": request.topic,
            "difficulty": request.difficulty,
            "questions": processed_questions,
            "created_at": datetime.now().isoformat()
        }
        
        # Return quiz without answers
        return {
            "quiz_id": quiz_id,
            "subject": request.subject,
            "topic": request.topic,
            "difficulty": request.difficulty,
            "total_questions": len(processed_questions),
            "questions": [
                {
                    "question_id": q["question_id"],
                    "question_number": q["question_number"],
                    "question": q["question"],
                    "options": q["options"]
                }
                for q in processed_questions
            ]
        }
        
    except Exception as e:
        print(f"Quiz Generation Error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate quiz: {str(e)}")

@router.post("/submit")
async def submit_quiz(request: QuizSubmitRequest, current_user: User = Depends(get_current_user)):
    """Submit quiz answers and get results"""
    if request.quiz_id not in quiz_store:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    quiz_data = quiz_store[request.quiz_id]
    questions = quiz_data["questions"]
    
    correct_count = 0
    wrong_count = 0
    results = []
    
    for q in questions:
        question_id = q["question_id"]
        user_answer = request.answers.get(question_id, "").strip().upper()
        correct_answer = q["correct_answer"]
        
        # Check if answer is correct
        is_correct = (user_answer == correct_answer)
        
        if is_correct:
            correct_count += 1
        else:
            wrong_count += 1
        
        results.append({
            "question_number": q["question_number"],
            "question": q["question"],
            "user_answer": user_answer if user_answer else "Skipped",
            "correct_answer": correct_answer,
            "is_correct": is_correct,
            "explanation": q.get("explanation", "")
        })
    
    score_percentage = round((correct_count / len(questions)) * 100, 2) if questions else 0
    
    return {
        "quiz_id": request.quiz_id,
        "score": correct_count,
        "total_questions": len(questions),
        "correct_answers": correct_count,
        "wrong_answers": wrong_count,
        "score_percentage": score_percentage,
        "results": results
    }
