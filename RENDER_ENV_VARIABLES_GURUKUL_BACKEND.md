# Gurukul Backend - Environment Variables for Render

Copy-paste these environment variables into Render Dashboard for `gurukul-backend` service.

## Step 1: Required Core Variables (Copy-paste as-is)

```
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080
ENVIRONMENT=production
PYTHON_VERSION=3.11.0
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=10080
```

## Step 2: API Keys (Copy from your .env file)

```
GROQ_API_KEY=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
GROQ_API_ENDPOINT=https://api.groq.com/openai/v1/chat/completions
GROQ_MODEL_NAME=llama-3.3-70b-versatile
OPENAI_API_KEY=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
GEMINI_API_KEY=AIzaSyDSunIIg6InYPa4yaYhrXKGXO2HTWhi_wc
GEMINI_API_KEY_BACKUP=AIzaSyAycjWjrpcYlYsvgSOjEZBfmCFf1WRODn4
LLAMA_API_KEY=b0a42236-938c-4ab5-afe4-e9f46e15a4d2
AGENTOPS_API_KEY=4be58a32-e415-4142-82b7-834ae6b95422
ALPHA_VANTAGE_API_KEY=CNDDBU70Y449RJ61
YOUTUBE_API_KEY=AIzaSyCJhsvlm7aAhnOBM6oBl1d90s9l67ksfbc
```

## Step 3: Configuration Variables (Copy-paste as-is)

