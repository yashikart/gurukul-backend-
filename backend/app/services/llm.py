
import requests
from fastapi import HTTPException
from app.core.config import settings

def create_teaching_prompt(subject: str, topic: str) -> str:
    return f"""You are an expert teacher specializing in {subject}. Your task is to teach the topic "{topic}" to a student.

Please provide comprehensive, clear, and engaging educational notes that include:

1. **Introduction**: A brief overview of the topic and why it's important
2. **Key Concepts**: Break down the main concepts in simple, understandable terms
3. **Detailed Explanation**: Provide a thorough explanation with examples
4. **Real-world Applications**: Show how this topic applies in real life
5. **Summary**: A concise recap of the key points
6. **Practice Questions**: 2-3 questions to help reinforce learning

Write in a friendly, encouraging tone as if you're speaking directly to a student. Use simple language, analogies, and examples to make complex concepts easy to understand. Structure the content with clear headings and bullet points for better readability.

Subject: {subject}
Topic: {topic}

Now, provide the educational notes:"""

async def call_groq_api(subject: str, topic: str) -> str:
    if not settings.GROQ_API_KEY:
        raise HTTPException(status_code=500, detail="Groq API key not configured")
    
    prompt = create_teaching_prompt(subject, topic)
    
    headers = {
        "Authorization": f"Bearer {settings.GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": settings.GROQ_MODEL_NAME,
        "messages": [
            {
                "role": "system",
                "content": "You are an expert teacher who explains concepts clearly and simply."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.7,
        "max_tokens": 2000
    }
    
    try:
        response = requests.post(settings.GROQ_API_ENDPOINT, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Groq API error: {str(e)}")

async def call_ollama_api(subject: str, topic: str) -> str:
    prompt = create_teaching_prompt(subject, topic)
    
    url = f"{settings.OLLAMA_BASE_URL}/api/generate"
    
    payload = {
        "model": settings.OLLAMA_MODEL_PRIMARY,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.7,
            "num_predict": 2000
        }
    }
    
    try:
        response = requests.post(url, json=payload, timeout=60)
        response.raise_for_status()
        data = response.json()
        return data.get("response", "Error generating response from Ollama")
    except requests.exceptions.ConnectionError:
        raise HTTPException(status_code=503, detail="Ollama service not available. Make sure Ollama is running on localhost:11434")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ollama API error: {str(e)}")
