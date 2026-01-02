
from typing import Dict, List

# Conversation Memory Storage
# Structure: {conversation_id: {"messages": [...], "created_at": "...", "updated_at": "..."}}
conversation_store: Dict[str, Dict] = {}

# RAG Knowledge Store
# Structure: {hash: {"text": "...", "metadata": {...}}}
rag_knowledge_store: Dict[str, Dict] = {}

# Saved Summaries Store
# Structure: {summary_id: {"title": "...", "content": "...", "source": "...", "created_at": "...", "questions": [...]}}
saved_summaries_store: Dict[str, Dict] = {}
# Compatibility for list-based usage in some endpoints
saved_summaries_db = []

# Questions Store
# Structure: {question_id: {"summary_id": "...", "type": "...", "question": "...", "answer": "...", "options": [...], "review_schedule": {...}}}
questions_store: Dict[str, Dict] = {}

# Quiz Store
# Structure: {quiz_id: {"subject": "...", "topic": "...", "questions": [...], "created_at": "...", "provider": "..."}}
quiz_store: Dict[str, Dict] = {}

# Helper stores for specific features
financial_profiles_store: Dict[str, Dict] = {}
wellness_profiles_store: Dict[str, Dict] = {}

# Flashcards DB (List based)
flashcards_db = []