```
HOST=0.0.0.0
PORT=3000
RELOAD=True
API_TITLE=Gurukul Backend API
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL_PRIMARY=llama2
OLLAMA_MODEL_ALTERNATIVES=mistral,codellama,neural-chat
OLLAMA_TEMPERATURE=0.7
OLLAMA_MAX_TOKENS=500
OLLAMA_TOP_P=0.9
LOCAL_LLAMA_API_URL=http://localhost:8080/v1/chat/completions
LOCAL_OLLAMA_API_URL=http://localhost:11434/api/generate
DEFAULT_LOCAL_MODEL=llama3.1
FALLBACK_LOCAL_MODEL=llama2
LOCAL_MODEL_TEMPERATURE=0.7
LOCAL_MODEL_MAX_TOKENS=2048
LOCAL_MODEL_TOP_P=1.0
VECTOR_STORE_BACKEND=chromadb
VECTOR_STORE_PATH=./knowledge_store
VECTOR_STORE_COLLECTION=knowledge_base
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

## Step 4: Database & Services (Set manually with your actual values)

```
DATABASE_URL=postgresql://user:password@host:port/dbname
SECRET_KEY=your-secret-key-here-change-in-production
JWT_SECRET_KEY=your-secret-key-here-change-in-production
MONGODB_URI=mongodb+srv://user:password@cluster.mongodb.net/dbname
MONGO_URI=mongodb+srv://user:password@cluster.mongodb.net/dbname
DB_NAME=karma-chain
REDIS_URL=redis://default:password@host:port
```

## Step 5: Frontend URLs (Update after deploying static sites)

```
FRONTEND_URL=https://gurukul-frontend.onrender.com
EMS_FRONTEND_URL=https://ems-frontend.onrender.com
EMS_API_BASE_URL=https://ems-backend.onrender.com
```

## Step 6: EMS Integration (Copy from your .env)

```
EMS_ADMIN_EMAIL=vasco20090@gmail.com
EMS_ADMIN_PASSWORD=Somsid@2014
EMS_AUTO_CREATE_STUDENTS=true
```

## Step 7: Optional - Ngrok URLs (if using)

```
NGROK_URL=https://fb0cb82eb590.ngrok-free.app
UNIGURU_NGROK_ENDPOINT=
UNIGURU_API_BASE_URL=
ANIMATEDIFF_NGROK_ENDPOINT=https://c7d82cf2656d.ngrok-free.app
```

---

## Complete List (All in one place for easy copy)

**In Render Dashboard, add each variable one by one:**

1. **ALGORITHM** = `HS256`
2. **ACCESS_TOKEN_EXPIRE_MINUTES** = `10080`
3. **ENVIRONMENT** = `production`
4. **PYTHON_VERSION** = `3.11.0`
5. **JWT_ALGORITHM** = `HS256`
6. **JWT_ACCESS_TOKEN_EXPIRE_MINUTES** = `10080`
7. **GROQ_API_KEY** = `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`
8. **GROQ_API_ENDPOINT** = `https://api.groq.com/openai/v1/chat/completions`
9. **GROQ_MODEL_NAME** = `llama-3.3-70b-versatile`
10. **OPENAI_API_KEY** = `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`
11. **GEMINI_API_KEY** = `AIzaSyDSunIIg6InYPa4yaYhrXKGXO2HTWhi_wc`
12. **GEMINI_API_KEY_BACKUP** = `AIzaSyAycjWjrpcYlYsvgSOjEZBfmCFf1WRODn4`
13. **LLAMA_API_KEY** = `b0a42236-938c-4ab5-afe4-e9f46e15a4d2`
14. **AGENTOPS_API_KEY** = `4be58a32-e415-4142-82b7-834ae6b95422`
15. **ALPHA_VANTAGE_API_KEY** = `CNDDBU70Y449RJ61`
16. **YOUTUBE_API_KEY** = `AIzaSyCJhsvlm7aAhnOBM6oBl1d90s9l67ksfbc`
17. **HOST** = `0.0.0.0`
18. **PORT** = `3000`
19. **RELOAD** = `True`
20. **API_TITLE** = `Gurukul Backend API`
21. **OLLAMA_BASE_URL** = `http://localhost:11434`
22. **OLLAMA_MODEL_PRIMARY** = `llama2`
23. **OLLAMA_MODEL_ALTERNATIVES** = `mistral,codellama,neural-chat`
24. **OLLAMA_TEMPERATURE** = `0.7`
25. **OLLAMA_MAX_TOKENS** = `500`
26. **OLLAMA_TOP_P** = `0.9`
27. **LOCAL_LLAMA_API_URL** = `http://localhost:8080/v1/chat/completions`
28. **LOCAL_OLLAMA_API_URL** = `http://localhost:11434/api/generate`
29. **DEFAULT_LOCAL_MODEL** = `llama3.1`
30. **FALLBACK_LOCAL_MODEL** = `llama2`
31. **LOCAL_MODEL_TEMPERATURE** = `0.7`
32. **LOCAL_MODEL_MAX_TOKENS** = `2048`
33. **LOCAL_MODEL_TOP_P** = `1.0`
34. **VECTOR_STORE_BACKEND** = `chromadb`
35. **VECTOR_STORE_PATH** = `./knowledge_store`
36. **VECTOR_STORE_COLLECTION** = `knowledge_base`
37. **EMBEDDING_MODEL** = `sentence-transformers/all-MiniLM-L6-v2`
38. **EMS_ADMIN_EMAIL** = `vasco20090@gmail.com`
39. **EMS_ADMIN_PASSWORD** = `Somsid@2014`
40. **EMS_AUTO_CREATE_STUDENTS** = `true`
41. **NGROK_URL** = `https://fb0cb82eb590.ngrok-free.app`
42. **UNIGURU_NGROK_ENDPOINT** = `` (empty)
43. **UNIGURU_API_BASE_URL** = `` (empty)
44. **ANIMATEDIFF_NGROK_ENDPOINT** = `https://c7d82cf2656d.ngrok-free.app`

**Then add these with your actual values:**
45. **DATABASE_URL** = `postgresql://user:password@host:port/dbname` (from Render PostgreSQL)
46. **SECRET_KEY** = `generate-or-set-your-own-secret-key`
47. **JWT_SECRET_KEY** = `generate-or-set-your-own-secret-key`
48. **MONGODB_URI** = `mongodb+srv://user:password@cluster.mongodb.net/dbname` (from MongoDB Atlas)
49. **MONGO_URI** = `mongodb+srv://user:password@cluster.mongodb.net/dbname` (same as above)
50. **DB_NAME** = `karma-chain`
51. **REDIS_URL** = `redis://default:password@host:port` (optional, if using Redis)
52. **FRONTEND_URL** = `https://gurukul-frontend.onrender.com` (after creating static site)
53. **EMS_FRONTEND_URL** = `https://ems-frontend.onrender.com` (after creating static site)
54. **EMS_API_BASE_URL** = `https://ems-backend.onrender.com` (after deploying EMS backend)

---

## Quick Instructions

1. Go to Render Dashboard → Your `gurukul-backend` service
2. Click "Environment" tab
3. For each variable above:
   - Click "Add Environment Variable"
   - Paste the KEY (left side)
   - Paste the VALUE (right side)
4. For variables marked with placeholders, replace with your actual values
5. Save and redeploy

