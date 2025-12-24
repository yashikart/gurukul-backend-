"""
Example script to test the Chatbot API
Run this after starting your FastAPI server
"""

import requests
import json
from typing import Optional, Dict

BASE_URL = "http://localhost:3000"

def add_knowledge(text: str, metadata: Optional[Dict] = None) -> Dict:
    """Add knowledge to RAG store"""
    response = requests.post(
        f"{BASE_URL}/chat/knowledge",
        json={"text": text, "metadata": metadata or {}}
    )
    response.raise_for_status()
    return response.json()

def chat(message: str, conversation_id: Optional[str] = None, 
         provider: str = "auto", use_rag: bool = True, 
         max_history: int = 10) -> Dict:
    """Send a chat message"""
    payload = {
        "message": message,
        "provider": provider,
        "use_rag": use_rag,
        "max_history": max_history
    }
    if conversation_id:
        payload["conversation_id"] = conversation_id
    
    response = requests.post(f"{BASE_URL}/chat", json=payload)
    response.raise_for_status()
    return response.json()

def get_history(conversation_id: str) -> Dict:
    """Get conversation history"""
    response = requests.get(f"{BASE_URL}/chat/history/{conversation_id}")
    response.raise_for_status()
    return response.json()

def delete_conversation(conversation_id: str) -> Dict:
    """Delete a conversation"""
    response = requests.delete(f"{BASE_URL}/chat/history/{conversation_id}")
    response.raise_for_status()
    return response.json()

# ==================== EXAMPLE 1: Educational Assistant ====================
def example_1_educational_assistant():
    print("\n" + "="*60)
    print("EXAMPLE 1: Educational Assistant")
    print("="*60)
    
    # Step 1: Add educational knowledge
    print("\n[STEP 1] Adding knowledge about Machine Learning...")
    result = add_knowledge(
        "Machine Learning is a subset of artificial intelligence that enables computers to learn from data without explicit programming. Types include: Supervised Learning (uses labeled data), Unsupervised Learning (finds patterns in unlabeled data), and Reinforcement Learning (learns through rewards). Popular algorithms: Linear Regression, Decision Trees, Neural Networks, and Support Vector Machines.",
        {"subject": "Computer Science", "topic": "Machine Learning", "level": "Beginner"}
    )
    print(f"[SUCCESS] {result['message']}")
    
    # Step 2: Start a conversation
    print("\n[STEP 2] Asking: 'What is Machine Learning?'")
    response = chat("What is Machine Learning?", conversation_id="edu-001", use_rag=True)
    print(f"[BOT] Response: {response['response'][:200]}...")
    print(f"[INFO] Conversation ID: {response['conversation_id']}")
    print(f"[INFO] Message Count: {response['message_count']}")
    
    # Step 3: Follow-up question
    print("\n[STEP 3] Asking: 'What are the types of Machine Learning?'")
    response2 = chat(
        "What are the different types of Machine Learning?",
        conversation_id=response['conversation_id'],
        use_rag=True
    )
    print(f"[BOT] Response: {response2['response'][:200]}...")
    
    # Step 4: View full history
    print("\n[STEP 4] Getting conversation history...")
    history = get_history(response['conversation_id'])
    print(f"Total messages: {history['message_count']}")
    for i, msg in enumerate(history['messages'], 1):
        print(f"  {i}. [{msg['role'].upper()}]: {msg['content'][:80]}...")

# ==================== EXAMPLE 2: Platform Information Bot ====================
def example_2_platform_info():
    print("\n" + "="*60)
    print("EXAMPLE 2: Platform Information Bot")
    print("="*60)
    
    # Add platform knowledge
    print("\n[STEP 1] Adding Gurukul platform information...")
    add_knowledge(
        "Gurukul is an AI-powered educational platform that helps students learn through interactive chatbots, document summarization (PDF, DOCX), and personalized teaching. Features: Subject Explorer for detailed explanations, YouTube video recommendations, multi-page PDF summarization, and intelligent chat with conversation memory. The platform supports subjects like Mathematics, Physics, Chemistry, Computer Science, and more.",
        {"category": "Platform Info", "product": "Gurukul"}
    )
    print("[SUCCESS] Knowledge added")
    
    # Ask about platform
    print("\n[STEP 2] Asking: 'What is Gurukul?'")
    response = chat("What is Gurukul and what features does it have?", 
                   conversation_id="platform-001", use_rag=True)
    print(f"[BOT] Response:\n{response['response']}\n")

