# Chatbot API Usage Examples

## Table of Contents
1. [Adding Knowledge to RAG Store](#adding-knowledge)
2. [Chatting with RAG Enabled](#chatting-with-rag)
3. [Complete Workflow Examples](#complete-workflows)
4. [Testing with cURL](#testing-with-curl)
5. [Testing with Python](#testing-with-python)

---

## 1. Adding Knowledge to RAG Store

### Example 1: Add Company Information
```json
POST http://localhost:3000/chat/knowledge

Body (form-data or JSON):
{
  "text": "Gurukul is an AI-powered educational platform that helps students learn through interactive chatbots, document summarization, and personalized teaching. The platform supports subjects like Mathematics, Physics, Chemistry, Computer Science, and more. Students can ask questions, get explanations, and receive YouTube video recommendations.",
  "metadata": {
    "category": "Platform Info",
    "type": "Company Description"
  }
}
```

### Example 2: Add Technical Documentation
```json
POST http://localhost:3000/chat/knowledge

Body:
{
  "text": "FastAPI is a modern Python web framework for building APIs. Key features: Fast performance, automatic API documentation, type hints support, async/await support. Installation: pip install fastapi uvicorn. To run: uvicorn main:app --reload",
  "metadata": {
    "category": "Programming",
    "framework": "FastAPI",
    "language": "Python"
  }
}
```

### Example 3: Add Educational Content
```json
POST http://localhost:3000/chat/knowledge

Body:
{
  "text": "Machine Learning is a subset of artificial intelligence. It allows computers to learn from data without explicit programming. Types: Supervised Learning (labeled data), Unsupervised Learning (unlabeled data), Reinforcement Learning (reward-based). Common algorithms: Linear Regression, Decision Trees, Neural Networks.",
  "metadata": {
    "subject": "Computer Science",
    "topic": "Machine Learning",
    "level": "Beginner"
  }
}
```

### Example 4: Add Historical Facts
```json
POST http://localhost:3000/chat/knowledge

Body:
{
  "text": "Python was created by Guido van Rossum and first released in 1991. It's an interpreted, high-level programming language. Python 3.0 was released in 2008. Key features: Simple syntax, extensive libraries, cross-platform compatibility. Popular uses: Web development, data science, AI/ML, automation.",
  "metadata": {
    "category": "Programming History",
    "language": "Python"
  }
}
```

---

## 2. Chatting with RAG Enabled

### Example 1: Basic Chat (New Conversation)
```json
POST http://localhost:3000/chat

Body:
{
  "message": "What is Gurukul?",
  "provider": "auto",
  "use_rag": true,
  "max_history": 10
}

Response:
{
  "response": "...",
  "conversation_id": "abc-123-def-456",
  "provider": "groq",
  "message_count": 2,
  "timestamp": "2025-12-24T12:00:00",
  "success": true
}
```

### Example 2: Continue Conversation
```json
POST http://localhost:3000/chat

Body:
{
  "message": "Tell me more about its features",
  "conversation_id": "abc-123-def-456",
  "provider": "auto",
  "use_rag": true,
  "max_history": 10
}
```

### Example 3: Chat Without RAG
```json
POST http://localhost:3000/chat

Body:
{
  "message": "What is Python?",
  "conversation_id": "1",
  "provider": "groq",
  "use_rag": false,
  "max_history": 10
}
```

---

## 3. Complete Workflow Examples

### Workflow 1: Educational Q&A System

**Step 1: Add Knowledge**
```json
POST /chat/knowledge
{
  "text": "Photosynthesis is the process by which plants convert light energy into chemical energy. It occurs in chloroplasts and requires carbon dioxide, water, and sunlight. The equation is: 6CO2 + 6H2O + light → C6H12O6 + 6O2. This process produces glucose and oxygen.",
  "metadata": {
    "subject": "Biology",
    "topic": "Photosynthesis",
    "grade": "10"
  }
}
```

**Step 2: Ask Questions**
```json
POST /chat
{
  "message": "Explain photosynthesis",
  "conversation_id": "bio-001",
  "use_rag": true
}
```

**Step 3: Follow-up Questions**
```json
POST /chat
{
  "message": "What are the reactants and products?",
  "conversation_id": "bio-001",
  "use_rag": true
}
```

### Workflow 2: Technical Support Bot

**Step 1: Add Product Documentation**
```json
POST /chat/knowledge
{
  "text": "To reset your password: 1) Go to login page, 2) Click 'Forgot Password', 3) Enter your email, 4) Check email for reset link, 5) Click link and set new password. Password must be at least 8 characters with uppercase, lowercase, and numbers.",
  "metadata": {
    "category": "Support",
    "topic": "Password Reset",
    "product": "Gurukul Platform"
  }
}
```

**Step 2: User Asks for Help**
```json
POST /chat
{
  "message": "How do I reset my password?",
  "conversation_id": "support-123",
  "use_rag": true
}
```

### Workflow 3: Learning Assistant

**Step 1: Add Multiple Topics**
```json
# Add Math knowledge
POST /chat/knowledge
{
  "text": "The quadratic formula is: x = (-b ± √(b²-4ac)) / 2a. It solves equations of form ax² + bx + c = 0. The discriminant (b²-4ac) determines the nature of roots: positive = 2 real roots, zero = 1 real root, negative = 2 complex roots.",
  "metadata": {"subject": "Mathematics", "topic": "Quadratic Formula"}
}

# Add Physics knowledge
POST /chat/knowledge
{
  "text": "Newton's Second Law: F = ma, where F is force, m is mass, and a is acceleration. Force is measured in Newtons (N). This law states that acceleration is directly proportional to force and inversely proportional to mass.",
  "metadata": {"subject": "Physics", "topic": "Newton's Laws"}
}
```

**Step 2: Ask Questions**
```json
POST /chat
{
  "message": "What is the quadratic formula?",
  "conversation_id": "math-001",
  "use_rag": true
}
```

---

## 4. Testing with cURL

### Add Knowledge
```bash
curl -X POST "http://localhost:3000/chat/knowledge" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Gurukul is an AI-powered educational platform for students.",
    "metadata": {"category": "Platform Info"}
  }'
```

### Chat with RAG
```bash
curl -X POST "http://localhost:3000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is Gurukul?",
    "conversation_id": "1",
    "provider": "auto",
    "use_rag": true,
    "max_history": 10
  }'
```

### Get Conversation History
```bash
curl -X GET "http://localhost:3000/chat/history/1" \
  -H "accept: application/json"
```

---

## 5. Testing with Python

```python
import requests

BASE_URL = "http://localhost:3000"

# 1. Add Knowledge
def add_knowledge(text, metadata=None):
    response = requests.post(
        f"{BASE_URL}/chat/knowledge",
        json={"text": text, "metadata": metadata or {}}
    )
    return response.json()

# 2. Chat
def chat(message, conversation_id=None, use_rag=True):
    payload = {
        "message": message,
        "provider": "auto",
        "use_rag": use_rag,
        "max_history": 10
    }
    if conversation_id:
        payload["conversation_id"] = conversation_id
    
    response = requests.post(f"{BASE_URL}/chat", json=payload)
    return response.json()

# 3. Get History
def get_history(conversation_id):
    response = requests.get(f"{BASE_URL}/chat/history/{conversation_id}")
    return response.json()

# Example Usage
if __name__ == "__main__":
    # Add knowledge
    print("Adding knowledge...")
    result = add_knowledge(
        "Gurukul is an AI-powered educational platform.",
        {"category": "Platform Info"}
    )
    print(result)
    
    # Start chat
    print("\nStarting chat...")
    chat_response = chat("What is Gurukul?", conversation_id="1")
    print(f"Response: {chat_response['response']}")
    print(f"Conversation ID: {chat_response['conversation_id']}")
    
    # Continue conversation
    print("\nContinuing chat...")
    chat_response2 = chat(
        "Tell me more about it",
        conversation_id=chat_response['conversation_id']
    )
    print(f"Response: {chat_response2['response']}")
    
    # Get full history
    print("\nGetting history...")
    history = get_history(chat_response['conversation_id'])
    print(f"Total messages: {history['message_count']}")
    for msg in history['messages']:
        print(f"{msg['role']}: {msg['content'][:50]}...")
```

---

## 6. Testing in FastAPI Docs (Swagger UI)

1. **Open Swagger UI**: Go to `http://localhost:3000/docs`

2. **Add Knowledge**:
   - Find `POST /chat/knowledge`
   - Click "Try it out"
   - Enter:
     ```json
     {
       "text": "FastAPI is a modern Python web framework.",
       "metadata": {"category": "Programming"}
     }
     ```
   - Click "Execute"

3. **Chat**:
   - Find `POST /chat`
   - Click "Try it out"
   - Enter:
     ```json
     {
       "message": "What is FastAPI?",
       "conversation_id": "1",
       "provider": "auto",
       "use_rag": true,
       "max_history": 10
     }
     ```
   - Click "Execute"

4. **View History**:
   - Find `GET /chat/history/{conversation_id}`
   - Enter conversation_id: `1`
   - Click "Execute"

---

## 7. Real-World Scenarios

### Scenario 1: Student Learning Assistant

```python
# Add course materials
add_knowledge(
    "The water cycle consists of: Evaporation (water to vapor), Condensation (vapor to clouds), Precipitation (rain/snow), Collection (water returns to oceans).",
    {"subject": "Science", "topic": "Water Cycle", "grade": "5"}
)

# Student asks question
response = chat("Explain the water cycle", conversation_id="student-001", use_rag=True)
print(response['response'])
```

### Scenario 2: Customer Support

```python
# Add FAQ
add_knowledge(
    "Our refund policy: Full refund within 30 days of purchase. Contact support@example.com with order number. Processing takes 5-7 business days.",
    {"category": "Support", "topic": "Refund Policy"}
)

# Customer asks
response = chat("What is your refund policy?", conversation_id="support-001", use_rag=True)
print(response['response'])
```

### Scenario 3: Code Documentation Assistant

```python
# Add API documentation
add_knowledge(
    "FastAPI endpoint example: @app.post('/items') async def create_item(item: Item): return item. Use Pydantic models for validation. Access docs at /docs.",
    {"category": "Documentation", "framework": "FastAPI"}
)

# Developer asks
response = chat("How do I create a POST endpoint in FastAPI?", conversation_id="dev-001", use_rag=True)
print(response['response'])
```

---

## Tips for Best Results

1. **Add knowledge before chatting** - Knowledge must be in the store before it can be retrieved
2. **Use descriptive text** - More detailed knowledge = better context retrieval
3. **Add metadata** - Helps organize and filter knowledge (optional but recommended)
4. **Keep knowledge focused** - One topic per knowledge entry works best
5. **Update regularly** - Keep knowledge base current and accurate
6. **Use specific keywords** - Knowledge with specific terms matches better

---

## Common Issues & Solutions

**Issue**: RAG not finding relevant knowledge
- **Solution**: Make sure `use_rag: true` is set, and knowledge contains keywords from your question

**Issue**: Conversation not found
- **Solution**: Use the `conversation_id` from the previous chat response, or let it auto-generate

**Issue**: Knowledge not being used
- **Solution**: Check that knowledge was added successfully, and that your question contains matching keywords

