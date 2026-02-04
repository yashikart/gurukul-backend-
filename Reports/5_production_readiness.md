# Production Readiness

## Status: CONDITIONAL ✅

Ready if:
- ✅ Summarizer stays disabled
- ✅ DATABASE_URL remains valid
- ✅ No new heavy dependencies added

## Working Features

| Feature      | Endpoint                         | Status |
|--------------|----------------------------------|--------|
| Registration | POST /api/v1/auth/register       | ✅ |
| Login        | POST /api/v1/auth/login          | ✅ |
| Chat         | POST /api/v1/chat/send           | ✅ |
| Quiz         | POST /api/v1/quiz/generate       | ✅ |
| TTS          | POST /api/v1/tts/speak           | ✅ |
| PRANA Bucket | POST /api/v1/bucket/prana/ingest | ✅ |

## Disabled Features

| Feature    | Reason          | Impact                |
|------------|-----------------|-----------------------|
| Summarizer | Memory (300MB+) | Cannot summarize docs |
| LED Model  | Memory (300MB+) | Part of summarizer    |

## Memory Budget

| Component         | MB      |
|-------------------|---------|
| FastAPI + Uvicorn | 50      |
| SQLAlchemy        | 30      |
| Routers           | 100     |
| ChromaDB          | 50      |
| gTTS + Groq       | 30      |
| **Total**         | **260** |
| **Limit**         | **512** |
| **Headroom**      | **252** |

## PRANA Impact

| If PRANA fails | Impact |
|----------------|--------|
| Login          | None   |
| Chat           | None   |
| Quiz           | None   |
| TTS            | None   |
| Karma data     | Delayed (acceptable) |

## Blockers for Full Production

1. No `/health` endpoint (TODO)
2. No automated alerts
3. No rollback automation