# ==================== EXAMPLE 3: Technical Support ====================
def example_3_technical_support():
    print("\n" + "="*60)
    print("EXAMPLE 3: Technical Support Bot")
    print("="*60)
    
    # Add support knowledge
    print("\n[STEP 1] Adding support documentation...")
    add_knowledge(
        "Password Reset Instructions: 1) Go to login page, 2) Click 'Forgot Password' link, 3) Enter your registered email address, 4) Check your email inbox for reset link, 5) Click the reset link (valid for 24 hours), 6) Enter new password (minimum 8 characters, must include uppercase, lowercase, and numbers), 7) Confirm new password. If you don't receive email, check spam folder or contact support@example.com",
        {"category": "Support", "topic": "Password Reset", "product": "Gurukul"}
    )
    print("[SUCCESS] Knowledge added")
    
    # User asks for help
    print("\n[STEP 2] User: 'How do I reset my password?'")
    response = chat("How do I reset my password?", 
                   conversation_id="support-001", use_rag=True)
    print(f"🤖 Support Bot:\n{response['response']}\n")

# ==================== EXAMPLE 4: Programming Assistant ====================
def example_4_programming_assistant():
    print("\n" + "="*60)
    print("EXAMPLE 4: Programming Assistant")
    print("="*60)
    
    # Add programming knowledge
    print("\n[STEP 1] Adding FastAPI documentation...")
    add_knowledge(
        "FastAPI is a modern Python web framework for building APIs. Key features: High performance (comparable to Node.js), automatic interactive API documentation (Swagger UI), type hints support, async/await support, data validation with Pydantic. Installation: pip install fastapi uvicorn. To create an endpoint: @app.post('/items') async def create_item(item: Item): return item. Access docs at http://localhost:8000/docs",
        {"category": "Programming", "framework": "FastAPI", "language": "Python"}
    )
    print("[SUCCESS] Knowledge added")
    
    # Ask programming question
    print("\n[STEP 2] Developer: 'How do I create a POST endpoint in FastAPI?'")
    response = chat("How do I create a POST endpoint in FastAPI?", 
                   conversation_id="dev-001", use_rag=True)
    print(f"🤖 Programming Assistant:\n{response['response']}\n")

# ==================== EXAMPLE 5: Chat Without RAG ====================
def example_5_without_rag():
    print("\n" + "="*60)
    print("EXAMPLE 5: Chat Without RAG (General AI)")
    print("="*60)
    
    print("\n[TEST] Asking: 'What is Python?' (without RAG)")
    response = chat("What is Python?", 
                   conversation_id="general-001", use_rag=False)
    print(f"[BOT] Response:\n{response['response'][:300]}...\n")
    
    print("[TEST] Same question with RAG enabled:")
    response2 = chat("What is Python?", 
                    conversation_id="general-002", use_rag=True)
    print(f"[BOT] Response:\n{response2['response'][:300]}...\n")
    print("[NOTE] RAG response may include knowledge from your knowledge base if relevant.")

# ==================== MAIN ====================
if __name__ == "__main__":
    import sys
    import io
    # Fix encoding for Windows
    if sys.platform == "win32":
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    print("\n[STARTING] Chatbot API Examples")
    print("="*60)
    print("Make sure your FastAPI server is running on http://localhost:3000")
    print("="*60)
    
    try:
        # Test connection
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("[SUCCESS] Server is running!")
        else:
            print("[ERROR] Server is not responding correctly")
            exit(1)
    except requests.exceptions.ConnectionError:
        print("[ERROR] Cannot connect to server. Make sure it's running on http://localhost:3000")
        exit(1)
    
    # Run examples
    try:
        example_1_educational_assistant()
        example_2_platform_info()
        example_3_technical_support()
        example_4_programming_assistant()
        example_5_without_rag()
        
        print("\n" + "="*60)
        print("[SUCCESS] All examples completed successfully!")
        print("="*60)
        
    except Exception as e:
        print(f"\n[ERROR] {str(e)}")
        import traceback
        traceback.print_exc()

